# Obsolete (to be updated)

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
[`]

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


```
require!(config.is_placeholder[true.idx()].expr() + config.is_placeholder[false.idx()].expr() => bool);
```




# Obsolete

A branch occupies 19 rows:
```
BRANCH.IS_INIT
BRANCH.IS_CHILD 0
...
BRANCH.IS_CHILD 15
BRANCH.IS_EXTENSION_NODE_S
BRANCH.IS_EXTENSION_NODE_C
```

Example:

```
[1 0 1 0 248 241 0 248 241 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 164 92 78 34 81 137 173 236 78 208 145 118 128 60 46 5 176 8 229 165 42 222 110 4 252 228 93 243 26 160 241 85 0 160 95 174 59 239 229 74 221 53 227 115 207 137 94 29 119 126 56 209 55 198 212 179 38 213 219 36 111 62 46 43 176 168 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 1]
[0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 1]
[0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 1]
[0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 16]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 17]
```
The witness data for branch contains 16 children which are distributed across 16 rows.
There is an additional branch init row and two extension node rows (for cases when branch resides
in an extension node).

Branch rows:
```
Branch init
Branch child 0
...
Branch child 15
Extension node S
Extension node C
```

The branch does not include raw children, it includes only a hash of each children (except
when a child is shorter than 32 bytes, in this case the raw child is part of a branch).

When non-empty node, the branch child row looks like:
```
160  hash(child i)
```

The value 160 is RLP specific and it means the the following RLP string is of length `128 = 160 - 32`.

When empty node, the branch child row looks like:
```
128 0 ... 0
```

In case there is a branch child of length smaller than 32, its corresponding row looks like:
```
194 32 1 0 ... 0
```

The value 194 is RLP specific and it means that the following RLP list is of length
`2 = 194 - 192`.

Note [that](main.md) there are `S` and `C` parallel proofs, however
we do not need to include the whole `C` proof in the witness as 15 out of 16 rows stay the same.
At each trie level, there is only one branch child that has been modified and we include it
in the branch init row.

---


Note that when `BRANCH.IS_CHILD` row presents a nil node, there is only one byte non-zero:
128 at `s_main.bytes[0] / c_main.bytes[0]`.

## Branch

### Branch S and C equal at NON modified_node position & only two non-nil nodes when placeholder

The gate
`Branch S and C equal at NON modified_node position & only two non-nil nodes when placeholder`
ensures that the only change in
`S` and `C` proof occur at `modified_node` (denoting which child of the branch is changed) position.
This is needed because the circuit allows only one change at at time. 

#### rlp2

We check `s_main.rlp2 = c_main.rlp2` everywhere except at `modified_node`.

Note: We do not compare `s_main.rlp1 = c_main.rlp1` because there is no information
about branch. We use `rlp1` to store information about `S` branch and
`C` branch RLP length (see the gate below).

#### s = c when NOT is_modified

Similarly as above for `rlp2` we check here that `s_main.bytes[i] = c_main.bytes[i]`
except at `modified_node`.

#### Only two nil-nodes when placeholder branch
 
 This constraint applies for when we have a placeholder branch.
In this case, both branches are the same - the placeholder branch and its
parallel counterpart, which is not a placeholder, but a regular branch (newly added branch).
The regular branch has only two non-nil nodes, because the placeholder branch
appears only when an existing leaf drifts down into a newly added branch.
Besides an existing leaf, we have a leaf that was being added and that caused
a new branch to be added. So we need to check that there are exactly two non-nil nodes
(otherwise the attacker could add two or more new leaves at the same time).

The non-nil nodes need to be at `is_modified` and `is_at_drifted_pos`, elsewhere
there have to be zeros. When there is no placeholder branch, this constraint is ignored.

### RLP length

We need to check that the length of the branch corresponds to the bytes at the beginning of
the RLP stream that specify the length of the RLP stream. There are three possible scenarios:

  1. Branch (length `21 = 213 - 192`) with one byte of RLP meta data
     ```
     [213,128,194,32,1,128,194,32,1,128,128,128,128,128,128,128,128,128,128,128,128,128]
     ```

  2. Branch (length 83) with two bytes of RLP meta data
     ```
     [248,81,128,128,...
     ```

  3. Branch (length 340) with three bytes of RLP meta data
     ```
     249,1,81,128,16,...
     ```

We specify which of the scenarios is in the current row as (note that `S` branch and
`C` branch could be of different length. `s_rlp1, s_rlp2` is used for `S` and
`s_main.bytes[0], s_main.bytes[1]` is used for `C`):
```
rlp1, rlp2: 1, 1 means 1 RLP byte
rlp1, rlp2: 1, 0 means 2 RLP bytes
rlp1, rlp2: 0, 1 means 3 RLP bytes
```

#### Not both zeros: rlp1, rlp2

There should never be `rlp1, rlp2: 0, 0` for `S` (we only have three cases, there is no case with
both being 0).

#### First branch children one RLP meta byte

We check that the first branch children has properly stored the number of the remaining
bytes. For example, if there are 81 bytes in the branch and the first branch child
contains 1 byte, then it needs to store the value `80 = 81 - 1`.

#### Branch children node_index > 0 RLP

We check that the non-first branch children has properly stored the number of the remaining
bytes. For example, if there are 81 bytes in the branch, the first branch child
contains 1 byte, the second child contains 33 bytes, then the third child
needs to store the value `81 - 1 - 33`.

#### Branch last child RLP length

In the final branch child `s_rlp1` and `c_rlp1` need to be 1 (because RLP length
specifies also ValueNode which occupies 1 byte).

### Branch children selectors

#### is_branch_child after is_branch_init

If we have `is_branch_init` in the previous row, we have `is_branch_child = 1` in the current row.

#### node_index = 0 after is_branch_init

We could have only one constraint using sum, but then we would need
to limit `node_index` (to prevent values like -1). Now, `node_index` is
limited by ensuring its first value is 0, its last value is 15,
and it is being increased by 1.
If we have `is_branch_init` in the previous row, we have
`node_index = 0` in the current row.

#### Last branch child node_index

When `is_branch_child` changes back to 0, previous `node_index` needs to be 15.

#### is_last_child index

When `node_index` is not 15, `is_last_child` needs to be 0.

#### is_last_child when node_index = 15

When `node_index` is 15, `is_last_child` needs to be 1.

#### node_index increasing for branch children

`node_index` is increased by 1 for each is_branch_child node.

#### modified_node the same for all branch children

`modified_node` (the index of the branch child that is modified)
needs to be the same for all branch nodes.

#### drifted_pos the same for all branch children

`drifted_pos` (the index of the branch child that drifted down into a newly added branch)
needs to be the same for all branch nodes.

#### NOT is_branch_placeholder_s: s_mod_node_hash_rlc corresponds to s_main.bytes at modified pos

For a branch placeholder we do not have any constraints. However, in the parallel
(regular) branch we have an additional constraint (besides `is_modified` row
corresponding to `mod_nod_hash_rlc`) in this case: `is_at_drifted_pos main.bytes RLC`
is stored in the placeholder `mod_node_hash_rlc`. For example, if there is a placeholder
branch in `S` proof, we have:
* `is_modified c_main.bytes RLC = c_mod_node_hash_rlc`
* `is_at_drifted_pos c_main.bytes RLC = s_mod_node_hash_rlc`
That means we simply use `mod_node_hash_rlc` column (because it is not occupied)
in the placeholder branch for `is_at_drifted_pos main.bytes RLC` of
the regular parallel branch.

When `S` branch is NOT a placeholder, `s_main.bytes RLC` corresponds to the value
stored in `accumulators.s_mod_node_rlc` in `is_modified` row.

Note that `s_hash_rlc` is a bit misleading naming, because sometimes the branch
child is not hashed (shorter than 32 bytes), but in this case we need to compute
the RLC too - the same computation is used (stored in variable `s_hash_rlc`), but
we check in `branch_parallel` that the non-hashed child is of the appropriate length
(the length is specified by `rlp2`) and that there are 0s after the last branch child byte.
The same applies for `c_hash_rlc`.

#### is_branch_placeholder_s: s_mod_node_hash_rlc corresponds to c_main.bytes at drifted pos

When `S` branch is a placeholder, `c_main.bytes RLC` corresponds to the value
stored in `accumulators.s_mod_node_rlc` in `is_at_drifted_pos` row.

#### NOT is_branch_placeholder_c: c_mod_node_hash_rlc corresponds to c_main.bytes at modified pos

When `C` branch is NOT a placeholder, `c_main.bytes RLC` corresponds to the value
stored in `accumulators.c_mod_node_rlc` in `is_modified` row.

#### is_branch_placeholder_c: c_mod_node_hash_rlc corresponds to s_main.bytes at drifted pos

When `C` branch is a placeholder, `s_main.bytes RLC` corresponds to the value
stored in `accumulators.c_mod_node_rlc` in `is_at_drifted_pos` row.

#### is_modified = 1 only for modified node

`is_modified` is boolean (booleanity is checked in `selectors.rs`):
   * 0 when `node_index != modified_node`
   * 1 when `node_index == modified_node`

#### is_at_drifted_pos = 1 only for modified node

`is_at_drifted_pos` is boolean (booleanity is checked in `selectors.rs`):
   * 0 when `node_index != drifted_pos`
   * 1 when `node_index == drifted_pos`

### Branch placeholder selectors

#### Bool check is_branch_placeholder_s

`is_branch_placeholder_s` needs to be boolean.

#### Bool check is_branch_placeholder_c

`is_branch_placeholder_c` needs to be boolean.

#### Bool check is_branch_non_hashed_s

`is_branch_non_hashed_s` needs to be boolean.

#### Bool check is_branch_non_hashed_c

`is_branch_non_hashed_c` needs to be boolean.

### Branch number of nibbles (not first level)

The cell `s_main.bytes[NIBBLES_COUNTER_POS - RLP_NUM]` in branch init row stores the number of
nibbles used up to this point (up to this branch). If a regular branch, the counter increases only
by 1 as only one nibble is used to determine the position of `modified_node` in a branch.
On the contrary, when it is an extension node the counter increases by the number of nibbles
in the extension key and the additional nibble for the position in a branch (this constraint
is in `extension_node.rs` though).

### Branch number of nibbles (first level)

If we are in the first level of the trie, `nibbles_count` needs to be 1. 

#### nibbles_count first level account

If branch is in the first level of the account trie, `nibbles_count` needs to be 1.

#### nibbles_count first level storage

If branch is in the first level of the storage trie, `nibbles_count` needs to be 1.

### Range lookups

Range lookups ensure that `s_main.bytes` and `c_main.bytes` columns are all bytes (between 0 - 255).

Note: We do not check this for branch init row here.
Branch init row contains selectors related to drifted_pos,
modified_node, branch placeholders, extension node selectors. The constraints for these
selectors are in `branch_init.rs`.
Range lookups for extension node rows are in `extension_node_key.rs`.

## Branch hash in parent

A branch occupies 19 rows:
```
BRANCH.IS_INIT
BRANCH.IS_CHILD 0
...
BRANCH.IS_CHILD 15
BRANCH.IS_EXTENSION_NODE_S
BRANCH.IS_EXTENSION_NODE_C
```

Example:

```
[1 0 1 0 248 241 0 248 241 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 164 92 78 34 81 137 173 236 78 208 145 118 128 60 46 5 176 8 229 165 42 222 110 4 252 228 93 243 26 160 241 85 0 160 95 174 59 239 229 74 221 53 227 115 207 137 94 29 119 126 56 209 55 198 212 179 38 213 219 36 111 62 46 43 176 168 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 1]
[0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 1]
[0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 1]
[0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 16]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 17]
```

The constraints in this file check whether the RLC of the whole branch is in its parent node
at the proper position. The RLC is computed over the first 17 rows (the last 2 rows are reserved
for the cases when the parent of the branch is an extension node).

Let us say we have the following situation:

```
Branch1:
  node1_0       node3_0_RLC
  ...           node3_0_RLC
  node1_15      node3_0_RLC
Branch2
  node2_0
  ...
  node2_15
```

Let us say we are checking `Branch2` to be at the proper position in `Branch1`.
We compute `Branch2` RLC (the constraints for ensuring the proper RLC computation are in `branch_rlc.rs`).
Let us say the `modified_node = 3` in `Branch1`. That means there is `node3_0_RLC` stored in all 16
rows. We need to check that `(Branch2_RLC, node3_0_RLC)` is in the Keccak table which would mean
that `hash(Branch2) = node3_0`.

### Branch in first level of account trie - hash compared to root

When branch is in the first level of the account trie, we need to check whether
`hash(branch) = account_trie_root`. We do this by checking whether
`(branch_RLC, account_trie_root_RLC)` is in the Keccak table.

Note: branch in the first level cannot be shorter than 32 bytes (it is always hashed).

### Branch in first level of storage trie - hash compared to the storage root

When branch is in the first level of the storage trie, we need to check whether
`hash(branch) = storage_trie_root`. We do this by checking whether
`(branch_RLC, storage_trie_root_RLC)` is in the keccak table.

Note: branch in the first level cannot be shorter than 32 bytes (it is always hashed).

### Branch hash in parent branch

This is the scenario described at the top of the file.
When branch is in some other branch, we need to check whether
`hash(branch) = parent_branch_modified_node`. We do this by checking whether
`(branch_RLC, parent_branch_modified_node_RLC)` is in the Keccak table.

### NON-HASHED branch hash in parent branch

Similar as the gate above, but here the branch is not hashed.
Instead of checking `hash(branch) = parent_branch_modified_node`, we check whether
`branch_RLC = parent_branch_modified_node_RLC`.

## Branch init

A branch occupies 19 rows:
```
BRANCH.IS_INIT
BRANCH.IS_CHILD 0
...
BRANCH.IS_CHILD 15
BRANCH.IS_EXTENSION_NODE_S
BRANCH.IS_EXTENSION_NODE_C
```

Example:

```
[1 0 1 0 248 241 0 248 241 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 164 92 78 34 81 137 173 236 78 208 145 118 128 60 46 5 176 8 229 165 42 222 110 4 252 228 93 243 26 160 241 85 0 160 95 174 59 239 229 74 221 53 227 115 207 137 94 29 119 126 56 209 55 198 212 179 38 213 219 36 111 62 46 43 176 168 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 1]
[0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 1]
[0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 1]
[0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 16]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 17]
```

The constraints in `branch_init.rs` check whether the RLC of the branch init row (first branch row)
is computed correctly.

There are three possible cases:
1. Branch (length 21 = 213 - 192) with one byte of RLP meta data
    `[213,128,194,32,1,128,194,32,1,128,128,128,128,128,128,128,128,128,128,128,128,128]`
    In this case the init row looks like (specifying only for `S`, we put `x` for `C`):
    `[1,1,x,x,213,0,0,...]`
    The RLC is simply `213`.

2. Branch (length 83) with two bytes of RLP meta data
    `[248,81,128,128,...]`
    In this case the init row looks like (specifying only for `S`, we put `x` for `C`):
    `[1,0,x,x,248,81,0,...]`
    The RLC is `248 + 81*r`.


3. Branch (length 340) with three bytes of RLP meta data
    `[249,1,81,128,16,...]`
    In this case the init row looks like (specifying only for `S`, we put `x` for `C`):
    `[1,0,x,x,249,1,81,...]`
    The RLC is `249 + 1*r + 81*r^2`.

We specify the case as (note that `S` branch and
`C` branch can be of different length. `s_rlp1, s_rlp2` is used for `S` and
`s_main.bytes[0], s_main.bytes[1]` is used for `C`):
```
rlp1, rlp2: 1, 1 means 1 RLP byte
rlp1, rlp2: 1, 0 means 2 RLP bytes
rlp1, rlp2: 0, 1 means 3 RLP bytes
```

The example branch init above is the second case (two RLP meta bytes).

Note: the constraints for the selectors in branch init row to be boolean are in `branch.rs`
and `extension_node.rs`.

### Branch init RLC

The RLC of the init branch comprises 1, 2, or 3 bytes. This gate ensures the RLC
is computed properly in each of the three cases. It also ensures that the values
that specify the case are boolean.

### Range lookups

Range lookups ensure that the values in the used columns are all bytes (between 0 - 255).
Note: range lookups for extension node rows are in `extension_node_key.rs`.

## Branch key

The constraints in this `branch_key.rs` checks whether the key RLC is being properly
computed using `modified_node`. Note that `modified_node` presents the branch node
to be modified and is one of the nibbles of a key.

Let us have the following scenario:

```
Branch1:
  node1_0
  node1_1     <- modified_node
  ...
  node1_15
Branch2
  node2_0
  ...
  node2_7    <- modified_node
  ...
  node2_15
Branch3
  node3_0
  ...
  node3_5    <- modified_node
  ...
  node3_15
Branch4
  node4_0
  ...
  node4_11    <- modified_node
  ...
  node4_15
Leaf1
```

We have four branches and finally a leaf in the fourth branch. The modified nodes are: `1, 7, 5, 11`.
The modified nodes occupy two bytes, the remaining 30 bytes are stored in `Leaf1`:
`b_0, ..., b_29`.

The key at which the change occurs is thus: `1 * 16 + 7, 5 * 16 + 11, b_0, ..., b_29`.
The RLC of the key is: `(1 * 16 + 7) + (5 * 16 + 11) * r + b_0 * r^2 + b_29 * r^31`.

In each branch we check whether the intermediate RLC is computed correctly. The intermediate
values are stored in `accumulators.key`. There is always the actual RLC value and the multiplied
that is to be used when adding the next summand: `accumulators.key.rlc, accumulators.key.mult`.

For example, in `Branch1` we check whether the intermediate RLC is `1 * 16`.
In `Branch2`, we check whether the intermediate RLC is `rlc_prev_branch_init_row + 7`.
In `Branch3`, we check whether the intermediate RLC is `rlc_prev_branch_init_row + 5 * 16 * r`.
In `Branch4`, we check whether the intermediate RLC is `rlc_prev_branch_init_row + 11 * r`.

There are auxiliary columns `sel1` and `sel2` which specify whether we are in branch where
the nibble has to be multiplied by 16 or by 1. `sel1 = 1` means multiplying by 16,
`sel2 = 1` means multiplying by 1.

### Branch key RLC

#### Key RLC sel1 not first level

When we are not in the first level and when sel1, the intermediate key RLC needs to be
computed by adding `modified_node * 16 * mult_prev` to the previous intermediate key RLC.

#### Key RLC sel2 not first level

When we are not in the first level and when sel2, the intermediate key RLC needs to be
computed by adding `modified_node * mult_prev` to the previous intermediate key RLC.

#### Key RLC sel1 not first level mult
When we are not in the first level and when sel1, the intermediate key RLC mult needs to
stay the same - `modified_node` in the next branch will be multiplied by the same mult
when computing the intermediate key RLC.

#### Key RLC sel2 not first level mult

When we are not in the first level and when sel1, the intermediate key RLC mult needs to
be multiplied by `r` - `modified_node` in the next branch will be multiplied
by `mult * r`.

#### Account address RLC first level

In the first level, address RLC is simply `modified_node * 16`.

#### Account address RLC mult first level

In the first level, address RLC mult is simply 1.

#### Storage key RLC first level

In the first level, storage key RLC is simply `modified_node * 16`.

#### Storage key RLC first level mult

In the first level, storage key RLC mult is simply 1.

#### sel1, sel2

Selectors `sel1` and `sel2` need to be boolean and `sel1 + sel2 = 1`.

#### Account first level sel1 (regular branch)

`sel1` in the first level is 1.

#### Account first level sel1 = 1 (extension node even key)

`sel1/sel2` present with what multiplier (16 or 1) is to be multiplied
the `modified_node` in a branch, so when we have an extension node as a parent of
a branch, we need to take account the nibbles of the extension node.

If extension node, `sel1` and `sel2` in the first level depend on the extension key
(whether it is even or odd). If key is even, the constraints stay the same. If key
is odd, the constraints get turned around. Note that even/odd
presents the number of key nibbles (what we actually need here) and
not key byte length (how many bytes key occupies in RLP).

####  Account first level sel1 = 0 (extension node odd key)

`sel1/sel2` get turned around when odd number of nibbles. 

#### Storage first level sel1 = 1 (regular branch)

Similarly as for the account first level above.

#### Storage first level sel1 = 1 (extension node even key)

Similarly as for the account first level above (extension node even key).
               
#### Storage first level sel1 = 0 (extension node odd key)

Similarly as for the account first level above (extension node odd key).

#### sel1 0->1->0->...

`sel1` alernates between 0 and 1 for regular branches.
Note that `sel2` alternates implicitly because of `sel1 + sel2 = 1`.

#### sel1 0->1->0->... (extension node even key)

`sel1` alernates between 0 and 1 for extension nodes with even number of nibbles.

####  sel1 stays the same (extension node odd key)

`sel1` stays the same for extension nodes with odd number of nibbles.

## Branch parallel

```
A branch occupies 19 rows:
BRANCH.IS_INIT
BRANCH.IS_CHILD 0
...
BRANCH.IS_CHILD 15
BRANCH.IS_EXTENSION_NODE_S
BRANCH.IS_EXTENSION_NODE_C
```

Example:

```
[1 0 1 0 248 241 0 248 241 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 164 92 78 34 81 137 173 236 78 208 145 118 128 60 46 5 176 8 229 165 42 222 110 4 252 228 93 243 26 160 241 85 0 160 95 174 59 239 229 74 221 53 227 115 207 137 94 29 119 126 56 209 55 198 212 179 38 213 219 36 111 62 46 43 176 168 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 0 160 60 157 212 182 167 69 206 32 151 2 14 23 149 67 58 187 84 249 195 159 106 68 203 199 199 65 194 33 215 102 71 138 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 0 160 21 230 18 20 253 84 192 151 178 53 157 0 9 105 229 121 222 71 120 109 159 109 9 218 254 1 50 139 117 216 194 252 1]
[0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 0 160 229 29 220 149 183 173 68 40 11 103 39 76 251 20 162 242 21 49 103 245 160 99 143 218 74 196 2 61 51 34 105 123 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 0 160 0 140 67 252 58 164 68 143 34 163 138 133 54 27 218 38 80 20 142 115 221 100 73 161 165 75 83 53 8 58 236 1 1]
[0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 0 160 149 169 206 0 129 86 168 48 42 127 100 73 109 90 171 56 216 28 132 44 167 14 46 189 224 213 37 0 234 165 140 236 1]
[0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 0 160 42 63 45 28 165 209 201 220 231 99 153 208 48 174 250 66 196 18 123 250 55 107 64 178 159 49 190 84 159 179 138 235 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 16]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 17]
```

The constraints that are the same for `S` and `C` proofs are implemented in `branch_parallel.rs`.
For example, in a an empty row (nil branch child) like
```
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
```
we need to check that `rlp2 = 0`, `bytes[0] = 128`, and `bytes[i] = 0` for `i > 0`.

Also, we check that the RLC corresponding to the `modified_node` is stored in `mod_node_hash_rlc` column.
In the above example we have `modified_node = 2` which corresponds to the row:
```
[0 160 164 92 78 34 81 137 173 236 78 208 145 118 128 60 46 5 176 8 229 165 42 222 110 4 252 228 93 243 26 160 241 85 0 160 95 174 59 239 229 74 221 53 227 115 207 137 94 29 119 126 56 209 55 198 212 179 38 213 219 36 111 62 46 43 176 168 1]
```

So the `S` RLC of the `modified_node` is: `164 + 92 * r + 78 * r^2 + ... + 85 * r^31` 
The `C` RLC is: `95 + 174*r + 59* r^2 + ... + 168 * r^31`

The `S` RLC is stored in `s_mod_node_hash_rlc` column, in all 16 branch children rows.
The `C` RLC is stored in `c_mod_node_hash_rlc` column, in all 16 branch children rows.

Having the values stored in all 16 rows makes it easier to check whether it is really the value that
corresponds to the `modified_node`. Otherwise, having this value stored for example only in branch init row
we would not know what rotation to use into branch init when in `modified_node` row.

Note that the constraints about having the RLC value corresponds to the `modified_node` row are
implemented in `branch.rs`. This is because we do not have full symmetry between `S` and `C` proofs in the case
of branch placeholders.

Finally, when there is a non-hashed branch child, we need to check that there are 0s after the last
branch child byte. The example is:
```
[0,0,198,132,48,0,0,0,1,...]
```

In this case the branch child is of length `6 = 198 - 192`: `[132, 48, 0, 0, 0, 1]`.
We need to make sure there are 0s after these 6 bytes.

### Empty and non-empty branch children

Empty nodes have 0 at `rlp2`, have `128` at `bytes[0]` and 0 everywhere else:
```
[0, 0, 128, 0, ..., 0].
```
While non-empty nodes have `160` at `rlp2` and then any byte at `bytes`:
```
[0, 160, a0, ..., a31].
```

Note: `s_rlp1` and `c_rlp1` store the number of RLP still left in the in the branch rows.
The constraints are in `branch.rs`, see `RLP length` gate.

#### rlp2 = 0 or rlp2 = 160

Empty nodes have `rlp2 = 0`. Non-empty nodes have: `rlp2 = 160`.

### bytes[0] = 128 in empty node

When an empty node (0 at `rlp2`), `bytes[0] = 128`. Note that `rlp2` can be only 0 or 128 (see constraint
above).

#### bytes[i] = 0 for i > 0 in empty

When an empty node (0 at `rlp2`), `bytes[i] = 0` for `i > 0`.

### Branch child RLC & selector for specifying whether the modified node is empty

#### mod_node_hash_rlc the same for all branch children

`mod_node_hash_rlc` is the same for all `is_branch_child` rows.
Having the values stored in all 16 rows makes it easier to check whether it is really the value that
corresponds to the `modified_node`. This is used in `branch.rs` constraints like:
```
* is_modified.clone()
* (hash_rlc.clone() - mod_node_hash_rlc_cur.clone()
```

`hash_rlc` is computed in each row as: `bytes[0] + bytes[1] * r + ... + bytes[31] * r^31`.

Note that `hash_rlc` is somehow misleading name because the branch child can be non-hashed too.

#### Empty branch child modified: bytes[0] = 128

When a value is being added (and reverse situation when deleted) to the trie and
there is no other leaf at the position where it is to be added, we have empty branch child
in `S` proof and hash of a newly added leaf at the parallel position in `C` proof.
That means we have empty node in `S` proof at `modified_node`.
When this happens, we denote this situation by having `sel = 1`.
In this case we need to check that `main.bytes = [128, 0, ..., 0]`.
We first check `bytes[0] = 128`.

#### Empty branch child modified: bytes[i] = 0 for i > 0

The remaining constraints for `main.bytes = [128, 0, ..., 0]`:
`bytes[i] = 0` for `i > 0`.

#### Selector for the modified child being empty the same for all branch children

Having selector `sel` the same for all branch children makes it easier to write 
the constraint above for checking that `main.bytes = [128, 0, ..., 0]`
when `modified_node`. As for writing the constraints for RLC above, we would not know
what rotation to use otherwise (if information about modified node being empty would
be stored for example in branch init row).

### Non-hashed nodes have 0s after the last byte

When branch child is shorter than 32 bytes it does not get hashed, that means some positions
in `main.bytes` stay unused. But we need to ensure there are 0s at unused positions to avoid
attacks on the RLC which is computed taking into account all `main.bytes`.

## Branch RLC

The constraints in `branch_rlc.rs` check whether the branch RLC is being properly computed row by row.
There are three type of branch children rows: empty children, non-empty hashed children,
non-empty non-hashed children. We need to take into account these three types when computing
the intermediate RLC of the current row.

Note that the RLC for branch init row is checked in `branch_init.rs`.

### Branch RLC

#### Branch RLC empty

When a branch child is empty, we only have one byte (128 at `bytes[0]`)
that needs to be added to the RLC:
`branch_acc_curr = branch_acc_prev + 128 * branch_mult_prev`

`branch_mult_prev` is the value that is to be used when multiplying the byte to be added
to the RLC. Note that `branch_mult_prev` is stored in the previous row.

#### Branch RLC mult empty

When a branch child is empty, we only have one byte in a row and the multiplier only
changes by factor `r`.

#### Branch RLC non-empty hashed

When a branch child is non-empty and hashed, we have 33 bytes in a row.
We need to add these 33 bytes to the RLC.

#### Branch RLC mult non-empty hashed",
           
When a branch child is non-empty and hashed, we have 33 bytes in a row.
The multiplier changes by factor `r^33`.

#### Branch RLC non-hashed",

When a branch child is non-hashed, we have `bytes[0] - 192` bytes in a row.
We need to add these bytes to the RLC. Note that we add all `bytes` to the RLC, but
we rely that there are 0s after the last non-hashed byte (see constraints in `branch.rs`).

For example we have 6 bytes in the following child: `[0,0,198,132,48,0,0,0,1,...]`.

#### Branch RLC mult non-hashed

When a branch child is non-hashed, we have `f = bytes[0] - 192` bytes in a row.
The multiplier changes by factor `r^{f+1}`. `+1` is for the byte that specifies the length.

We do not know in advance the factor `f`, so we use the lookup table that it corresponds
to the length specified at `rlp2` position. See `mult_diff_lookup` constraint below.

### mult_diff_lookup

We need to check that the multiplier in non-hashed nodes changes according to the non-hashed
node length.


             