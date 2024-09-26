## MainRLPGadget

To verify the RLP encoding, MPT circuit uses `MainRLPGadget`:
```
pub struct MainRLPGadget<F> {
    bytes: Vec<Cell<F>>,
    rlp: RLPItemGadget<F>,
    num_bytes: Cell<F>,
    len: Cell<F>,
    mult_diff: Cell<F>,
    rlc_content: Cell<F>,
    rlc_rlp: Cell<F>,
    tag: Cell<F>,
}
```

The field `rlp` is of type `RLPItemGadget`:

```
pub(crate) struct RLPItemGadget<F> {
    pub(crate) value: RLPValueGadget<F>,
    pub(crate) list: RLPListGadget<F>,
}
```

`RLPItemGadget` is an abstraction over two types of the RLP item.
An RLP item is either a string (i.e. byte array) or a list of items.
The abstraction provides functions `is_short`, `is_long`, `is_very_long` that gives
information on the type of the stream - whether the number of RLP bytes is short or long.

Furthermore, it provides functions `num_rlp_bytes`, `num_bytes`, `len` that gives information
about the number of RLP bytes, number of bytes in total (including RLP bytes), and
length of value (excluding RLP bytes) respectively.

Finally, it provides functions `rlc_rlp` and `rlc_content` which provide the RLC of the whole
stream (including RLP bytes) and the RLC of the values (excluding RLP values) respectively.

The cells which store information such as `is_short` and `is_long` are ensured to correspond to the
RLP byte by using lookups. There is a fixed table (with tag `FixedTableTag::RLP`) which contains the valid
options for RLP byte and `is_list`, `is_short`, `is_long`, `is_very_long` fields.
The table is loaded like (see `mpt_circuit.rs`):

```
let (is_list, is_short, is_long, is_very_long) = decode_rlp(byte);
assignf!(region, (self.fixed_table[0], offset) => FixedTableTag::RLP.scalar())?;
assignf!(region, (self.fixed_table[1], offset) => byte.scalar())?;
assignf!(region, (self.fixed_table[2], offset) => is_list.scalar())?;
assignf!(region, (self.fixed_table[3], offset) => is_short.scalar())?;
assignf!(region, (self.fixed_table[4], offset) => is_long.scalar())?;
assignf!(region, (self.fixed_table[5], offset) => is_very_long.scalar())?;
```

Both, `RLPValueGadget` and `RLPListGadget` execute the lookup to ensure that the cells have the proper
values.

The MPT circuit instantiates the `RLPItemGadget` for each RLP item in the MPT proof.
The assignment code is in the main `assign` function in `mpt_circuit.rs`:

```
for (idx, (bytes, item_type)) in node.values.iter().zip(item_types.iter()).enumerate() {
    cached_region.push_region(offset + idx, MPTRegion::RLP as usize);
    let rlp_value = self.rlp_item.assign(
        &mut cached_region,
        offset + idx,
        bytes,
        *item_type,
    )?;
    rlp_values.push(rlp_value);
    cached_region.pop_region();
}
```

Each node has a list of values (for example branch children in branch node) and each value is an
RLP item.

Note that the `item_type` specifies one of the following types:

```
pub enum RlpItemType {
    /// Node (string with len == 0 or 32, OR list with len <= 31)
    Node,
    /// Value (string with len <= 32)
    Value,
    /// Hash (string with len == 32)
    Hash,
    /// Key (string with len <= 33)
    Key,
    /// Nibbles
    Nibbles,
}
```

The constraints are triggered by using the `rlp_item` function as for example in `extension.rs`:

```
ctx.rlp_item(
    meta,
    cb,
    ExtensionBranchRowType::Key as usize,
    RlpItemType::Key,
),
```

The third parameter specified the rotation (in the list of node's values), the fourth parameter
specifies the item type.

### Constraints

`MainRLPGadget` ensures that the values stored in the cells `num_bytes`, `len`, `mult_diff`,
`rlc_content`, `rlc_rlp`, `tag` correspond to the bytes stored in `bytes`.

`MainRLPGadget` uses `RLPItemGadget` (via `rlp` field) to verify that the cell values correct:
```
config.num_bytes == config.rlp.num_bytes()
config.len => config.rlp.len()
config.rlc_content = config.rlp.rlc_content(r) // r is randomness used to compute the RLC
config.rlc_rlp = config.rlp.rlc_rlp(cb, r)
let mult_diff = config.mult_diff.expr();
(FixedTableTag::RMult, config.rlp.num_bytes(), mult_diff) in @FIXED
```

## IsEmptyTreeGadget

`IsEmptyTreeGadget` returns `1` when the trie is empty or when there is `0` at the modified position
in the branch (meaning there is no child at this position).

```
pub struct IsEmptyTreeGadget<F> {
    is_in_empty_trie: IsEqualGadget<F>,
    is_in_empty_branch: IsEqualGadget<F>,
}
```

We can use `IsEmptyTreeGadget` to check whether the (account / storage) leaf exists. Note that the gadget
is to be used only in the context of a leaf as it uses `parent_data.rlc` to execute the checks:

```
let is_in_empty_trie =
    IsEqualGadget::construct(&mut cb.base, parent_rlc.expr(), empty_root_rlc.expr());
let is_in_empty_branch =
    IsEqualGadget::construct(&mut cb.base, parent_rlc.expr(), 0.expr());
```

## DriftedGadget

`DriftedGadget` handles the leaf being moved from one branch to a newly created branch.

Sometimes `S` and `C` proofs are not of the same length. For example, when a new account `A1` is added,
the following scenario might happen. Let us say that the account that is being added has the address
(in nibbles):
``` 
[8, 15, 1, ...]
``` 

And let us say there already exists an account `A` with the following nibbles:
```
[8, 15, 3, ...]
```

Also, let us assume that the account `A` is in the third trie level. We have `Branch0` in the first level:
```
           Branch0
Node_0_0 Node_0_1 ... Node_0_15
```

`Node_0_8` is the hash of a branch `Branch1`:
```
           Branch1
Node_1_0 Node_1_1 ... Node_1_15
```

`Node_1_15` is the hash of the account `A`.

So we have:
```
                              Branch0
Node_0_0 Node_0_1 ...              Node_0_8                 ... Node_0_15
                                      |
                        Node_1_0 Node_1_1 ... Node_1_15
                                                  |
                                                  A
```

Before we add the account `A1`, we first obtain the `S` proof which will contain the account `A` as a leaf
because the first part of the address `[8, 15]` is the same and when going down the trie retrieving
the elements of a proof, the algorithm arrives to the account `A`.

When we add the account `A1`, it cannot be placed at position 15 in `Branch1` because it is already
occupied by the account `A`. For this reason, a new branch `Branch2` is added.
Now, the third nibble of the accounts `A` and `A1` is considered. The account `A` drifts into a new branch
to position 3, while the account `A1` is placed at position 1 in `Branch2`.

Thus, the `C` proof has one element more than the `S` proof (the difference is due to `Branch2`).

```
S proof              || C proof
Branch0              || Branch0
Branch1              || Branch1
(Placeholder branch) || Branch2
A                    || A1
```

Note that the scenario is reversed (`S` and `C` are turned around) when a leaf is deleted
from the branch with exactly two leaves.

To preserve the parallel layout, the circuit uses a placeholder branch that occupies the columns
in `S` proof parallel to `Branch2`.

Having a parallel layout is beneficial for multiple reasons, for example having the layout as below
would cause problems with selectors such as `is_branch_child` as there would be account and branch
in the same row. Also, it would make the lookups more complicated as it is much easier to enable
a lookup if accounts `A` and `A1` are in the same row. Non-parallel layout:

```
S proof              || C proof
Branch0              || Branch0
Branch1              || Branch1
A                    || Branch2
                     || A1
```

We need to include the account `A` that drifted into `Branch2` in the `C` proof too. This is because
we need to check that `Branch2` contains exactly two leaves: `A1` and `A` after it moved down from
`Branch1`. We need to also check that the account `A` in `S` proof (in `Branch1`) differs 
from the account `A` in `C` proof (in `Branch2`) in exactly one key nibble (this is different
if an extension node is added instead of a branch), everything else stays the same (the value
stored in the leaf).

An example of `getProof` output where `S` proof have two elements (branch and account leaf):

```
[248 241 160 255 151 217 75 103 5 122 115 224 137 233 146 50 189 95 178 178 247 44 237 22 101 231 39 198 40 14 249 60 251 151 15 128 128 128 128 160 60 79 85 51 115 192 158 157 93 223 211 100 62 94 72 146 251 82 116 111 190 139 246 12 252 146 211 122 66 110 206 20 128 160 120 190 160 200 253 109 255 226 49 189 87 112 136 160 23 77 119 59 173 185 188 145 251 156 155 144 100 217 100 114 109 106 128 160 69 72 113 186 79 146 63 86 46 218 1 200 131 76 71 142 217 35 30 209 101 239 91 47 163 221 136 130 249 155 236 112 160 49 65 26 94 193 156 227 78 42 198 56 211 105 254 0 33 31 96 41 208 40 13 215 156 51 173 132 112 34 192 121 49 160 244 154 252 18 232 96 245 36 84 15 253 182 157 226 247 165 106 144 166 1 2 140 228 170 110 87 112 80 140 149 162 43 128 160 20 103 6 95 163 140 21 238 207 84 226 60 134 0 183 217 11 213 185 123 139 201 37 22 227 234 220 30 160 20 244 115 128 128 128]
[248 102 157 55 236 125 29 155 142 209 241 75 145 144 143 254 65 81 209 56 13 192 157 236 195 213 73 132 11 251 149 241 184 70 248 68 1 128 160 112 158 181 221 162 20 124 79 184 25 162 13 167 162 146 25 237 242 59 120 184 154 118 137 92 181 187 152 115 82 223 48 160 7 190 1 231 231 32 111 227 30 206 233 26 215 93 173 166 90 214 186 67 58 230 71 161 185 51 4 105 247 198 103 124]
```

An example of `getProof` output where `C` proof have three elements (branch, added branch, and account leaf):

```
[248 241 160 188 253 144 87 144 251 204 78 148 203 12 141 0 77 176 70 67 92 90 100 110 40 255 28 218 97 116 184 26 121 18 49 128 128 128 128 160 60 79 85 51 115 192 158 157 93 223 211 100 62 94 72 146 251 82 116 111 190 139 246 12 252 146 211 122 66 110 206 20 128 160 120 190 160 200 253 109 255 226 49 189 87 112 136 160 23 77 119 59 173 185 188 145 251 156 155 144 100 217 100 114 109 106 128 160 69 72 113 186 79 146 63 86 46 218 1 200 131 76 71 142 217 35 30 209 101 239 91 47 163 221 136 130 249 155 236 112 160 49 65 26 94 193 156 227 78 42 198 56 211 105 254 0 33 31 96 41 208 40 13 215 156 51 173 132 112 34 192 121 49 160 244 154 252 18 232 96 245 36 84 15 253 182 157 226 247 165 106 144 166 1 2 140 228 170 110 87 112 80 140 149 162 43 128 160 20 103 6 95 163 140 21 238 207 84 226 60 134 0 183 217 11 213 185 123 139 201 37 22 227 234 220 30 160 20 244 115 128 128 128]
[248 81 128 128 128 128 128 128 128 160 222 45 71 217 199 68 20 55 244 206 68 197 49 191 78 208 106 209 111 87 254 9 221 230 148 86 131 219 7 121 62 140 160 190 214 56 80 83 126 135 17 104 48 181 30 249 223 80 59 155 70 206 67 24 6 82 98 81 246 212 143 253 181 15 180 128 128 128 128 128 128 128 128]
[248 102 157 32 133 130 180 167 143 97 28 115 102 25 94 62 148 249 8 6 55 244 16 75 187 208 208 127 251 120 61 73 184 70 248 68 1 23 160 112 158 181 221 162 20 124 79 184 25 162 13 167 162 146 25 237 242 59 120 184 154 118 137 92 181 187 152 115 82 223 48 160 7 190 1 231 231 32 111 227 30 206 233 26 215 93 173 166 90 214 186 67 58 230 71 161 185 51 4 105 247 198 103 124]
```

We can observe that there is a difference of one nibble in the key. In the first proof, the nibbles
are compressed as: `[55, 236, 125, ...]`. In the second proof, the nibbles are compressed as:
`[32, 133, 130, ...]`. The difference is that in the first row there is a first nibble `7 = 55 - 48`.
This nibble is not present in the account `A` when moved down into `Branch2` because `7` is the position
where the account `A` is placed in `Branch2`.

`DriftedGadget` contains a field `drifted_rlp_key`: `ListKeyGadget` which stores the key of the drifted
leaf.

```
pub struct DriftedGadget<F> {
    drifted_rlp_key: ListKeyGadget<F>,
}
```

The `DriftedGadget` constructor is given below:

```
pub(crate) fn construct(
    cb: &mut MPTConstraintBuilder<F>,
    parent_data: &[ParentData<F>],
    key_data: &[KeyData<F>],
    expected_key_rlc: &[Expression<F>],
    leaf_no_key_rlc: &[Expression<F>],
    drifted_item: &RLPItemView<F>,
    r: &Expression<F>,
)
```

### Constraints

The key RLC of the drifted leaf needs to be the same as the key RLC of the leaf before it drifted. The leaf
before the drift has more nibbles in the leaf key bytes, while these nibbles move to the path to the leaf for
the leaf after the drift:
```
key_rlc = expected_key_rlc
```

The total number of nibbles needs to be `64`. The value `key_num_nibbles` is obtained from `key_data` and
`num_nibbles` is the number of nibbles in the drifted leaf key:
```
key_num_nibbles + num_nibbles = 64
```

Complete the drifted leaf rlc by adding the bytes on the value row
The drifted leaf needs to be in the newly created branch (at `drifted_index`). The value `leaf_rlc` is
computed using the drifted leaf key and the value RLC (`leaf_no_key_rlc`):
```
((1, leaf_rlc, config.drifted_rlp_key.rlp_list.num_bytes(), parent_data[is_s.idx()].drifted_parent_rlc.expr()) in @KECCAK)
```

## WrongGadget

`WrongGadget` is used to prove that there is no leaf at the specified address (for an account leaf)
or key (for storage leaf).

When proving there is no leaf, there are two proof types:
    1. A leaf is returned by `getProof` that is not at the required address (we call this a wrong leaf).
    This happens when traversing through branches and there is a leaf in the last branch at the same nibble
    as the nibble in the required address, but the following nibbles are different - adding a leaf at this
    position would result in having a new branch with the old (wrong) leaf and the newly added.
    2. A branch is the last element of `getProof` response and there is a nil object
    at the next nibble (placeholder leaf is added).
    `WrongGadget` is not needed in this case.
    We just need to prove that the branch contains nil object at the enquired address.

`WrongGadget` constructor takes the following fields:
```
pub(crate) fn construct(
    cb: &mut MPTConstraintBuilder<F>,
    expected_address: Expression<F>,
    is_non_existing: Expression<F>,
    key_value: &RLPItemView<F>,
    key_rlc: &Expression<F>,
    wrong_item: &RLPItemView<F>,
    is_in_empty_tree: Expression<F>,
    key_data: KeyData<F>,
    r: &Expression<F>,
)
```

### Constraints

The `wrong_item` field holds the address / key (the nibbles that remain
after the nibbles used for traversing through the branches are removed) that was enquired.
The `expected_address` field contains the RLC of the address that was enquired.

The value `key_rlc_wrong` is computed using `key_data.rlc` and `wrong_item`.
It needs to be the same as the required address:
```
key_rlc_wrong = expected_address
```

The field `key_rlc` contains the key RLC of the (wrong) leaf that was returned by `getProof`.
It needs to be different than the expected address. For this reason, `IsEqualGadget is instantiated:
```
config.is_key_equal = IsEqualGadget::construct(
    &mut cb.base,
    key_rlc.expr(),
    expected_address,
);
```

And the constraint should ensure that the two addresses are different:
```
config.is_key_equal = false
```

Finally, it needs to be ensured that the lengths of the wrong address and the enquired address
are the same:
```
config.wrong_rlp_key.key_value.len() = key_value.len()
```

## RLPValueGadget and RLPListGadget

The RLP item can be a value or a list of items. For the value RLP item, the `RLPValueGadget`
is to be instantiated.

```
pub(crate) struct RLPValueGadget<F> {
    pub(crate) is_short: Cell<F>,
    pub(crate) is_long: Cell<F>,
    pub(crate) is_very_long: Cell<F>,
    pub(crate) is_list: Cell<F>,
    pub(crate) bytes: Vec<Expression<F>>,
}
```


The RLP item can be a value or a list of items. For the list of the RLP items, the `RLPListGadget`
is to be instantiated.

```
pub(crate) struct RLPListGadget<F> {
    pub(crate) is_short: Cell<F>,
    pub(crate) is_long: Cell<F>,
    pub(crate) is_very_long: Cell<F>,
    pub(crate) is_string: Cell<F>,
    pub(crate) bytes: Vec<Expression<F>>,
}
```

The two gadgets ensure that the `is_short`, `is_long`, `is_very_long` fields are correctly assigned.
These values are used to compute the RLP item properties like the length and the random linear
combination of all the bytes in the item.

## ListKeyGadget

```
pub(crate) struct ListKeyGadget<F> {
    pub(crate) rlp_list_bytes: [Cell<F>; 3],
    pub(crate) rlp_list: RLPListGadget<F>,
    pub(crate) key_value: RLPItemView<F>,
    pub(crate) key: LeafKeyGadget<F>,
}
```

`ListKeyGadget` is used for the account leaf, storage leaf, and extension node - it is used to check the key part (without
leaf value).
In these cases, the RLP item is always a list (hence the name), because the RLP stream contains multiple elements:
the key and the value. However, note that the value part is not checked in this gadget, in fact `key_value` contains
the actual leaf key and it is checked by `key: LeafKeyGadget`.

For example, the RLC of the whole leaf is computed by concatenating the RLC obtained from `ListKeyGadget` and the RLC of the
leaf value (see `account_leaf.rs`):
```
// Calculate the key RLC
let rlp_key = &mut config.rlp_key[is_s.idx()];
*rlp_key = ListKeyGadget::construct(cb, &key_items[is_s.idx()]);

let leaf_rlc = rlp_key.rlc2(&cb.keccak_r).rlc_chain_rev((
    leaf_no_key_rlc[is_s.idx()].expr(),
    leaf_no_key_rlc_mult[is_s.idx()].expr(),
));
```

The field `rlp_list_bytes` contains the bytes that specify the length of the (list) RLP item.

For example, let us observe the storage leaf below.
```
[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68]
```

The field `rlp_list_bytes` would be `[[226],[226]]`. Note that it contains the byte for each, `S`
and `C` leaf.

For example, the following constraint (in `extension.rs`) ensures that the lengths in the RLP encoding are
consistent:
```
require!(config.rlp_key.rlp_list.len() => config.rlp_key.key_value.num_bytes() + rlp_value[is_s.idx()].num_bytes());
```

Above, the `config.rlp_key` is of type `ListKeyGadget` - it contains information about the leaf
key. The `config.rlp_key.key_value` and `rlp_value` are of type `RLPItemView` - instantiated by
the call `rlp_item` (see above). The constraint checks whether the length of the key RLP stream (the whole length obtained from
the `ListKeyGadget`) is the sum of the length of the key and the length of the value. 

## IsPlaceholderLeafGadget

`IsPlaceholderLeafGadget` is used to check whether the leaf is a placeholder.
The placeholder leaf is used in the following scenarios:
 * When the leaf has been added to the position in branch where there was no leaf - in this case `S` proof contains a placeholder leaf.
 * When the leaf has been deleted from the branch and there is at least one other leaf in the branch (otherwise the branch is deleted) - in this case `C` proof constains a placeholder leaf.
 * For the non-existence proofs (however, some non-existence proofs have a leaf - wrong leaf, see `WrongGadget`).

To determine whether the leaf is placeholder or not, the gadget checks
whether `ParentData hash` is a hash of an empty trie (when no leaf is in the trie):
```
let is_empty_trie = IsEqualWordGadget::construct(
    &mut cb.base,
    &parent_word,
    &Word::<Expression<F>>::new([
        Expression::Constant(empty_hash.lo()),
        Expression::Constant(empty_hash.hi()),
    ]),
);
```

or whether `ParentData hash` is `nil`, meaning there is no leaf at the `modified_index` position in the parent branch: 
```
let is_nil_in_branch_at_mod_index = IsEqualWordGadget::construct(
    &mut cb.base,
    &parent_word,
    &Word::<Expression<F>>::new([0.expr(), 0.expr()]),
);
```

