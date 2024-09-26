# Account leaf

An account leaf stores the information about the account nonce, balance, codehash (smart contract code hash), and hash of the account's storage trie.

In the trie, when an account is added two things can happen:
 1. There exists another account which has the same address to the some point as the one that
 is being added, including the position of this account in the branch.
 In this case a new branch is added to the trie.
 The existing account drifts down one level to the new branch. The newly
 added account also appears in this branch. For example, let us say that there exists an account `A`
 with address nibbles `[3, 12, 3]` in the trie. Let's say three branches are above `A` and to navigate to the account leaf, we need to choose the positions `3, 12, 3` in the three branches. We then add the account `A1` with address nibbles `[3, 12, 5]`
 to the trie. The branch will appear (at position `[3, 12]`) which will have `A` at position `3`
 and `A1` at position `5`. This means there will be an additional branch in `C` proof (or in `S`
 proof when the situation is reversed - we are deleting the leaf instead of adding).
 For this reason the MPT circuit uses a placeholder branch for `S` proof (for `C` proof in reversed situation)
 to preserve the circuit layout.

 2. The branch where the new account is to be added has `nil` node at the position where the new account
 is to be added. For example, let us have a branch at `[3, 12]`, we are adding a leaf with the
 first three address nibbles being `[3, 12, 5]`, and the position `5` in our branch is not occupied.
 In this case, the `getProof` response (before we add a leaf) does not end with a leaf, but with a branch.
 To preserve the layout and to enable lookups, a placeholder account leaf is added in the `S` proof (in `C` proof in the delete scenario).


An example account leaf RLP stream:
<!--
TestAccountAddPlaceholderExtension
-->
```
[248 108 157 52 45 53 199 120 18 165 14 109 22 4 141 198 233 128 219 44 247 218 241 231 2 206 125 246 58 246 15 3 184 76 248 74 4 134 85 156 208 108 8 0 160 86 232 31 23 27 204 85 166 255 131 69 230 146 192 248 110 91 72 224 27 153 108 173 192 1 98 47 181 227 99 180 33 160 197 210 70 1 134 247 35 60 146 126 125 178 220 199 3 192 229 0 182 83 202 130 39 59 123 250 216 4 93 133 164 112]
```

If, for example, the balance is modified, we get the following RLP (only the substream representing the balance is modified):
```
[248 101 156 58 168 111 115 58 191 32 139 53 139 168 184 7 8 29 109 70 164 7 116 82 56 174 242 193 51 253 77 184 70 248 68 4 23 160 86 232 31 23 27 204 85 166 255 131 69 230 146 192 248 110 91 72 224 27 153 108 173 192 1 98 47 181 227 99 180 33 160 197 210 70 1 134 247 35 60 146 126 125 178 220 199 3 192 229 0 182 83 202 130 39 59 123 250 216 4 93 133 164 112]
```

In the circuit, the account leaf node looks as follows:
```
{
"address":[204,228,98,4,186,168,111,115,58,191,32,139,53,139,168,184,7,8,29,109,70,164,7,116,82,56,174,242,193,51,253,77],
"list_rlp_bytes":[[248,108],[248,101]],
"value_rlp_bytes":[[184,76],[184,70]],
"value_list_rlp_bytes":[[248,74],[248,68]],
"drifted_rlp_bytes":[248,107],
"wrong_rlp_bytes":[248,101]},
"storage":null,
"values":[
    [157,52,45,53,199,120,18,165,14,109,22,4,141,198,233,128,219,44,247,218,241,231,2,206,125,246,58,246,15,3,0,0,0,0],
    [156,58,168,111,115,58,191,32,139,53,139,168,184,7,8,29,109,70,164,7,116,82,56,174,242,193,51,253,77,0,0,0,0,0],
    [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [134,85,156,208,108,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0],
    [160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,112,0],
    [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [23,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0],
    [160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,112,0],
    [156,61,53,199,120,18,165,14,109,22,4,141,198,233,128,219,44,247,218,241,231,2,206,125,246,58,246,15,3,0,0,0,0,0],
    [156,58,168,111,115,58,191,32,139,53,139,168,184,7,8,29,109,70,164,7,116,82,56,174,242,193,51,253,77,0,0,0,0,0]
],
"keccak_data":[
    [248,108,157,52,45,53,199,120,18,165,14,109,22,4,141,198,233,128,219,44,247,218,241,231,2,206,125,246,58,246,15,3,184,76,248,74,4,134,85,156,208,108,8,0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,112],[248,101,156,58,168,111,115,58,191,32,139,53,139,168,184,7,8,29,109,70,164,7,116,82,56,174,242,193,51,253,77,184,70,248,68,4,23,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,112],
    [248,107,156,61,53,199,120,18,165,14,109,22,4,141,198,233,128,219,44,247,218,241,231,2,206,125,246,58,246,15,3,184,76,248,74,4,134,85,156,208,108,8,0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,112]
]
}
```

The rows of `values` are:
```
KeyS,
KeyC,
NonceS,
BalanceS,
StorageS,
CodehashS,
NonceC,
BalanceC,
StorageC,
CodehashC,
Drifted,
Wrong,
LongExtNodeKey, // only used when extension node nibbles are modified
LongExtNodeNibbles, // only used when extension node nibbles are modified
LongExtNodeValue, // only used when extension node nibbles are modified
ShortExtNodeKey, // only used when extension node nibbles are modified
ShortExtNodeNibbles, // only used when extension node nibbles are modified
ShortExtNodeValue, // only used when extension node nibbles are modified
Address, // account address
Key, // hashed account address
```

Note that `Address` and `Key` are added in the method `load_proof` in `mpt_circuit.rs`.

Each of the `values` is checked by [MainRLPGadget](gadgets.md) to ensure that the RLP bytes correspond
to the RLP stream length. For example, the first value of the `values` above is `[157,52,45,53,...]`.
It needs to be checked that the length of the stream is `29 = 157 - 128`.

We can reconstruct the `S` RLP stream if we start with `list_rlp_bytes[0]`, then append `KeyS`,
`value_rlp_bytes[0]`, `value_list_rlp_bytes[0]`, `NonceS`, `BalanceS`, `StorageS`, and `CodehashS`.

We can reconstruct the `C` RLP stream if we start with `list_rlp_bytes[1]`, then append `KeyC`,
`value_rlp_bytes[1]`, `value_list_rlp_bytes[1]`, `NonceC`, `BalanceC`, `StorageC`, and `CodehashC`.

## Constraints

There is a [memory](main.md) mechanism that is used for `MainData`, `ParentData`, and `KeyData` -
the lookup table is being built dynamically and in each node there is a check whether the data has been updated
correctly. 

`MainData` contains the following fields: `proof_type`, `is_below_account`, `address_rlc`, `root_prev`,
and `root`. 

### Constraint 1

Check with a lookup that the [memorized](main.md) values for `MainData` are correct:
```
config.main_data = MainData::load(cb, &mut ctx.memory[main_memory()], 0.expr());
```

Note that the key is used for a lookup (`0` in the case above means the current node) - the key is important because in different nodes there are different correct values.
In each node, the circuit checks whether `MainData` is set correctly and
stores it in the lookup table using `MainData::store` call.

### Constraint 2

Do not allow an account node to follow another account node:
```
main_data.is_below_account = false
```

Note that `is_below_account` is set to `false` in the start and storage leaf node (second parameter):
``` 
MainData::store(
    cb,
    &mut ctx.memory[main_memory()],
    [
        config.proof_type.expr(),
        false.expr(),
        0.expr(),
        root[true.idx()].lo().expr(),
        root[true.idx()].hi().expr(),
        root[false.idx()].lo().expr(),
        root[false.idx()].hi().expr(),
    ],
);
```

and is set to `true` in the account leaf node:
```
MainData::store(
    cb,
    &mut ctx.memory[main_memory()],
    [
        config.main_data.proof_type.expr(),
        true.expr(),
        address_item.word().lo()
            + address_item.word().hi() * pow::value::<F>(256.scalar(), 16),
        config.main_data.new_root.lo().expr(),
        config.main_data.new_root.hi().expr(),
        config.main_data.old_root.lo().expr(),
        config.main_data.old_root.hi().expr(),
    ],
);
```

### Constraint 3

Check with a lookup that the [memorized](main.md) values for `S ParentData` are correct:
```
parent_data[0] = ParentData::load(cb, &mut ctx.memory[parent_memory(true)], 0.expr());
```

### Constraint 4

Check with a lookup that the [memorized](main.md) values for `C ParentData` are correct:
```
parent_data[1] = ParentData::load(cb, &mut ctx.memory[parent_memory(false)], 0.expr());
```

### Constraint 5

Check with a lookup that the [memorized](main.md) values for `S KeyData` are correct:
```
key_data[0] = KeyData::load(cb, &mut ctx.memory[key_memory(true)], 0.expr());
```

### Constraint 6

Check with a lookup that the [memorized](main.md) values for `C KeyData` are correct:
```
key_data[1] = KeyData::load(cb, &mut ctx.memory[key_memory(false)], 0.expr());
```

### Constraint 7

`IsEqualGadget` (using `IsZeroGadget`) to determine the proof type:
```
config.is_non_existing_account_proof = IsEqualGadget::construct(
    &mut cb.base,
    config.main_data.proof_type.expr(),
    MPTProofType::AccountDoesNotExist.expr(),
);
config.is_account_delete_mod = IsEqualGadget::construct(
    &mut cb.base,
    config.main_data.proof_type.expr(),
    MPTProofType::AccountDestructed.expr(),
);
...
```

### Constraint 8

This and the following constraints are triggered only for the cases when there is no extension node with modified nibbles.
The constraints for the modified extension node cases are in `ModExtensionGadget`.

The constraint is used to check whether the leaf is a placeholder (the trie is empty or branch has a nil value
at the position at the account address):
```
config.is_placeholder_leaf[is_s.idx()] =
    IsPlaceholderLeafGadget::construct(cb, parent_data[is_s.idx()].hash.expr());
```

### Constraint 9

Check the leaf RLP and enable access to the functions like `rlc2`:
```
*rlp_key = ListKeyGadget::construct(cb, &key_items[is_s.idx()]);
```

### Constraint 10:

The total number of nibbles needs to be `KEY_LEN_IN_NIBBLES = 64`.
To get all the nibbles we need to take the nibbles that are used for navigating
through the branches / extension nodes (stored in `key_data`) and nibbles stored
in the leaf.

```
let num_nibbles =
    num_nibbles::expr(rlp_key.key_value.len(), key_data[is_s.idx()].is_odd.expr());
require!(key_data[is_s.idx()].num_nibbles.expr() + num_nibbles.expr() => KEY_LEN_IN_NIBBLES);
```

### Constraint 11

This constraint is enabled only for the non-placeholder leaf.

Check that the hash of all bytes of the account leaf is in the parent.

```
let hash = parent_data[is_s.idx()].hash.expr();
require!((1.expr(), leaf_rlc, rlp_key.rlp_list.num_bytes(), hash.lo(), hash.hi()) =>> @KECCAK);
```

Note that `hash` is the hash of the modified branch child in the parent branch.
If the account leaf is in the first level (no branch above it), the variable `hash` obtained
from `parent_data` contains the hash of the trie.



###

Storage and codehash RLP constraints (the length of storage and codehash is always `32`):
```
AccountStorageS RLP = 160
AccountStorageC RLP = 160
AccountCodehashS RLP = 160
AccountCodehashC RLP = 160
```

`KeyData` contains the following fields: `rlc`, `mult`, `num_nibbles`, `is_odd`, `drifted_rlc`,
`drifted_mult`, `drifted_num_nibbles`, and `drifted_is_odd`.

Total number of the account address nibbles nees to be `64`. This is to prevent having short addresses
which could lead to a root node which would be shorter than `32` bytes and thus not hashed. That
means the trie could be manipulated to reach the desired root. The constraint below ensures that
the number of nibbles in the branches and extensions above the leaf (stored in `key_data.num_nibbles`)
together with the number of nibbles in the leaf is `64`:
```
key_data.num_nibbles + num_nibbles = 64
```

`ParentData` contains the following fields: `rlc`, `is_root`, `is_placeholder`, and `drifted_parent_rlc`.
The field `parent_data.rlc` contains the hash of a child. The constraint below checks that the hashed
value of the leaf RLC is `parent_data.rlc`:
```
(1, leaf_rlc, rlp_key.rlp_list.num_bytes(), parent_data.rlc) in keccak_table
```

The first RLP byte of the value has to be `184`. This is the RLP byte meaning that behind this byte
there is a string of length more than `55` and that only `1 = 184 - 183` byte is reserved
for the length (the second RLP byte). The string is always of length greater than `55` because it contains
the codehash (`32` bytes) and storage root (`32` bytes). Constraints:
```
value_rlp_bytes[0][0] = 183 + 1
value_rlp_bytes[1][0] = 183 + 1
```

The value length is specified in `value_rlp_bytes[i][1]` and the length of the list containing in the
value is specified in `value_list_rlp_bytes[i][1]`. The difference is always `2` - the difference coming
from the two bytes: `value_list_rlp_bytes[i][0]` and `value_list_rlp_bytes[i][1]`. Constraints:
```
value_rlp_bytes[0][1] = value_list_rlp_bytes[0][1] + 2
value_rlp_bytes[1][1] = value_list_rlp_bytes[1][1] + 2
```

The first RLP byte of the list is always `248 = 247 + 1` where `1` means there is `1` byte
used for storing the list length (in `value_list_rlp_bytes[i][1]`). Constraints:
```
value_list_rlp_bytes[0][0] = 247 + 1
value_list_rlp_bytes[1][0] = 247 + 1
```

The list contains the nonce, the balance, the storage (`1 + 32`), and the codehash (`1 + 32`). The length
(`value_list_rlp_bytes[i][1]`) needs to reflect this:
```
value_list_rlp_bytes[i][1] = nonce_items[i].num_bytes() + balance_items[i].num_bytes() + (2 * (1 + 32))
```

The key length and the value list length have to match the account length. Constraints:
```
config.rlp_key[0].rlp_list.len() = config.rlp_key[0].key_value.num_bytes() + value_list_num_bytes
config.rlp_key[1].rlp_list.len() = config.rlp_key[1].key_value.num_bytes() + value_list_num_bytes
```
Note that here `config.rlp_key[i]` contains the key (and its RLP bytes), but also `list_rlp_bytes[i]`.
`rlp_key[i].rlp_list.len()` returns `list_rlp_bytes[i][1]` (`108` and `101` in the above example).

We then add a value to the dynamic lookup table that stores `key` data:
```
KeyData::store_defaults(cb, &ctx.memory[key_memory(is_s)]);
```
This sets the `key` data to `0` to be prepared for a storage proof (up until this point `key`
was used for the address).
When in the first storage proof node, the lookup will be executed to
ensure that the key RLC is `0` (the key RLC is updated in each trie level).

We add a value to the dynamic lookup table that stores `parent` data:
```
ParentData::store(
    cb,
    &ctx.memory[parent_memory(is_s)],
    storage_rlc[is_s.idx()].expr(),
    true.expr(),
    false.expr(),
    storage_rlc[is_s.idx()].expr(),
);
```
When in the first storage proof node, the lookup will be executed to
ensure that the first storage proof node hash is the same as the parent `rlc` 
(which stores the storage trie root hash).

Finally, we add a value to the dynamic table that stores `main` data:
```
MainData::store(
    cb,
    &ctx.memory[main_memory()],
    [
        config.main_data.proof_type.expr(),
        true.expr(),
        is_non_existing_account.expr(),
        key_rlc[true.idx()].expr(),
        config.main_data.root_prev.expr(),
        config.main_data.root.expr(),
    ],
);
```
Note the `true` value as the second parameter which results into `is_below_account = 1`. This is to
know that we are from now on in the storage proof (below account proof) and is used to prevent having
two account proofs in a row.

When `config.is_account_delete_mod = true` we need to make sure there is no account at the given
address.
There are two possible cases:
- 1. Account leaf is deleted and there is a `nil` object in
branch. In this case we have a placeholder leaf.
- 2. Account leaf is deleted from a branch with two leaves, the remaining
leaf moves one level up and replaces the branch. In this case we
have a branch placeholder.

Note that for the second case, the `drifted` gadget constraints ensure the proper transition.
TODO: update the names when updated in the circuit
```
require!(or::expr([
    config.is_in_empty_trie[false.idx()].expr(),
    config.parent_data[false.idx()].is_placeholder.expr()
]) => true);
```

When `config.is_account_delete_mod = false` we need to make sure there
is only one modification:
```
ifx!{not!(config.is_nonce_mod) => {
    require!(nonce_rlc[false.idx()] => nonce_rlc[true.idx()]);
}}
ifx!{not!(config.is_balance_mod) => {
    require!(balance_rlc[false.idx()] => balance_rlc[true.idx()]);
}}
ifx!{not!(config.is_storage_mod) => {
    require!(storage_rlc[false.idx()] => storage_rlc[true.idx()]);
}}
ifx!{not!(config.is_codehash_mod) => {
    require!(codehash_rlc[false.idx()] => codehash_rlc[true.idx()]);
}}
```

For `AccountDoesNotExist` proof we need to ensure `S` and `C` proofs are the same — there is no
change in the trie and the same address is used:
```
require!(config.main_data.root => config.main_data.root_prev);
require!(key_rlc[true.idx()] => key_rlc[false.idx()]);
```

Finally, the MPT table (for external lookups) is checked to contain the proper values.

<!--
Note that a new entry is stored in the lookup table with the field `is_below_account` set to `true`.

In the account leaf, all the fields stay the same except `address_rlc`. This one was set to `0` in
the `StartNode` and should be the address RLC of the account in the account leaf row.
This serves to check that there is always an account leaf above the storage leaf (only in the account leaf,
the field `address_rlc` is allowed to be updated).
-->

## Gadgets

`AccountLeafConfig` uses the following [gadgets](gadgets.md):

```
rlp_key: [ListKeyGadget<F>; 2],
is_in_empty_trie: [IsEmptyTreeGadget<F>; 2],
drifted: DriftedGadget<F>,
wrong: WrongGadget<F>,
is_non_existing_account_proof: IsEqualGadget<F>,
is_account_delete_mod: IsEqualGadget<F>,
is_nonce_mod: IsEqualGadget<F>,
is_balance_mod: IsEqualGadget<F>,
is_storage_mod: IsEqualGadget<F>,
is_codehash_mod: IsEqualGadget<F>
```

### rlp_key

`rlp_key` stores two `ListKeyGadget` (one for `S` key, one for `C` key).
It can be used to access the information about the key (length, number of nibbles, key RLC,
RLC multiplier to be used after key, ...), but it also
stores the first RLP bytes of the account leaf (that are stored in `rlp_list_bytes`).

```
pub(crate) struct ListKeyGadget<F> {
    pub(crate) rlp_list_bytes: [Cell<F>; 3],
    pub(crate) rlp_list: RLPListGadget<F>,
    pub(crate) key_value: RLPItemView<F>,
    pub(crate) key: LeafKeyGadget<F>,
}
```

`ListKeyGadget` contains `RLPListGadget` (as `MainRLPGadget` does) because the account leaf
is always a list of RLP items (and `ListKeyGadget` does not contain only the key, but also
the first bytes of the account leaf). Thus, for example, `rlp_list` can be used to access the
number of bytes of the account leaf stream.

### is_in_empty_trie

The gadget [IsEmptyTreeGadget](gadgets.md) is used to check whether the trie is empty or there
is no leaf in the branch at the modified position - this is to avoid triggering the account leaf 
constraints when there is no account leaf.

### drifted

The gadget [DriftedGadget](gadgets.md) handles the leaf being moved from one branch to a newly created branch.
`AccountDrifted` value contains the key of the leaf that drifted to a new branch - it is the same as the key
before drifting, but with the first nibble (or nibbles if extension node) removed.

The gadget is constructed as follows:

 * `key_rlc` contains the key RLC of the leaf before it drifted, this value needs to be checked in the 
 gadget to be the same as the key RLC of the leaf after it drifted (the nibble(s) moved from the leaf key
 to the nibbles that mark the path to the leaf)
 * `leaf_no_key_rlc` is the RLC of the leaf value (which does not change when the leaf drifts to a new
 branch)
 * `drifted_bytes` contains the `AccountDrifted` value.

```
config.drifted = DriftedGadget::construct(
    cb,
    &config.parent_data,
    &config.key_data,
    &key_rlc,
    &leaf_no_key_rlc,
    &drifted_bytes,
    &ctx.r,
);
```

### wrong

The `AccountWrong` value has nonzero bytes only when there is an `AccountDoesNotExist` proof
and when there is a leaf returned by `getProof` which does not correspond to the actual enquired address.
[WrongGadget](gadgets.md) ensures there exists a leaf which has some
number of the starting nibbles the same as the enquired address (the path through branches
above the leaf), but at the same time the full address is not the same - the nibble that denotes the
position in the last branch (above the leaf) is the same, but the remaining nibbles stored in the leaf
differ.

When this particular `AccountDoesNotExist` proof subtype occurs, the `AccountWrong` holds the value
of the enquired address, while the wrong leaf address is stored in the `AccountKeyC` value.


# Account leaf (obsolete)

## Account key constraints

### Account leaf RLC after key

#### Account leaf key s_main.rlp1 = 248

Account leaf always starts with 248 because its length is always longer than 55 bytes due to
containing two hashes - storage root and codehash, which are both of 32 bytes. 
248 is RLP byte which means there is `1 = 248 - 247` byte specifying the length of the remaining
list. For example, in `[248,112,157,59,...]`, there are 112 byte after the second byte.

#### Leaf key RLC

In each row of the account leaf we compute an intermediate RLC of the whole leaf.
The RLC after account leaf key row is stored in `acc` column. We check the stored value
is computed correctly.

### Zeros in s_main.bytes & c_main.rlp1 & c_main.rlp2 after key ends

Key RLC is computed over all of `s_main.bytes[1], ..., s_main.bytes[31], c_main.rlp1, c_main.rlp2`
because we do not know the key length in advance.
To prevent changing the key and setting `s_main.bytes[i]` (or `c_main.rlp1/c_main.rlp2`) for
`i > key_len + 1` to get the desired key RLC, we need to ensure that
`s_main.bytes[i] = 0` for `i > key_len + 1`.

Note: the key length is always in `s_main.bytes[0]` here as opposed to storage
key leaf where it can appear in `s_rlp2` too. This is because the account
leaf contains nonce, balance, ... which makes it always longer than 55 bytes,
which makes a RLP to start with 248 (`s_rlp1`) and having one byte (in `s_rlp2`)
for the length of the remaining stream.

### mult_diff

When the account intermediate RLC is computed in the next row (nonce balance row), we need
to know the intermediate RLC and the randomness multiplier (`r` to some power) from the current row.
The power of randomness `r` is determined by the key length - the intermediate RLC in the current row
is computed as (key starts in `s_main.bytes[1]`):

```
rlc = s_main.rlp1 + s_main.rlp2 * r + s_main.bytes[0] * r^2 + key_bytes[0] * r^3 + ... + key_bytes[key_len-1] * r^{key_len + 2}
```

So the multiplier to be used in the next row is `r^{key_len + 2}`. 

`mult_diff` needs to correspond to the key length + 2 RLP bytes + 1 byte for byte that contains the key length.
That means `mult_diff` needs to be `r^{key_len+1}` where `key_len = s_main.bytes[0] - 128`.

### Account leaf address RLC & nibbles count (branch not placeholder)

#### Account leaf key with even nibbles: s_main.bytes[1] = 32

If there is an even number of nibbles in the leaf, `s_main.bytes[1]` need to be 32.

#### Address RLC

Account leaf contains the remaining nibbles of the account address. Combining the path 
of the leaf in the trie and these remaining nibbles needs to be the same as the account
address which is given in the `address_rlc` column that is to be used by a lookup (see the
constraint below).

Address RLC needs to be computed properly - we need to take into account the path of the leaf 
in the trie and the remaining nibbles in the account leaf.

The intermediate RLC is retrieved from the last branch above the account leaf - this
presents the RLC after the path to the leaf is considered. After this, the bytes (nibbles
in a compacted form) in the leaf have to be added to the RLC.

#### Computed account address RLC same as value in address_rlc column

The computed key RLC needs to be the same as the value in `address_rlc` column.
This seems to be redundant (we could write one constraint instead of two:
`key_rlc_acc - address_rlc = 0`), but note that `key_rlc` is used in
`account_leaf_key_in_added_branch` and in cases when there is a placeholder branch
we have `key_rlc - address_rlc != 0` because `key_rlc` is computed for the branch
that is parallel to the placeholder branch.

Note that there is a similar constraint for the cases when the account leaf is in the first level, but
here we do not fetch for the intermediate RLC from the branch above as there is no branch above.

### Account leaf address RLC & nibbles count (after placeholder)

This gate is again similar to the gate `Account leaf address RLC & nibbles count (leaf not in first level, branch not placeholder)`, but with a leaf being after a branch placeholder.

#### Account address RLC after branch placeholder

The example layout for a branch placeholder looks like (placeholder could be in `C` proof too):
```
Branch 1S               || Branch 1C
Branch 2S (placeholder) || Branch 2C
Leaf S
Leaf C
```

Using `Previous key RLC` constraint we ensured that we copied the key RLC from Branch 1S
to Leaf S `accs.acc_c.rlc` column. So when add nibbles to compute the key RLC (address RLC)
of the account, we start with `accs.acc_c.rlc` value from the current row.

Although `key_rlc` is not compared to `address_rlc` in the case when the leaf
is below the placeholder branch (`address_rlc` is compared to the parallel leaf `key_rlc`), 
we still need properly computed `key_rlc` to reuse it in `account_leaf_key_in_added_branch`.

Note: `key_rlc - address_rlc != 0` when placeholder branch.

### Account delete

#### If account delete, there is either a placeholder leaf or a placeholder branch

We need to make sure there is no leaf when account is deleted. Two possible cases:
1. Account leaf is deleted and there is a nil object in branch. In this case we have 
    a placeholder leaf.
2. Account leaf is deleted from a branch with two leaves, the remaining leaf moves one level up
    and replaces the branch. In this case we have a branch placeholder.

So we need to check there is a placeholder branch when we have the second case.

Note: we do not need to cover the case when the (only) branch dissapears and only one
leaf remains in the trie because there will always be at least two leaves
(the genesis account) when account will be deleted,
so there will always be a branch / extension node (and thus placeholder branch).

### Range lookups

Range lookups ensure that `s_main`, `c_main.rlp1`, `c_main.rlp2` columns are all bytes (between 0 - 255).
Note that `c_main.bytes` columns are not used.

## Account leaf nonce balance constraints

An example rows of the account leaf are:

```
[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[0,0,0,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[184,70,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,248,68,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[184,70,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,248,68,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]

[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]

[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```

In `ACCOUNT_LEAF_NONCE_BALANCE_S` row (fourth row), there is `S` nonce stored in `s_main`
and `S` balance in `c_main`. We can see nonce in `S` proof is `0 = 128 - 128`.

In `ACCOUNT_LEAF_NONCE_BALANCE_C` row (fifth row), there is `C` nonce stored in `s_main`
and `C` balance in `c_main`. We can see nonce in `C` proof is `1`.

The constraints for the first gate of `AccountLeafNonceBalanceChip` which is named
`Account leaf nonce balance RLC & RLP` are given below.

### Account leaf nonce balance RLC & RLP

#### Bool check is_nonce_long & Bool check is_balance_long

If nonce (same holds for balance) is smaller or equal to 128, then it will occupy only one byte:
`s_main.bytes[0]` (`c_main.bytes[0]` for balance).
We can see such case in the example above. The nonce there is 128 (meaning 0) before modification
and 1 (meaning 1) after modification.

In case nonce (same for balance) is bigger than 128, it will occupy more than 1 byte.
The example row below shows nonce value 142, while 129 means there is a nonce of byte
length `1 = 129 - 128`.
Balance in the example row below is: `28 + 5 * 256 + 107 * 256^2 + ... + 59 * 256^6`, while
135 means there are `7 = 135 - 128` bytes.
```
[rlp1 rlp2 bytes[0] bytes[1]]           rlp1 rlp2 bytes[0] bytes[1]   ...    ]
[184  78   129      142       0 0 ... 0 248  76   135      28       5 107 201 118 120 59 0 0 ... 0]
```

The `sel1` column in the `ACCOUNT_LEAF_KEY_S` or `ACCOUNT_LEAF_KEY_C` row
is used to mark whether nonce is of 1 byte (short) or more than 1 byte (long).
`sel1 = 1` means long, `sel1 = 0` means short.
`Bool check is_nonce_long` constraint ensures the value is boolean.

Analogously, `sel2` holds the information whether balance is long or short.
Bool check `is_balance_long` constraint ensures the `sel2` value is boolean.

#### s_main.bytes[i] = 0 for i > 0 when is_nonce_short

It is important that there are 0s in `s_main.bytes` after the nonce bytes end.
When nonce is short (1 byte), like in `[184,70,1,0,...]`, the constraint is simple:
`s_main.bytes[i] = 0` for all `i > 0`.

When nonce is long, the constraints need to be written differently because we do not
know the length of nonce in advance.
The row below holds nonce length specification in `s_main.bytes[0]`.
The length in the example below is `1 = 129 - 128`,
so the constraint needs to be `s_main.bytes[i] = 0` for
all `i > 1` (note that the actual value is in `s_main.bytes[1]`).

```
[184  78   129      142       0 0 ... 0 248  76   135      28       5 107 201 118 120 59 0 0 ... 0]
```

But instead of 129 we could have 130 or some other value in `s_main.bytes[0]`. For this
reason, the constraints are implemented using `key_len_lookup`, more about this approach
in what follows.

#### c_main.bytes[i] = 0 for i > 0 when is_balance_short

The balance constraints are analogous to the nonce constraints described above.
The difference is that balance is stored in `c_main.bytes`.

#### Nonce RLC long 

Besides having nonce (its bytes) stored in `s_main.bytes`, we also have the RLC
of nonce bytes stored in `s_mod_node_hash_rlc` column. The value in this column
is to be used by lookups.
`Nonce RLP long` constraint ensures the RLC of a nonce is computed properly when
nonce is long.

#### Nonce RLC short

Similarly as in `Nonce RLP long` constraint, 
`Nonce RLP short` constraint ensures the RLC of a nonce is computed properly when
nonce is short.

#### Balance RLC long 

Besides having balance (its bytes) stored in `c_main.bytes`, we also have the RLC
of nonce bytes stored in `c_mod_node_hash_rlc` column. The value in this column
is to be used by lookups.
`Balance RLP long` constraint ensures the RLC of a balance is computed properly when
balance is long.

#### Balance RLC short

Similarly as in `Balance RLP long` constraint, 
`Balance RLP short` constraint ensures the RLC of a balance is computed properly when
balance is short.

#### S nonce RLC is correctly copied to value_prev column

To enable lookup for nonce modification we need to have S nonce and C nonce in the same row.
For this reason, S nonce RLC is copied to `value_prev` column.

#### C nonce RLC is correctly copied to lookup row

To enable lookup for nonce modification we need to have S nonce and C nonce in the same row.
For this reason, C nonce RLC is copied to `value` column in `ACCOUNT_LEAF_NONCE_BALANCE_S` row.

#### C nonce RLC is correctly copied to NON_EXISTING_ACCOUNT row

To enable lookup for nonce modification we need to have S nonce and C nonce in the same row.
For this reason, C nonce RLC is copied to `value` column in `NON_EXISTING_ACCOUNT` row.

#### S balance RLC is correctly copied to C row

To enable lookup for balance modification we need to have S balance and C balance in the same row.
For this reason, S balance RLC is copied to `value_prev` column in C row.

#### S balance RLC is correctly copied to C row

To enable lookup for balance modification we need to have `S` balance and `C` balance
in the same row. For this reason, `S` balance RLC is copied to `sel2` column in `C` row.
This constraint checks whether the value is properly copied.

#### C balance RLC is correctly copied to value column

To enable lookup for balance modification we need to have S balance and C balance in the same row.
For this reason, C balance RLC is copied to `value` column in C row.
constraints.push((


#### If storage or balance or codehash modification: S nonce = C nonce

We need to ensure there is only one modification at a time. If there is storage or
balance or codehash modification, we need to ensure `S` nonce and `C` nonce are the same.

Note: For `is_non_existing_account_proof` we do not need this constraint,
`S` and `C` proofs are the same and we need to do a lookup into only one
(the other one could really be whatever).

#### If storage or nonce or codehash modification: S balance = C balance

We need to ensure there is only one modification at a time. If there is storage or
nonce modification, we need to ensure `S` balance and `C` balance are the same.

Note: For `is_non_existing_account_proof` we do not need this constraint,
`S` and `C` proofs are the same and we need to do a lookup into only one
(the other one could really be whatever).

#### Leaf nonce balance RLC

Computed RLC after nonce balance row is the same as the stored RLC value.

#### Leaf nonce RLC mult (nonce long)

When adding nonce bytes to the account leaf RLC we do:

```
rlc_after_nonce = rlc_tmp + s_main.bytes[0] * mult_tmp + s_main.bytes[1] * mult_tmp * r + ... + s_main.bytes[k] * mult_tmp * r^k
```

Note that `rlc_tmp` means the RLC after the previous row, while `mult_tmp` means the multiplier
(power of randomness `r`) that needs to be used for the first byte in the current row.

In this case we assumed there are `k + 1` nonce bytes. After this we continue adding bytes:
`rlc_after_nonce + b1 * mult_tmp * r^{k+1} + b2 * mult_tmp * r^{k+1} * r + ...
Note that `b1` and `b2` are the first two bytes that need to used next (balance bytes).

The problem is `k` can be different from case to case. For this reason, we store `r^{k+1}` in
`mult_diff_nonce` (which is actually `acc_c`).
That means we can compute the expression above as:
`rlc_after_nonce + b1 * mult_tmp * mult_diff_nonce + b2 * mult_tmp * mult_diff_nonce * r + ...

However, we need to ensure that `mult_diff_nonce` corresponds to `s_main.bytes[0]` where the length
of the nonce is specified. This is done using `key_len_lookup` below.

There is one more detail: when computing RLC after nonce, we compute also the bytes that come before
nonce bytes in the row. These are: `s_main.rlp1`, `s_main.rlp2`, `c_main.rlp1`, `c_main.rlp2`.
It is a bit confusing (we are limited with layout), but `c_main.rlp1` and `c_main.rlp2`
are bytes that actually appear in the account leaf RLP stream before `s_main.bytes`.
So we have:

```
rlc_after_nonce = rlc_tmp + s_main.rlp1 * mult_tmp + s_main.rlp2 * mult_tmp * r + c_main.rlp1 * mult_tmp * r^2 + c_main.rlp2 * mult_tmp * r^3 + s_main.bytes[0] * mult_tmp * r^4 + ... + s_main.bytes[k] * mult_tmp * r^4 * r^k
```

That means `mult_diff_nonce` needs to store `r^4 * r^{k+1}` and we continue computing the RLC
as mentioned above:

```
rlc_after_nonce + b1 * mult_tmp * mult_diff_nonce + b2 * mult_tmp * mult_diff_nonce * r + ...
```

Let us observe the following example.
```
[184  78   129      142       0 0 ... 0 248  76   135      28       5 107 201 118 120 59 0 0 ... 0]
```

Here:

```
rlc_after_nonce = rlc_tmp + 184 * mult_tmp + 78 * mult_tmp * r + 248 * mult_tmp * r^2 + 76 * mult_tmp * r^3 + 129 * mult_tmp * r^4 + 142 * mult_tmp * r^5
```

And we continue computing the RLC:

```
rlc_after_nonce + 135 * mult_tmp * mult_diff_nonce + 28 + mult_tmp * mult_diff_nonce * r + ...
```

#### Leaf nonce RLC mult (nonce short)

When nonce is short (occupying only one byte), we know in advance that `mult_diff_nonce = r^5`
as there are `s_main.rlp1`, `s_main.rlp2`, `c_main.rlp1`, `c_main.rlp2`, and `s_main.bytes[0]` bytes to be taken into account.

#### Leaf balance RLC mult (balance long)

We need to prepare the multiplier that will be needed in the next row: `acc_mult_final`.
We have the multiplier after nonce bytes were added to the RLC: `acc_mult_after_nonce`.
Now, `acc_mult_final` depends on the number of balance bytes. 

```
rlc_after_balance = rlc_after_nonce + b1 * acc_mult_after_nonce + ... + bl * acc_mult_after_nonce * r^{l-1}
```

Where `b1,...,bl` are `l` balance bytes. As with nonce, we do not know the length of balance bytes
in advance. For this reason, we store `r^l` in `mult_diff_balance` and check whether:

```
acc_mult_final = acc_mult_after_nonce * mult_diff_balance
```

Note that `mult_diff_balance` is not the last multiplier in this row, but the first in
the next row (this is why there is `r^l` instead of `r^{l-1}`).

#### Leaf balance RLC mult (balance short)

When balance is short, there is only one balance byte and we know in advance that the
multiplier changes only by factor `r`.

#### Leaf nonce balance s_main.rlp2 - c_main.rlp2

`c_main.rlp2` specifies the length of the remaining RLP string. Note that the string
is `s_main.rlp1`, `s_main.rlp2`, `c_main.rlp1`, `c_main.rlp2`, nonce bytes, balance bytes.
Thus, `c_main.rlp2 = #(nonce bytes) + #(balance bytes) + 32 + 32`.
`s_main.rlp2` - `c_main.rlp2` = 2 because of two bytes difference: `c_main.rlp1` and c_main.rlp2`.

Example:
```
[184  78   129      142       0 0 ... 0 248  76   135      28       5 107 201 118 120 59 0 0 ... 0]
```
We can see: `78 - 76 - 1 - 1 = 0`.

#### Lean nonce balance c_main.rlp2

`c_main.rlp2 = #(nonce bytes) + #(balance bytes) + 32 + 32`.
Note that `32 + 32` means the number of codehash bytes + the number of storage root bytes.

#### Account leaf RLP length 

The whole RLP length of the account leaf is specified in the account leaf key row with
`s_main.rlp1 = 248` and `s_main.rlp2`. `s_main.rlp2` in key row actually specifies the length.
`s_main.rlp2` in nonce balance row specifies the length of the remaining string in nonce balance
row, so we need to check that `s_main.rlp2` corresponds to the key length (in key row) and
`s_main.rlp2` in nonce balance row. However, we need to take into account also the bytes
where the lengths are stored:

```
s_main.rlp2 (key row) - key_len - 1 (because key_len is stored in 1 byte) - s_main.rlp2 (nonce balance row) - 1 (because of s_main.rlp1) - 1 (because of s_main.rlp2) = 0
```

Example:
```
[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
[184,70,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,248,68,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```
We can see: `106 - 33 - 1 - 70 - 1 - 1 = 0`.

### mult_diff_nonce

`mult_diff_nonce` needs to correspond to nonce length + 5 bytes:
`s_main.rlp1,` `s_main.rlp2`, `c_main.rlp1`, `c_main.rlp1`, 1 for byte with nonce length (`s_main.bytes[0]`).
That means `mult_diff_nonce` needs to be `r^{nonce_len+5}` where `nonce_len = s_main.bytes[0] - 128`.

Note that when nonce is short, `mult_diff_nonce` is not used (see the constraint above).

### 0s after nonce ends

Nonce RLC is computed over `s_main.bytes[1]`, ..., `s_main.bytes[31]` because we do not know
the nonce length in advance. To prevent changing the nonce and setting `s_main.bytes[i]` for
`i > nonce_len + 1` to get the correct nonce RLC, we need to ensure that
`s_main.bytes[i] = 0` for `i > nonce_len + 1`.

### mult_diff_balance

`mult_diff_balance` needs to correspond to balance length + 1 byte for byte that contains balance length.
That means `mult_diff_balance` needs to be `r^{balance_len+1}` where `balance_len = c_main.bytes[0] - 128`.

Note that when balance is short, `mult_diff_balance` is not used (see the constraint above).

### 0s after balance ends

Balance RLC is computed over `c_main.bytes[1]`, ..., `c_main.bytes[31]` because we do not know
the balance length in advance. To prevent changing the balance and setting `c_main.bytes[i]` for
`i > balance_len + 1` to get the correct balance RLC, we need to ensure that
`c_main.bytes[i] = 0` for `i > balance_len + 1`.

### Range lookups

Range lookups ensure that `s_main` and `c_main` columns are all bytes (0 - 255).

## Account leaf storage codehash constraints

The constraints in `account_leaf_storage_codehash.rs` apply to ACCOUNT_LEAF_STORAGE_CODEHASH_S and
ACCOUNT_LEAF_STORAGE_CODEHASH_C rows.

For example, the two rows might be:
```
[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]
[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]
```

Here, in `ACCOUNT_LEAF_STORAGE_CODEHASH_S` example row, there is `S` storage root stored in `s_main.bytes`
and `S` codehash in `c_main.bytes`. Both these values are hash outputs.
We can see `s_main.rlp2 = 160` which specifies that the length of the following string is `32 = 160 - 128`
(which is hash output). Similarly, `c_main.rlp2 = 160`.

In `ACCOUNT_LEAF_STORAGE_CODEHASH_C` example row, there is `C` storage root stored in `s_main.bytes`
and `C` codehash in `c_main.bytes`. Both these values are hash outputs.

#### Storage root RLC 

`s_main.bytes` contain storage root hash, but to simplify lookups we need to have
the RLC of storage root hash stored in some column too. The RLC is stored in
`s_mod_node_hash_rlc`. We need to ensure that this value corresponds to the RLC
of `s_main.bytes`.

#### Codehash RLC

`c_main.bytes` contain codehash, but to simplify lookups we need to have
the RLC of the codehash stored in some column too. The RLC is stored in
`c_mod_node_hash_rlc`. We need to ensure that this value corresponds to the RLC
of `c_main.bytes`.

#### S codehash RLC is correctly copied to C row

To enable lookup for codehash modification we need to have S codehash
and C codehash in the same row.
For this reason, S codehash RLC is copied to `value_prev` column in C row.

##### C codehash RLC is correctly copied to value row

To enable lookup for codehash modification we need to have S codehash
and C codehash in the same row (`value_prev`, `value` columns).
C codehash RLC is copied to `value` column in C row.

#### If nonce or balance or codehash modification: storage_root_s = storage_root_c

If the modification is nonce or balance or codehash modification, the storage root needs to 
stay the same.

Note: For `is_non_existing_account_proof` we do not need this constraint,
`S` and `C` proofs are the same and we need to do a lookup into only one
(the other one could really be whatever).

#### If nonce or balance or storage modification: codehash_s = codehash_c

If the modification is nonce or balance or storage modification (that means
always except for `is_account_delete_mod` and `is_non_existing_account_proof`),
the storage root needs to stay the same.

Note: For `is_non_existing_account_proof` we do not need this constraint,
`S` and `C` proofs are the same and we need to do a lookup into only one
(the other one could really be whatever).

#### Account leaf storage codehash RLC

The RLC of the account leaf needs to be properly computed. We take the intermediate RLC
computed in the `ACCOUNT_LEAF_NONCE_BALANCE_*` row and add the bytes from the current row.
The computed RLC needs to be the same as the stored value in `acc_s` row.

### Account first level leaf without branch - compared to state root

Check hash of an account leaf to be state root when the leaf is without a branch (the leaf
is in the first level).

Note: the constraints for the first level branch to be compared to the state root
are in `branch_hash_in_parent`.

### Hash of an account leaf in a branch

Hash of an account leaf needs to appear (when not in first level) at the proper position in the
parent branch.

Note: the placeholder leaf appears when a new account is created (in this case there was
no leaf before and we add a placeholder). There are no constraints for
a placeholder leaf, it is added only to maintain the parallel layout.

### Hash of an account leaf when branch placeholder

When there is a placeholder branch above the account leaf (it means the account leaf
drifted into newly added branch, this branch did not exist in `S` proof), the hash of the leaf
needs to be checked to be at the proper position in the branch above the placeholder branch.

Note: a placeholder leaf cannot appear when there is a branch placeholder
(a placeholder leaf appears when there is no leaf at certain position, while branch placeholder
appears when there is a leaf and it drifts down into a newly added branch).

### Hash of an account leaf compared to root when branch placeholder in the first level

When there is a placeholder branch above the account leaf (it means the account leaf
drifted into newly added branch, this branch did not exist in `s` proof) in the first level,
the hash of the leaf needs to be checked to be the state root.

### Range lookups

Range lookups ensure that `s_main` and `c_main` columns are all bytes (between 0 - 255).

Note: `s_main.rlp1` and `c_main.rlp1` are not used.

### Range lookups

Range lookups ensure that the value in the columns are all bytes (between 0 - 255).
Note that `c_main.bytes` columns are not used.

## Account leaf non-existing-account constraints


#### Nil object in parent branch

In case when there is no wrong leaf, we need to check there is a nil object in the parent branch.
Note that the constraints in `branch.rs` ensure that `sel1` is 1 if and only if there is a nil object
at `modified_node` position. We check that in case of no wrong leaf in
the non-existing-account proof, `sel1` is 1.

### Non existing account proof leaf address RLC

Ensuring that the account does not exist when there is only one account in the state trie.
Similarly as `Account address RLC` constraint but for the first level.

Note 1: The hash of the only account is checked to be the state root in `account_leaf_storage_codehash.rs`.
Note 2: There is no nil_object case checked in this gate, because it is covered in the gate
above. That is because when there is a branch (with nil object) in the first level,
it automatically means the account leaf is not in the first level.

### Non existing account proof leaf address RLC (leaf in first level)

Similarly as the gate above, but for the account leaf being in the first level.

### Address of wrong leaf and the enquired address are of the same length

#### The number of nibbles in the wrong leaf and the enquired address are the same

This constraint is to prevent the attacker to prove that some account does not exist by setting
some arbitrary number of nibbles in the account leaf which would lead to a desired RLC.

### s_main.bytes[i] = 0 when key ends

Key RLC is computed over all of `s_main.bytes[1], ..., s_main.bytes[31], c_main.rlp1, c_main.rlp2`
because we do not know the key length in advance.
To prevent changing the key and setting `s_main.bytes[i]` (or `c_main.rlp1/c_main.rlp2`) for
`i > key_len + 1` to get the desired key RLC, we need to ensure that
`s_main.bytes[i] = 0` for `i > key_len + 1`.

Note that the number of the key bytes in the `ACCOUNT_NON_EXISTING` row needs to be the same as
the number of the key bytes in the `ACCOUNT_LEAF_KEY` row.

Note: the key length is always in s_main.bytes[0] here as opposed to storage
key leaf where it can appear in `s_rlp2` too. This is because the account
leaf contains nonce, balance, ... which makes it always longer than 55 bytes,
which makes a RLP to start with 248 (`s_rlp1`) and having one byte (in `s_rlp2`)
for the length of the remaining stream.

### Range lookups

Range lookups ensure that `s_main`, `c_main.rlp1`, `c_main.rlp2` columns are all bytes (between 0 - 255).
Note that `c_main.bytes` columns are not used.


## Example

Let us observe the proof for the modification of the account nonce. Let us assume there is only
one account stored in the trie. We change the nonce for this account from 0 to 1.

An account leaf occupies 8 rows. Thus, in our example, where there is only one account in the trie,
our circuit will only have 8 rows.

The witness for our proof looks like (excluding selector columns):

```
[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[0,0,0,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[184,70,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,248,68,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[184,70,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,248,68,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]

[0,160,86,232,31,23,27,204,85,166,255,131,69,230,146,192,248,110,91,72,224,27,153,108,173,192,1,98,47,181,227,99,180,33,0,160,197,210,70,1,134,247,35,60,146,126,125,178,220,199,3,192,229,0,182,83,202,130,39,59,123,250,216,4,93,133,164,122]

[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```

The rows are:
```
ACCOUNT_LEAF_KEY_S
ACCOUNT_LEAF_KEY_C
ACCOUNT_NON_EXISTING
ACCOUNT_LEAF_NONCE_BALANCE_S
ACCOUNT_LEAF_NONCE_BALANCE_C
ACCOUNT_LEAF_STORAGE_CODEHASH_S
ACCOUNT_LEAF_STORAGE_CODEHASH_C
ACCOUNT_DRIFTED_LEAF
```

In `ACCOUNT_LEAF_NONCE_BALANCE_S` row, there is `S` nonce stored in `s_main`
and `S` balance in `c_main`. We can see nonce in `S` proof is `0 = 128 - 128`.

In `ACCOUNT_LEAF_NONCE_BALANCE_C` row, there is `C` nonce stored in `s_main`
and `C` balance in `c_main`. We can see nonce in `C` proof is `1`.

The two main things the circuit needs to check are:
 * Everything is the same in `S` and `C`, except the nonce value.
 * The change occurs at the proper account address.

However, there are many other things to be checked, for example the RLP encoding and RLC accumulators.
The RLC accumulators are used to compute the RLC of the whole node, in this particular case the RLC of
the account leaf. As the account leaf is distributed over multiple rows, we need to compute
the intermediate RLC in each row. That means we compute the RLC after the first row, then starts
with this value in the second row, compute the RLC after the second row:

```
account_s_rlc = account_leaf_key_s_rlc + account_leaf_nonce_balance_s_rlc * mult1 + account_leaf_storage_codehash_s_rlc * mult2
```

Note that `mult1` and `mult2` depend on the number of bytes in `account_leaf_key_s` and
`account_leaf_nonce_balance_s` bytes respectively. The RLC computed after the last row
and the RLC of the state trie hash (we only have this account in the trie) need
to be in the keccak table in the same row.

When we check that the computed account address is the same as the given address where the change
should occur, all address nibles are in the account leaf (no nibbles used in the branches as there
are no branches).
We can see this in the `ACCOUNT_LEAF_KEY_S` row:

```
[248,106,161,32,252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```

There are `33 = 161 - 128` bytes that store the nibbles. The value 32 does not hold any nibble
(this is how nibbles are compressed in case of even nibbles), but then we have 32 bytes that
store the nibbles:
```
[252,237,52,8,133,130,180,167,143,97,28,115,102,25,94,62,148,249,8,6,55,244,16,75,187,208,208,127,251,120,61,73]
```

Each of these bytes stores two nibbles. The address is computed as:
```
address_rlc = 252 + 237 * r + ... + 73 * r^31
```