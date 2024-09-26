# How to use MPT circuit

The client that wants to use the MPT circuit to ensure the modifications in the MPT have been done correctly,
needs first to obtain all the modifications (`trie_modifications`) in a block.

The modifications are then transformed into the objects that MPT witness generator understands (see 
mpt-witness-generator/rustlib/src/lib.rs):
```
pub struct TrieModification {
    pub typ: ProofType,
    pub key: H256,
    pub value: U256,
    pub address: Address,
    pub nonce: U64,
    pub balance: U256,
    pub code_hash: H256,
}
```

Having the trie modifications, the MPT witness generator can be queried to provide the MPT nodes - for each
modification `getProof` is called two times to obtain a proof before and after the modification. Each proof contains
a list of nodes - `get_witness` (see mpt-witness-generator/rustlib/src/lib.rs) returns the nodes for all proofs:
```
let nodes = mpt_witness_generator::get_witness(
    block_no.as_u64() - 1,
    &trie_modifications,
    provider,
);
```

The nodes returned by `get_witness` are then to be checked by the MPT circuit:
```
let mpt_circuit = zkevm_circuits::mpt_circuit::MPTCircuit::<Fr> {
    nodes: nodes,
    keccak_data: keccak_data.clone(),
    degree,
    max_nodes,
    disable_preimage_check,
    _marker: std::marker::PhantomData,
};
```

`MPTConfig` is assigned the values:
```
mpt_config.assign(&mut layouter, &mpt_circuit.nodes, &challenges)?;
mpt_config.load_fixed_table(&mut layouter)?;
mpt_config.load_mult_table(&mut layouter, &challenges, mpt_circuit.max_nodes)?;

mpt_config.keccak_table.dev_load(
    &mut layouter,
    &self.mpt_circuit.keccak_data,
    &challenges,
)?;
```

The assignment is checked in the MPT circuit.
The final assignment step is to assign the MPT table (`mpt_table`) with `trie_modifications`. Below,
`stm` is one `TrieModification`:
```
[
    (mpt_table.proof_type, stm.typ),
    (mpt_table.address, stm.address),
    (mpt_table.new_value.lo(), stm.value.lo()),
    (mpt_table.new_value.hi(), stm.value.hi()),
    (mpt_table.storage_key.lo(), stm.key.lo()),
    (mpt_table.storage_key.hi(), stm.key.hi()),
    (mpt_table.old_root.lo(), stm.old_root.lo()),
    (mpt_table.old_root.hi(), stm.old_root.hi()),
    (mpt_table.new_root.lo(), stm.new_root.lo()),
    (mpt_table.new_root.hi(), stm.new_root.hi())
]
.map(|(col, value)|
        region.assign_advice(
            || "",
            col,
            offset,
            || Value::known(value),
        ).unwrap()
    );
```

In the client circuit, we need to ensure that the roots are chained - the previous `old_root` is
the same as the current `new_root` in `mpt_table`.

Finally, we can execute the lookups into `mpt_config.mpt_table`:
```
meta.lookup_any("mpt_updates lookups into mpt_table", |meta| {
    let is_not_padding = 1.expr() - is_padding.expr();

    let lookups = vec![
        (
            meta.query_advice(mpt_table.proof_type, Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.proof_type, Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.address, Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.address, Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.new_value.lo(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.new_value.lo(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.new_value.hi(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.new_value.hi(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.storage_key.lo(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.storage_key.lo(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.storage_key.hi(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.storage_key.hi(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.old_root.lo(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.new_root.lo(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.old_root.hi(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.new_root.hi(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.new_root.lo(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.old_root.lo(), Rotation::cur()),
        ),
        (
            meta.query_advice(mpt_table.new_root.hi(), Rotation::cur()),
            meta.query_advice(mpt_config.mpt_table.old_root.hi(), Rotation::cur()),
        ),
    ];

    lookups
        .into_iter()
        .map(|(from, to)| (from * is_not_padding.clone(), to))
        .collect()
});
```

## Caveats

The modifications of the block are obtained by having a list of `address/storage_keys` of changes and by
querying the state in the previous and current block, for example:
```
let old = client
    .get_proof(
        address,
        storage_keys.clone(),
        Some(BlockId::Number(BlockNumber::Number(block_no - 1))),
    )
    .await?;

let new = client
    .get_proof(
        address,
        storage_keys.clone(),
        Some(BlockId::Number(BlockNumber::Number(block_no))),
    )
    .await?;
```

We ignore the modifications where nothing changes:
```
if old.balance == new.balance
    && old.nonce == new.nonce
    && old.code_hash == new.code_hash
    && old.storage_hash == new.storage_hash
{
    continue;
}
```

When the account is created implicitly, for example by nonce or balance modification, the codehash
is set to the default value. In some light client tests, there was a further call to set the codehash to the default
value, but it was unnecessary, so it can be omitted:
```
let default_code_hash = "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470";
let is_default = new.code_hash == H256::from_str(default_code_hash).unwrap();
if old.code_hash != new.code_hash && !is_default {
    changed_values.push(TrieModification::codehash(address, new.code_hash));
}
```

Note that this was causing constraint failure only because the light client requires that if there is
a modification of the root in the current row, it has to be in the next one too (if not padding) - and
there was no modification of the root in the codehash modification call because it was already set implicitly.

The same constraint failed also in the case when the initial values has been proved first (the values in the
previous block). In this case the old block was queried with the address of the account that has been created
only in the new block, to avoid this failure, such modifications need to be ignored:
```
let old = client
    .get_proof(
        address,
        storage_keys.clone(),
        Some(BlockId::Number(BlockNumber::Number(block_no - 1))),
    )
    .await?;

// Skip if the account doesn't exist in the old block.
if old.balance.is_zero() && old.code_hash.is_zero()
    && old.nonce.is_zero() && old.storage_hash.is_zero()
{
    continue;
}
```