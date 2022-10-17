# Helper techniques

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
