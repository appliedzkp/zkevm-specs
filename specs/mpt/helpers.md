# Helpers

## RLPItemView

```
pub struct RLPItemView<F> {
    is_big_endian: bool,
    can_use_word: bool,
    bytes: Vec<Expression<F>>,
    num_bytes: Option<Expression<F>>,
    len: Option<Expression<F>>,
    mult: Option<Expression<F>>,
    hash_rlc: Option<Expression<F>>,
    rlc_rlp: Option<Expression<F>>,
    is_short: Option<Expression<F>>,
    is_long: Option<Expression<F>>,
    word: Option<Word<Expression<F>>>,
}
```

`RLPItemView` presents an entry point to the various item types. The types are given by the enumerator below:
```
pub enum RlpItemType {
    /// Node (string with len == 0 or 32, OR list with len <= 31)
    Node,
    /// Value (string with len <= 32)
    Value,
    /// Hash (string with len == 32)
    Hash,
    /// Address (string with len == 20)
    Address,
    /// Key (string with len <= 33)
    Key,
    /// Nibbles (raw data)
    Nibbles,
}
```

Note that `RLPItemView::Node` is used for branch children and for the value of the extension node (representing the branch hash or raw extension node if length < 33).
`RLPItemView::Value` is used for the value in the account and storage leaf.
`RLPItemView::Hash` is used for the codehash and storage trie hash as well as for the hashed address and key.
`RLPItemView::Address` is used for the non-hashed address.
`RLPItemView::Key` is used for the non-hashed key.
`RLPItemView::Nibbles` is used for the nibbles that are needed in the extension node.

When an RLP item is to be used, the `RLPItemView` is created by using the following function:
```
impl<F: Field> MPTContext<F> {
    pub(crate) fn rlp_item(
        &self,
        meta: &mut VirtualCells<F>,
        cb: &mut MPTConstraintBuilder<F>,
        idx: usize,
        item_type: RlpItemType,
    ) -> RLPItemView<F> {
        self.rlp_item.create_view(meta, cb, idx, item_type)
    }
}
```

For example in the account leaf:
```
let key_items = [
    ctx.rlp_item(meta, cb, AccountRowType::KeyS as usize, RlpItemType::Key),
    ctx.rlp_item(meta, cb, AccountRowType::KeyC as usize, RlpItemType::Key),
];
```

Now we have `RLPItemView` which can be used to retrieve the information such as the number of bytes or RLC the RLP item.

Let's observe each of the `RLPItemView` fields:
 * `is_big_endian` determines whether the data is stored in little endian or big endian. Little endian makes it much easier to decode the lo/hi split representation. Big endian is used in the case of `RlpItemType::Key` and `RlpItemType::Nibbles`.

<!--
    is_big_endian: bool,
    can_use_word: bool,
    bytes: Vec<Expression<F>>,
    num_bytes: Option<Expression<F>>,
    len: Option<Expression<F>>,
    mult: Option<Expression<F>>,
    hash_rlc: Option<Expression<F>>,
    rlc_rlp: Option<Expression<F>>,
    is_short: Option<Expression<F>>,
    is_long: Option<Expression<F>>,
    word: Option<Word<Expression<F>>>,
-->

TODO


## Extension key RLC helper functions

To ensure that the trie modification occurs at the right address/key, the path used to navigate through the trie needs to be somehow remembered by the circuit and it needs to be checked in the leaf. For this reason, the intermediate path is stored at each branch / extension node. The path is determined by the address / key nibbles and the circuit stores the intermediate RLC of the nibbles (actually of bytes) in each branch / extension node.

Let us say we have a branch `B1` in the root of the trie, a branch `B2` at the position `2` in `B1`, a branch `B3` at the position `7` in `B2`, a branch `B4` at the position `4` in `B3`, finally we have a leaf `L` at the position `9` in `B4`:
```
Child0    Child1     Child2: B2             ...            Child15
      Child0 ... Child7: B3 ... Child15
        Child0 ... Child4: B4 ... Child15
        Child0 ...      Child9: L ... Child15
```

The intermediate path RLC are:
```
RLC: 2 * 16 (first level)
RLC: 2 * 16 + 7 (second level)
RLC: (2 * 16 + 7) + 4 * 16 * r  (third level)
RLC: (2 * 16 + 7) + (4 * 16 + 9) * r  (fourth level)
```

Note that the nibbles are put into pairs to form bytes.

When there is an extension node, we need to take into account also its extension nibbles.

Let us say we have a branch `B1` in the root of the trie, a branch `B2` at the position `2` in `B1`, an extension node `E1` at the position `7` in `B2`, a branch `B4` at the position `4` in the underlying branch `B4` of `E1`, finally we have a leaf `L` at the position `9` in `B4`.
Let us say that the extension node `E1` has nibbles `8, 4, 11`.
```
Child0    Child1     Child2: B2             ...            Child15
      Child0 ... Child7: E1 ... Child15
        Child0 ... Child4: B4 ... Child15
        Child0 ...      Child9: L ... Child15
```

The intermediate path RLC are:
```
RLC: 2 * 16 (first level)
RLC: (2 * 16 + 7) + (8 * 16 + 4) * r + 11 * 16 (second level)
RLC: (2 * 16 + 7) + (8 * 16 + 4) * r + (11 * 16 + 4) * r^2 (third level)
RLC: (2 * 16 + 7) + (8 * 16 + 4) * r + (11 * 16 + 4) * r^2 + 9 * 16 (fourth level)
```

The computation of the intermediate RLC in the extension node depends on the two parities:
 * whether the number of the nibbles up to this level was odd or even
 * whether the number of the extension nibbles is odd or even

The second parity is important because it defined how the extension nibbles are compressed in the extension node RLP stream.

For example, let us observe the following extension node:
```
[228 130 0 150 160 215 121 207 40 14 160 149 115 175 222 139 45 208 88 81 65 226 190 111 191 208 252 147 90 105 163 154 4 132 52 204 121]
```

The second byte (`130 = 128 + 2`) denotes the length of the bytes that contain the nibbles (`2`).
The third and fourth bytes are (compressed) nibbles.
The compressed nibbles are `[0, 150]`.
The nibbles of this extension node are: `[9, 4]` (`150 = 9 * 16 + 4`).
When the number of nibbles is even, the first byte of the compressed nibbles is always `0`.

When the number of nibbles is odd, the first byte is `16` + the first nibble.

For example, in `[226,16,160,172,105,12...`
we have only one nibble (`0 = 16 - 16`) and the compressed nibbles occupy only one byte.

To take into account these different scenarios, the function with the following signature has been provided:
```
pub(crate) fn ext_key_rlc_expr<F: Field>(
    cb: &mut MPTConstraintBuilder<F>,
    key_value: RLPItemView<F>,
    key_mult_prev: Expression<F>,
    is_key_part_odd: Expression<F>,
    is_key_odd: Expression<F>,
    data: [Vec<Expression<F>>; 2],
    r: &Expression<F>,
) -> Expression<F>
```

The function takes the following parameters:
 * `key_value`: `RLPItemView` presenting the RLP item containing the compressed nibbles
 * `key_mult_prev`: the randomness multiplier `r^k` to be used in the computation of the RLC
 * `is_key_part_odd`: whether the number of the extension nibbles is odd
 * `is_key_odd`: whether the number of the nibbles up to this level is odd
 * `data`: bytes representing the compressed nibbles
 * `r`: the randomness for the computation of the RLC

The computation of the RLC is done depending on the two parities.

### `is_key_odd = true & is_key_part_odd = false`

Let us say we have nibbles `1, 7, 5` up to this level and we have nibbles `3, 2` in the extension. That means the nibbles in the extension node are compressed as `[0, 50 = 3 * 16 + 2]`.
The intermediate RLC is:
```
RLC = (1 * 16 + 7) + (5 * 16 + 3) * r + 2 * 16 * r^2
```

Note that to compute the RLC we need to know the nibbles `3, 2` separately (and not only the compressed value `50`) because they appear in different byte terms. For this reason, the MPT witness contains also the list of every second nibble (in this case the only second nibble is `2`).

The function `ext_key_rlc_expr` gets the second nibbles from the witness and computes the first nibbles using the byte and second nibbles information.

### `is_key_odd = false & is_key_part_odd = true`

Let us say we have nibbles `1, 7` up to this level and we have nibbles `5, 3, 2` in the extension. That means the nibbles in the extension node are compressed as `[21 = 16 + 5, 50 = 3 * 16 + 2]`.
The intermediate RLC is:
```
RLC = (1 * 16 + 7) + (5 * 16 + 3) * r + 2 * 16 * r^2
```

Note that we again need to know the nibbles `5, 3, 2` separately because they appear in different byte terms - `3` and `2` are compressed together in the witness, but the two appear in different byte terms in the computation of the RLC.

### `is_key_odd = false & is_key_part_odd = false`

Let us say we have nibbles `1, 7` up to this level and we have nibbles `5, 3` in the extension. That means the nibbles in the extension node are compressed as `[0, 50 = 3 * 16 + 2]`.
The intermediate RLC is:
```
RLC = (1 * 16 + 7) + (5 * 16 + 3) * r
```

Note that the nibbles `5, 3` are compressed together in the witness and they appear in the same byte term in the RLC computation, so there is no need to use the second nibble from the witness. 

### `is_key_odd = true & is_key_part_odd = true`

Let us say we have nibbles `1, 7, 5` up to this level and we have nibbles `4, 3, 2` in the extension. That means the nibbles in the extension node are compressed as `[20 = 16 + 4, 50 = 3 * 16 + 2]`.
The intermediate RLC is:
```
RLC = (1 * 16 + 7) + (5 * 16 + 4) * r + (3 * 16 + 2) * r^2
```

Note that there is again no need to use second nibbles.
We add the nibble that is compressed alone (`4 = 20 - 16`) to the term that has one nibble missing and we obtain `(5 * 16 + 4) * r`.

The following nibbles (`5, 3`) are compressed together in the witness and they appear in the same byte terms in the RLC computation, so there is no need to use the second nibble from the witness. 

### `is_key_part_odd` only has one nibble

In the case when `is_key_part_odd` only has one nibble, the computation of the RLC is simple (no computation of the first nibbles), it just needs to be taken into accout the parity of the number of nibbles up to this level.




# Obsolete (to be updated)

## Zeros in s_main/c_main after substream ends

In various cases, `s_main.bytes` and `c_main.bytes` columns are used only to a certain point.
Consider the example below:

```
228, 130, 0, 149, 0, ..., 0
```

In this example:

```
s_main.rlp1 = 228
s_main.rlp2 = 130
s_main.bytes[0] = 0
s_main.bytes[1] = 149
s_main.bytes[2] = 0
...
s_main.bytes[31] = 0
```

To prevent attacks on the RLC, it needs to be checked that `s_main.bytes[i] = 0` for `i > 1`:

```
s_main.bytes[2] = 0
...
s_main.bytes[31] = 0
```

The length of the substream is given by `s_main.rlp2`, it is `2 = 130 - 128` in the above example,
let us denote it by `len = 2`.
Also, there are constraints to ensure `s_main.bytes[i]` are bytes (between 0 and 255).

Note that `(len - 1 - i) * s_main.bytes[0] < 33 * 255` ensures `s_main.bytes[i] = 0` for `i > len - 1`.
So we check that the expression `(len - 1 - i) * s_main.bytes[0]` is in the range table
containing elements from `0` to `33 * 255`.

```
(len - 1) * s_main.bytes[0] < 33 * 255
(len - 2) * s_main.bytes[1] < 33 * 255
From now on, key_len < 0:
(len - 3) * s_main.bytes[2] < 33 * 255 (Note that this will be true only if s_main.bytes[2] = 0)
(len - 4) * s_main.bytes[3] < 33 * 255 (Note that this will be true only if s_main.bytes[3] = 0)
(len - 5) * s_main.bytes[4] < 33 * 255 (Note that this will be true only if s_main.bytes[4] = 0)
```

That is because when `len - i` goes below 0, it becomes a huge number close to the field modulus.
Furthermore, `len` is at most 33.
When `len - i` is below 0 and is multiplied by `s_main.bytes[i]` which is at most `255`, it will be
bigger then `-32 * 255` which is much bigger than `33 * 255`, so it will not be in the range table
unless `s_main.bytes[i] = 0`.

See `key_len_lookup` in `helpers.rs` for the implementation.

## Randomness for computing the RLC nees to be properly set for usage in the next row

As we have seen above,
in various cases, `s_main.bytes` are used only to certain point. Consider the example below:

```
228, 130, 0, 149, 0, ..., 0
```

Let us say this is the storage leaf key row. For computation of the storage leaf RLC we need
to first compute the intermediate RLC in the storage leaf key row and then take into account the bytes
from the storage leaf value row as well.

The RLC is thus computed in two steps.
The first step computes the RLC out of bytes `s_main.rlp1', 's_main.rlp2`, `s_main.bytes`.

The first step:

```
rlc_first_step = s_main.rlp1 + s_main.rlp2 * r + s_main.bytes[0] * r^2 + s_main.bytes[1] * r^3 + ... + s_main.bytes[31] * r^33 
```

We check that this value is properly stored in `acc_s` column.

```
rlc_first_step = acc_s
```

The second step computes the RLC out of bytes `c_main.rlp1', 'c_main.rlp2`, `c_main`.

```
rlc = rlc_first_step + c_main.rlp1 * r_1 + c_main.rlp2 * r_1^2 + c_main[0] * r_1^3 + c_main[1] * r_1^4 + ... + c_main[31] * r_1^34 
```

Note that `r_1` needs to correspond to the length of the bytes in the storage leaf key row.
Let us say `len` is the number of bytes in `s_main.bytes` in the storage leaf key row:

```
len = s_main.rlp2 - 128
```

It needs to be ensured that:

```
r_1 = r^(len+2)
```

This can be ensured using a lookup into a table:

```
(RMult, 0, 1)
(RMult, 1, r)
(RMult, 2, r^2)
(RMult, 3, r^3)
...
(RMult, 65, r^65)
```

The lookup looks like:

```
lookup(RMult, len+2, r_1)
```

See `mult_diff_lookup` in `helpers.rs` for the implementation.
