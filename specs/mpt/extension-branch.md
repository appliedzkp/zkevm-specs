# Branch

A branch consists of 21 rows. The enumerator with the branch row types is `ExtensionBranchRowType`:

```
pub(crate) enum ExtensionBranchRowType {
    Mod,
    Child0,
    Child1,
    Child2,
    Child3,
    Child4,
    Child5,
    Child6,
    Child7,
    Child8,
    Child9,
    Child10,
    Child11,
    Child12,
    Child13,
    Child14,
    Child15,
    Key, // Both (S and C) extension nodes have the same key - when it is different, we have a modified extension node case.
    ValueS,
    Nibbles, // The list of second nibbles (key byte = nibble1 * 16 + nibble2) that correspond to the key.
    ValueC,
    Count,
}
```

`S` and `C` branches have the same children except for the one at the index `modified_node`.
The witness stores the 16 `S` children in `Child1`, ..., `Child15` rows and stores at `Mod` row
the children of the `C` branch where the modification occurs (child of `C` proof at index `modified_node`).

The rows `Key`, `ValueS`, `Nibbles`, and `ValueC` are used only when the branch is an extension node.

The circuit handles extension node as a special case branch - branch
with a path elongated by one or more nibbles.
An example of the extension node returned by `get_Proof`:
```
[226 24 160 194 200 39 82 205 97 69 91 92 98 218 180 101 42 171 150 75 251 147 154 59 215 26 164 201 90 199 185 190 205 167 64]
```

The first byte (`226`) represents the length of the RLP stream (`226 - 192 = 34`). The second byte represents the nibble - (only one
nibble in that case:  `24 - 16 = 8`).

The byte `160` represents the length (`32 = 160 - 128`) of the RLP substream that represents the hash of the branch.

To preserve the branch layout in the case of extension nodes, the branch
witness contains the extension node rows with information about
nibbles (`Key` row), `S` branch hash (`ValueS` row), `C` branch hash (`ValueC` row), and second nibbles (`Nibbles`).

The witness for the second nibbles is necessary for the cases as below:
```
[228, 130, 16 + 3, 9*16 + 5, 0, ...]
```
In this case, there are three nibbles: `3`, `9`, `5`. With
the knowledge of the second nibble `5`, the circuit can compute
the first nibble `9`.

Note that in some cases the number of nibbles is different in `S` and
`C` proofs. These cases are handles by
[`ModExtensionGadget`](mod_extension.md).


`ExtensionBranchConfig` is an abstraction of the extension nodes and branches. It contains information whether the branch:
 * is a placeholder (`is_placeholder`): at most one of the two branches (`S` and `C`) is a placeholder,
 * is an extension (`is_extension`): both branches are extension nodes or none.

`ExtensionBranchConfig` uses `ExtensionGadget` and `BranchGadget` to compute the intermediate values for the key RLC, the key multiplier,
the key parity, the number of nibbles after the branch (in both cases - in the case of the extension node, the intermediate values after the underlying branch
are computed).

Extension node and branch specific constraints are implemented in [`ExtensionGadget`](extension-node.md) and
[`BranchGadget`](branch.md) respectively.

## ExtensionBranchConfig

```
pub(crate) struct ExtensionBranchConfig<F> {
    key_data: KeyData<F>,
    parent_data: [ParentData<F>; 2],
    is_placeholder: [Cell<F>; 2],
    is_extension: Cell<F>,
    extension: ExtensionGadget<F>,
    branch: BranchGadget<F>,
}
```

It needs to be checked that the cells for `is_placeholder` and `is_extension` contain boolean values.

It needs to be checked that at most one branch (either in `S` or `C` proof or none) is a placeholder:

```
require!(config.is_placeholder[true.idx()].expr() + config.is_placeholder[false.idx()].expr() => bool);
```

The post state after the extension node (considering only the extension node nibbles, not its branch) is computed:

```
let (
    num_nibbles,
    is_key_odd,
    key_rlc_post_ext,
    key_mult_post_ext,
    is_root_s,
    is_root_c,
    parent_word_s_lo,
    parent_word_s_hi,
    parent_word_c_lo,
    parent_word_c_hi,
    parent_rlc_s,
    parent_rlc_c,
) = ifx! {config.is_extension => {
    config.extension = ExtensionGadget::configure(
        meta,
        cb,
        ctx.clone(),
        &config.key_data,
        &config.parent_data,
        &config.is_placeholder,
    );
    let ext = config.extension.get_post_state();
    (
        ext.num_nibbles,
        ext.is_key_odd,
        ext.key_rlc,
        ext.key_mult,
        false.expr(),
        false.expr(),
        ext.branch_rlp_word[true.idx()].lo(),
        ext.branch_rlp_word[true.idx()].hi(),
        ext.branch_rlp_word[false.idx()].lo(),
        ext.branch_rlp_word[false.idx()].hi(),
        ext.branch_rlp_rlc[true.idx()].expr(),
        ext.branch_rlp_rlc[false.idx()].expr(),
    )
} elsex {
    (
        config.key_data.num_nibbles.expr(),
        config.key_data.is_odd.expr(),
        config.key_data.rlc.expr(),
        config.key_data.mult.expr(),
        config.parent_data[true.idx()].is_root.expr(),
        config.parent_data[false.idx()].is_root.expr(),
        config.parent_data[true.idx()].hash.lo().expr(),
        config.parent_data[true.idx()].hash.hi().expr(),
        config.parent_data[false.idx()].hash.lo().expr(),
        config.parent_data[false.idx()].hash.hi().expr(),
        config.parent_data[true.idx()].rlc.expr(),
        config.parent_data[false.idx()].rlc.expr(),
    )
}};
```

That means the number of nibbles is computed (the total number of nibbles used in the path so far). Note that when the leaf is reached, the number of nibbles combined
with the leaf nibbles needs to be `64`. The `ExtensionGadget` simply adds the number of the extension node nibbles to the current `num_nibbles` value.

The key parity `is_key_odd` is computed - if the number of nibbles in the extension node is even, the parity does not change.

The key RLC is computed - the extension node nibbles are added to the `key_rlc` value.

The parent word and RLC are computed - these values contain the information about the modified node (in the next level, the node will be checked against this value.

Note that if the node is a regular branch (and not extension node), this values are not computed in the `ExtensionGadget`, instead they are taken from
[`KeyData`](main.md) and [`ParentData`](main.md) (nothing has changed because there was no extension node and thus no extension node nibbles).

`BranchGadget` computes the post state after the branch (in both cases, in the extension node and regular branch). That means the `num_nibbles` value is increased
by `1`, the value `is_key_odd` is switched, the `key_rlc` value is updated with the branch `modified_index`. The `parent_word` and `parent_rlc` contain the information
about the modified child in the branch.

Finally, the values in the key and parent data store are updated:
```
KeyData::store(
    cb,
    &mut ctx.memory[key_memory(is_s)],
    branch.key_rlc_post_branch.expr(),
    branch.key_mult_post_branch.expr(),
    branch.num_nibbles.expr(),
    branch.is_key_odd.expr(),
    branch.key_rlc_post_drifted.expr(),
    0.expr(),
    0.expr(),
    false.expr(),
);
ParentData::store(
    cb,
    &mut ctx.memory[parent_memory(is_s)],
    branch.mod_word[is_s.idx()].clone(),
    branch.mod_rlc[is_s.idx()].expr(),
    false.expr(),
    false.expr(),
    Word::<Expression<F>>::new([0.expr(), 0.expr()])
);
```





