# Storage leaf

An example of the storage leaf returned by `getProof` is:
```
[226,160,59,138,106,70,105,186,37,13,38,205,122,69,158,202,157,33,95,131,7,227,58,235,229,3,121,188,90,54,23,236,52,68,1]
```

The first byte (`226 = 192 + 34`) represents the length of the RLP stream - meaning there are `34` bytes after the first byte.
The second byte `160 = 128 + 32`) represents the length of the RLP substream representing the key leaf - meaning there are `32` bytes after the
second byte that represent the key.
The last byte (`1`) is the leaf value - note that it does not have a RLP byte specifyng the length because it is only one byte.

The substream represents
`
59,138,106,70,105,186,37,13,38,205,122,69,158,202,157,33,95,131,7,227,58,235,229,3,121,188,90,54,23,236,52,68,
`
represents the key. The key nibbles are:
```
11 (59 - 48)
8
10 (8 * 16 + 10 = 138)
6
10 (6 * 16 + 10 = 106)
4
6 (4 * 16 + 6 = 70)
...
```



# Obsolete

A storage leaf occupies 6 rows.
Contrary as in the branch rows, the `S` and `C` leaves are not positioned parallel to each other.
The rows are the following:
```
LEAF_KEY_S
LEAF_VALUE_S
LEAF_KEY_C
LEAF_VALUE_C
LEAF_DRIFTED
LEAF_NON_EXISTING
```

An example of leaf rows:
```
[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

In the above example the value has been changed from 1 (`LEAF_VALUE_S`) to 17 (`LEAF_VALUE_C`).

In the example below the value in `LEAF_VALUE_C` takes more than 1 byte: `[187 239 170 ...]`
This has two consequences:
 - Two additional RLP bytes: `[161 160]` where `33 = 161 - 128` means there are `31` bytes behind `161`,
   `32 = 160 - 128` means there are `30` bytes behind `160`.
 - `LEAF_KEY_S` starts with `248` because the leaf has more than 55 bytes, `1 = 248 - 247` means
   there is 1 byte after `248` which specifies the length - the length is `67`. We can see that
   that the leaf key is shifted by 1 position compared to the example above.

For this reason we need to distinguish two cases: 1 byte in leaf value, more than 1 byte in leaf value.
These two cases are denoted by `is_short` and `is_long`. There are two other cases we need to
distinguish: `last_level` when the leaf is in the last level and has no nibbles, `one_nibble` when
the leaf has only one nibble.

`last_level`:
```
[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[161 160 187 239 170 18 88 1 56 188 38 60 149 117 120 38 223 78 36 235 129 201 170 170 170 170 170 170 170 170 170 170 170 170 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

`last_level`
```
[194 32 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[194 32 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

`one_nibble`:
```
[194 48 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[194 48 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

`s_mod_node_rlc` (`flag1`) and `c_mod_node_rlc` (`flag2`) columns store the information of what
kind of case we have:
 `flag1: 1, flag2: 0`: `is_long`
 `flag1: 0, flag2: 1`: `is_short`
 `flag1: 1, flag2: 1`: `last_level`
 `flag1: 0, flag0: 1`: `one_nibble`

The constraints in `leaf_key.rs` apply to `LEAF_KEY_S` and `LEAF_KEY_C` rows.
The constraints ensure the hash of a storage leaf is in a parent branch and that the RLP
of the leaf is correct.

Lookups:
The `is_storage_mod` lookup is enabled in `LEAF_VALUE_C` row.

Note that there are no checks for example for the root as the constraints to ensure `start_root`
and `final_root` does not change (except in the first row of the modification) are in `proof_chain.rs`
and the constraints to ensure the lookup roots correspond to the roots of the trie are in the first
level nodes (`account_leaf_storage_codehash.rs` or `branch_hash_in_parent.rs`).

## Storage leaf key constraints

### Storage leaf key RLC

#### is_long: s_rlp1 = 248

When `is_long` (the leaf value is longer than 1 byte), `s_main.rlp1` needs to be 248.

Example:
`[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`

#### last_level: s_rlp2 = 32

When `last_level`, there is no nibble stored in the leaf key, it is just the value
`32` in `s_main.rlp2`. In the `getProof` output, there is then the value stored immediately
after `32`. However, in the MPT witness, we have value in the next row, so there are 0s
in `s_main.bytes` (we do not need to check `s_main.bytes[i]` to be 0 due to how the RLC
constraints are written).

Example:
`[194 32 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`

#### flag1 is boolean & flag2 is boolean

The two values that store the information about what kind of case we have need to be boolean.

#### Leaf key RLC (short or long)

We need to ensure that the RLC of the row is computed properly for `is_short` and
`is_long`. We compare the computed value with the value stored in `accumulators.acc_s.rlc`.

#### Leaf key RLC (last level or one nibble)

We need to ensure that the RLC of the row is computed properly for `last_level` and
`one_nibble`. We compare the computed value with the value stored in `accumulators.acc_s.rlc`.

`last_level` and `one_nibble` cases have one RLP byte (`s_rlp1`) and one byte (`s_rlp2`)
where it is 32 (for `last_level`) or `48 + last_nibble` (for `one_nibble`).

#### 0s after the last key nibble

There are 0s in `s_main.bytes` after the last key nibble (this does not need to be checked for `last_level` and `one_nibble` as in these cases `s_main.bytes` are not used).

### mult_diff

The intermediate RLC value of this row is stored in `accumulators.acc_s.rlc`.
To compute the final leaf RLC in `LEAF_VALUE` row, we need to know the multiplier to be used
for the first byte in `LEAF_VALUE` row too. The multiplier is stored in `accumulators.acc_s.mult`.
We check that the multiplier corresponds to the length of the key that is stored in `s_main.rlp2`
for `is_short` and in `s_main.bytes[0]` for `is_long`.

Note: `last_level` and `one_nibble` have fixed multiplier because the length of the nibbles
in these cases is fixed.

### Storage leaf key RLC & nibbles count (leaf not in first level, branch not placeholder)

We need to ensure that the storage leaf is at the key specified in `key_rlc` column (used
by MPT lookup). To do this we take the key RLC computed in the branches above the leaf
and add the remaining bytes (nibbles) stored in the leaf.

We also ensure that the number of all nibbles (in branches / extension nodes above
the leaf and in the leaf) is 64.

#### Leaf key RLC s_bytes0 = 32 (short)

If `is_c1` and branch above is not a placeholder, we have 32 in `s_main.bytes[0]`.
This is because `is_c1` in the branch above means there is an even number of nibbles left
and we have an even number of nibbles in the leaf, the first byte (after RLP bytes
specifying the length) of the key is 32.

#### Key RLC (short)

We need to ensure the leaf key RLC is computed properly. We take the key RLC value
from the last branch and add the bytes from position
`s_main.bytes[0]` up at most to `c_main.rlp1`. We need to ensure that there are 0s
after the last key byte, this is done by `key_len_lookup`.

The computed value needs to be the same as the value stored `key_rlc` column.

`is_short` example:
[226,160,59,138,106,70,105,186,37,13,38[227,32,161,160,187,239,170,18,88,1,56,188,38,60,149,117,120,38,223,78,36,235,129,201,170,170,170,170,170,170,170,170,170,170,170,170]

Note: No need to distinguish between `c16` and `c1` here as it was already
when computing `key_rlc_acc_short`.

#### Leaf key acc s_bytes1 = 32 (long)

If `is_c1` and branch above is not a placeholder, we have 32 in `s_main.bytes[1]`.
This is because `is_c1` in the branch above means there is an even number of nibbles left
and we have an even number of nibbles in the leaf, the first byte (after RLP bytes
specifying the length) of the key is 32.

#### Key RLC (long)

We need to ensure the leaf key RLC is computed properly. We take the key RLC value
from the last branch and add the bytes from position
`s_main.bytes[1]` up at most to `c_main.rlp2`. We need to ensure that there are 0s
after the last key byte, this is done by `key_len_lookup`.

The computed value needs to be the same as the value stored `key_rlc` column.

`is_long` example:
`[248,67,160,59,138,106,70,105,186,37,13,38,205,122,69,158,202,157,33,95,131,7,227,58,235,229,3,121,188,90,54,23,236,52,68,161,160,...`

Note: No need to distinguish between `c16` and `c1` here as it was already
when computing `key_rlc_acc_long`.

#### Leaf key acc s_rlp2 = 32 (last level)

When the leaf is in the last level there are no nibbles stored in the key and `s_main.rlp2 = 32`.

#### Key RLC (last level)

We need to ensure the leaf key RLC is computed properly.
When the leaf is in the last level we simply take the key RLC value
from the last branch and this is the final key RLC value as there is no
nibble in the leaf.

The computed value needs to be the same as the value stored `key_rlc` column.

Last level example:
`[227,32,161,160,187,239,170,18,88,1,56,188,38,60,149,117,120,38,223,78,36,235,129,201,170,170,170,170,170,170,170,170,170,170,170,170]`

#### Key RLC (one nibble)

We need to ensure the leaf key RLC is computed properly.
When there is only one nibble in the leaf, we take the key RLC value
from the last branch and add the last remaining nibble stored in `s_main.rlp2`.

The computed value needs to be the same as the value stored `key_rlc` column.

One nibble example short value:
`[194,48,1]`

One nibble example long value:
`[227,48,161,160,187,239,170,18,88,1,56,188,38,60,149,117,120,38,223,78,36,235,129,201,170,170,170,170,170,170,170,170,170,170,170,170]`

#### Total number of storage address nibbles is 64 (not first level, not branch placeholder)

Checking the total number of nibbles is to prevent having short addresses
which could lead to a root node which would be shorter than 32 bytes and thus not hashed. That
means the trie could be manipulated to reach a desired root.

### Storage leaf key RLC (after placeholder)

For leaf under the placeholder branch we would not need to check the key RLC -
this leaf is something we did not ask for, it is just a leaf that happened to be
at the place where adding a new leaf causes adding a new branch.
For example, when adding a leaf `L` causes that a leaf `L1`
(this will be the leaf under the branch placeholder)
is replaced by a branch, we get a placeholder branch at `S` side
and leaf `L1` under it. However, the key RLC needs to be compared for leaf `L`,
because this is where the modification takes place.
In delete, the situation is turned around.

However, we also check that the key RLC for `L1` is computed properly because
we need `L1` key RLC for the constraints for checking that leaf `L1` is the same
as the drifted leaf in the branch parallel. This can be checked by
comparing the key RLC of the leaf before being replaced by branch and the key RLC
of this same leaf after it drifted into a branch.
Constraints for this are in `leaf_key_in_added_branch.rs`.

Note that the hash of a leaf `L1` needs to be checked to be in the branch
above the placeholder branch - this is checked in `leaf_value.rs`.

#### Leaf key acc s_bytes0 (short)

If `is_c1 = 1` which means there is an even number of nibbles stored in a leaf,
we have 32 in `s_main.bytes[0]`.

#### Key RLC (short)

When `is_short` the first key byte is at `s_main.bytes[0]`. We retrieve the key RLC from the
branch above the branch placeholder and add the nibbles stored in a leaf.
The computed key RLC needs to be the same as the value stored at `accumulators.key.rlc`.

`is_short`:
`[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]`

`is_long`:
`[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`

Note: No need to distinguish between `is_c16` and `is_c1` here as it was already
when computing `key_rlc_acc_short`.

#### Leaf key acc s_bytes1 (long)

If `is_c1 = 1` which means there is an even number of nibbles stored in a leaf,
we have 32 in `s_main.bytes[1]`.

#### Key RLC (long)

When `is_long` the first key byte is at `s_main.bytes[1]`. We retrieve the key RLC from the
branch above the branch placeholder and add the nibbles stored in a leaf.
The computed key RLC needs to be the same as the value stored at `accumulators.key.rlc`.

`is_short`:
`[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]`

`is_long`:
`[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`

Note: No need to distinguish between `is_c16` and `is_c1` here as it was already
when computing `key_rlc_acc_short`.

#### Total number of account address nibbles is 64 (after placeholder)

Checking the total number of nibbles is to prevent having short addresses
which could lead to a root node which would be shorter than 32 bytes and thus not hashed. That
means the trie could be manipulated to reach a desired root.

To get the number of nibbles above the leaf we need to go into the branch above the placeholder branch.

Note that when the leaf is in the first storage level (but positioned after the placeholder
in the circuit), there is no branch above the placeholder branch from where
`nibbles_count` is to be retrieved. In that case `nibbles_count = 0`.

### Range lookups

Range lookups ensure that `s_main`, `c_main.rlp1`, `c_main.rlp2` columns are all bytes (between 0 - 255).

## Leaf value constraints

### Leaf & Leaf value RLC

We need the RLC of the whole leaf for a lookup that ensures the leaf is in the parent branch.
We need the leaf value RLC for external lookups that ensure the value has been set correctly.

### is_long & is_short are booleans and the sum is 1

`is_short` means value has only one byte and consequently, the RLP of
the value is only this byte itself. If there are more bytes, the value is
equipped with two RLP meta bytes, like 161 160 if there is a
value of length 32 (the first RLP byte means 33 bytes after it, the second
RLP byte means 32 bytes after it).

`is_short` example:
`[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]`

`is_long` example:
`[161 160 187 239 170 18 88 1 56 188 38 60 149 117 120 38 223 78 36 235 129 201 170 170 170 170 170 170 170 170 170 170 170 170 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]`

We need to ensure `is_long` and `is_short` are booleans and that `is_long + is_short = 1`.

### Leaf RLC

We need to ensure that the stored leaf RLC is the same as the computed one.

### Leaf value RLC

We need to ensure that the stored leaf value RLC is the same as the computed one.

#### Leaf key C RLC properly copied & Leaf value S RLC properly copied

To enable external lookups we need to have the following information in the same row:
 - key RLC:                       we copy it to `accs.key.mult` column from the leaf key C row
 - previous (`S`) leaf value RLC: we copy it to `value_prev` column from the leaf value `S` row
 - current (`C`) leaf value RLC:  stored in `acc_c` column, we copy it to `value` column

#### s_main are 0s when there is no storage leaf (just a placeholder)

`sel` column in branch children rows determines whether the `modified_node` is empty child.
For example when adding a new storage leaf to the trie, we have an empty child in `S` proof
and non-empty in `C` proof. 
When there is an empty child, we have a placeholder leaf under the last branch.

If `sel = 1` which means an empty child, we need to ensure that the value is set to 0
in the placeholder leaf.

Note: For a leaf without a branch (means it is in the first level of the trie)
the constraint is in `storage_root_in_account_leaf.rs`.

#### RLP leaf short value short

When the leaf is short (first key byte in `s_main.bytes[0]` in the leaf key row) and the value
is short (first value byte in `s_main.rlp1` in the leaf value row), we need to check that:
`s_rlp1_prev - 192 - s_rlp2_prev + 128 - 1 - 1 = 0`.

The first `-1` presents the byte occupied by `s_rlp2_prev`.
The second `-1` presents the length of the value which is 1 because the value is short in this case.

Example:
`[226 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]`

In the example: `34 = 226 - 192` gives the length of the RLP stream. `32 = 160 - 128` gives the length
of the key. That means there are 34 bytes after the first byte, 32 of these are occupied by the key,
1 is occupied by `s_rlp2_prev`, and 1 is occupied by the value.

#### RLP leaf long value long

When the leaf is long (first key byte in `s_main.bytes[1]` in the leaf key row) and the value
is long (first value byte in `s_main.bytes[0]` in the leaf value row), we need to check that:
`s_rlp2_prev - s_bytes0_prev + 128 - 1 - (s_rlp2_cur - 128 + 1 + 1) = 0`.

The expression `s_rlp2_prev - s_bytes0_prev + 128 - 1` gives us the number of bytes that are to be left
in the value. The expression `s_rlp2_cur - 128 + 1 + 1` gives us the number of bytes in the leaf.

Note that there is an additional constraint to ensure `s_main.rlp1 = s_main.rlp2 + 1`.

Example:
`[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`
`[161 160 187 239 170 18 88 1 56 188 38 60 149 117 120 38 223 78 36 235 129 201 170 170 170 170 170 170 170 170 170 170 170 170 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]`

67 is the number of bytes after `s_main.rlp2`. `160 - 128 + 1` is the number of bytes that are occupied
by the key and the byte that stores key length.
In the next row, we have `32 = 160 - 128` bytes after `s_main.rlp2`, but we need to take into
account also the two bytes `s_main.rlp1` and `s_main.rlp2`.

#### RLP leaf short value long

When the leaf is short (first key byte in `s_main.bytes[0]` in the leaf key row) and the value
is long (first value byte in `s_main.bytes[0]` in the leaf value row), we need to check that:
`s_rlp1_prev - 192 - s_rlp2_prev + 128 - 1 - (s_rlp2_cur - 128 + 1 + 1) = 0`.

The expression `s_rlp1_prev - 192 - s_rlp2_prev + 128 - 1` gives us the number of bytes that are to be left in the value. The expression `s_rlp2_cur - 128 + 1 + 1` gives us the number of bytes in the leaf.

#### RLP long value check

When the leaf is long (first key byte in `s_main.bytes[1]` in the leaf key row)
we need to ensure that `s_main.rlp1 = s_main.rlp2 + 1`.

#### RLP check last level or one nibble & short value

When the leaf is in the last level of the trie and the value is short,
we need to ensure that `s_main.rlp2 = 32`.

Note that in this case we do not have the length of the key stored in `s_main.rlp2` or `s_main.bytes[0]`.
            
Example: `[194,32,1]`

#### RLP check last level or one nibble & long value

When the leaf is in the last level of the trie and the value is long or there is one nibble in the key,
we need to check:
`s_rlp1_prev - 192 - 1  - (s_rlp2_cur - 128 + 1 + 1) = 0`.

`s_rlp1_prev - 192 - 1` gives us the number of bytes that are to be in the leaf value row, while
s_rlp2_cur - 128 + 1 + 1 gives us the number of bytes in the leaf value row.

Note that in this case we do not have the length of the key stored in `s_main.rlp2` or `s_main.bytes[0]`.

Example:
`[227,32,161,160,187,239,170,18,88,1,56,188,38,60,149,117,120,38,223,78,36,235,129,201,170,170,170,170,170,170,170,170,170,170,170,170]`

### Hash of the only storage leaf is storage trie root

If there is no branch or extension node in the storage trie (just a leaf), it needs
to be ensured that the hash of the (only) leaf is the storage root.

Note: Storage leaf in the first level cannot be shorter than 32 bytes (it is always hashed).

### Hash of the only storage leaf which is placeholder requires empty storage root

When there is only one leaf in a storage trie and it is a placeholder, the trie needs to
be empty - the storage root is hash of an empty trie.
This occurs when the storage trie is empty and the first leaf is added (or reversed when
there is only one leaf and it is deleted) - in this case we have a placeholder leaf in
`S` proof and only one leaf in `C` proof. We need to check that in `S` proof we have an
empty trie.

### Hash of the only storage leaf which is after a placeholder is storage trie root

If there is no branch or extension node in the storage trie (just a leaf)
and the only leaf appears after branch placeholder, it needs
to be ensured that the hash of the (only) leaf is the storage root.
This appears when there is only one leaf in the storage trie and we add another leaf which
means the only leaf in a trie is replaced by a branch or extension node (in delete scenario
we have two leaves and one is deleted) - that means we have a branch placeholder in `S` proof
and the leaf after it.

Note: Branch in the first level cannot be shorter than 32 bytes (it is always hashed).

### Leaf hash in parent

It needs to be checked that the hash of a leaf is in the parent node. We do this by a lookup
into keccak table: `lookup(leaf_hash_rlc, parent_node_mod_child_rlc)`. 

### Hash of the only storage leaf is storage trie root

If there is no branch or extension node in the storage trie (just a leaf), it needs
to be ensured that the hash of the (only) leaf is the storage root.

Note: storage leaf in the first level cannot be shorter than 32 bytes (it is always hashed).

### Non-hashed leaf in parent

When the leaf is not hashed (shorter than 32 bytes), it needs to be checked that its RLC
is the same as the RLC of the modified node in the parent branch.

When leaf is not hashed, the `mod_node_hash_rlc` stores the RLC of the leaf bytes
(instead of the RLC of leaf hash). So we take the leaf RLC and compare it to the value
stored in `mod_node_hash_rlc` in the parent branch.

Note: `branch_parallel.rs` checks that there are 0s in `*_bytes` after the last
byte of the non-hashed branch child (otherwise some corrupted RLC could be provided).

### Leaf hash in parent (branch placeholder)

Lookup for case when there is a placeholder branch - in this case we need to
check the hash to correspond to the modified node of the branch above the placeholder branch.

### Range lookups

Range lookups ensure that `s_main`, `s_main.rlp1`, `s_main.rlp2` columns are all bytes (between 0 - 255).

### 0s in s_main.bytes after the last byte value

There are 0s in `s_main.bytes` after the last value byte.

## Leaf key in added branch constraints

A storage leaf occupies 6 rows.
Contrary as in the branch rows, the `S` and `C` leaves are not positioned parallel to each other.
The rows are the following:
```
LEAF_KEY_S
LEAF_VALUE_S
LEAF_KEY_C
LEAF_VALUE_C
LEAF_DRIFTED
LEAF_NON_EXISTING
```

An example of leaf rows:
```
[226 160 32 235 117 17 208 2 186 74 12 134 238 103 127 37 240 27 164 245 42 218 188 162 9 151 17 57 90 177 190 250 180 61 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[27 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[225 159 63 117 31 216 242 20 172 137 89 10 84 218 35 38 178 182 67 5 68 54 127 178 216 248 46 67 173 108 157 55 18 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[225 159 59 117 17 208 2 186 74 12 134 238 103 127 37 240 27 164 245 42 218 188 162 9 151 17 57 90 177 190 250 180 61 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

The `LEAF_DRIFTED` row is nonempty when a leaf is added (or deleted) to the position in trie where there is already
an existing leaf. This appears when an existing leaf and a newly added leaf have the same initial key nibbles.
In this case, a new branch is created and both leaves (existing and newly added) appear in the new branch.
`LEAF_DRIFTED` row contains the key bytes of the existing leaf once it drifted down to the new branch.

The constraints for `LEAF_DRIFTED` row are very similar to the ones for `LEAF_KEY` rows, but we have
different selectors (different row) and there are some scenarios that do not appear here, like being in
the first level of the trie. Also, when computing the leaf RLC, we need to take a different approach because
the leaf value for the drifted leaf is stored in a parallel proof.

### Storage leaf in added branch RLC

It needs to be ensured that the leaf intermediate RLC (containing the leaf key bytes) is properly computed.
The intermediate RLC is then used to compute the final leaf RLC (containing the leaf value bytes too).
Finally, the lookup is used to check that the hash that
corresponds to the leaf RLC is in the parent branch at `drifted_pos` position.

#### is_long: s_rlp1 = 248

When `is_long` (the leaf value is longer than 1 byte), `s_main.rlp1` needs to be 248.

Example:
`[248 67 160 59 138 106 70 105 186 37 13 38 205 122 69 158 202 157 33 95 131 7 227 58 235 229 3 121 188 90 54 23 236 52 68 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]`

#### flag1 is boolean & flag2 is boolean

The two values that store the information about what kind of case we have need to be boolean.

#### Leaf key RLC (short or long)

We need to ensure that the RLC of the row is computed properly for `is_short` and
`is_long`. We compare the computed value with the value stored in `accumulators.acc_s.rlc`.

#### Leaf key RLC (last level or one nibble)

We need to ensure that the RLC of the row is computed properly for `last_level` and
`one_nibble`. We compare the computed value with the value stored in `accumulators.acc_s.rlc`.

`last_level` and `one_nibble` cases have one RLP byte (`s_rlp1`) and one byte (`s_rlp2`)
where it is 32 (for `last_level`) or `48 + last_nibble` (for `one_nibble`).

#### 0s after the last key nibble

There are 0s in `s_main.bytes` after the last key nibble (this does not need to be checked for `last_level` and `one_nibble` as in these cases `s_main.bytes` are not used).

### mult_diff

The intermediate RLC value of this row is stored in `accumulators.acc_s.rlc`.
To compute the final leaf RLC in `LEAF_VALUE` row, we need to know the multiplier to be used
for the first byte in the leaf value row (which is in a parallel proof).
The multiplier is stored in `accumulators.acc_s.mult`.
We check that the multiplier corresponds to the length of the key that is stored in `s_main.rlp2`
for `is_short` and in `s_main.bytes[0]` for `is_long`.

Note: `last_level` and `one_nibble` have fixed multiplier because the length of the nibbles
in these cases is fixed.

### Storage drifted leaf key RLC

We need to ensure that the drifted leaf has the proper key RLC. It needs to be the same as the key RLC
of this same leaf before it drifted to the new branch. The difference is that after being drifted the leaf
has one nibble less stored in the key - `drifted_pos` nibble that is in a branch parallel to the branch
placeholder (if it is an extension node there are more nibbles of a difference).

```
Leaf key S
Leaf value S
Leaf key C
Leaf value C
Drifted leaf (leaf in added branch)
Leaf non existing
```

Add case (S branch is placeholder):
```
  Branch S           || Branch C             
  Placeholder branch || Added branch
  Leaf S             || Leaf C
                      || Drifted leaf (this is Leaf S drifted into Added branch)
```

Leaf S needs to have the same key RLC as Drifted leaf.
Note that Leaf S key RLC is computed by taking the key RLC from Branch S and
then adding the bytes in Leaf key S row.
Drifted leaf RLC is computed by taking the key RLC from Added branch and
then adding the bytes in Drifted leaf row.

Delete case (C branch is placeholder):
```
  Branch S                        || Branch C             
  Branch to be deleted            || Placeholder branch
  Leaf S (leaf to be deleted)     || Leaf C
  Leaf to be drifted one level up || 
```

#### Leaf key RLC s_bytes0 = 32 (short)

If `is_c1` and branch above is not a placeholder, we have 32 in `s_main.bytes[0]`.
This is because `c1` in the branch above means there is an even number of nibbles left
and we have an even number of nibbles in the leaf, the first byte (after RLP bytes
specifying the length) of the key is 32.

Note: `is_c1` is taken from the branch parallel to the placeholder branch. This is because
the leaf in added branch is in this branch (parallel to placeholder branch).
When computing the key RLC, `is_c1` means `drifted_pos` needs to be multiplied by 1, while
`is_c16` means `drifted_pos` needs to be multiplied by 16.

#### Drifted leaf key RLC S (short)

When `S` placeholder, `leaf_key_s_rlc` is the key RLC of the leaf before it drifted down
in a new branch. We retrieve it from `LEAF_KEY_S` row.
This value needs to be the same as the key RLC of the drifted leaf.

#### Drifted leaf key RLC C (short)

When `C` placeholder, `leaf_key_c_rlc` is the key RLC of the leaf after its neighbour leaf
has been deleted (and there were only two leaves, so the branch was deleted).
We retrieve it from `LEAF_KEY_C` row.
This value needs to be the same as the key RLC of the neighbour leaf (neighbour of
the leaf that was deleted) before the leaf was deleted.

#### Leaf key acc s_bytes1 = 32 (long)

If `is_c1` and branch above is not a placeholder, we have 32 in `s_main.bytes[1]`.
This is because `is_c1` in the branch above means there is an even number of nibbles left
and we have an even number of nibbles in the leaf, the first byte (after RLP bytes
specifying the length) of the key is 32.

#### Drifted leaf key RLC S (long)

Same as above `Drifted leaf key S (short)` but for `long` (key starts in `s_main.bytes[1]` instead
of `s_main.bytes[0]`).

#### Drifted leaf key RLC C (long)

Same as above `Drifted leaf key C (short)` but for `long` (key starts in `s_main.bytes[1]` instead
of `s_main.bytes[0]`).

#### Leaf key acc s_rlp2 = 32 (last level)

When the leaf is in the last level there are no nibbles stored in the key and `s_main.rlp2 = 32`.

#### Drifted leaf key RLC S (last level)

When `S` placeholder, `leaf_key_s_rlc` is the key RLC of the leaf before it drifted down
in a new branch. We retrieve it from `LEAF_KEY_S` row.
This value needs to be the same as the key RLC of the drifted leaf.

We do not need to add any nibbles to the key RLC as there are none stored in the storage leaf
(last level).

#### Drifted leaf key RLC C (last level)

When `C` placeholder, `leaf_key_c_rlc` is the key RLC of the leaf after its neighbour leaf
has been deleted (and there were only two leaves, so the branch was deleted).
We retrieve it from `LEAF_KEY_C` row.
This value needs to be the same as the key RLC of the neighbour leaf (neighbour of
the leaf that was deleted) before the leaf was deleted.

We do not need to add any nibbles to the key RLC as there are none stored in the storage leaf
(last level).

#### Drifted leaf key RLC S (one nibble)

When `S` placeholder, `leaf_key_s_rlc` is the key RLC of the leaf before it drifted down
in a new branch. We retrieve it from `LEAF_KEY_S` row.
This value needs to be the same as the key RLC of the drifted leaf.

We only need to add one nibble to the key RLC.

#### Drifted leaf key RLC C (one nibble)

When `C` placeholder, `leaf_key_c_rlc` is the key RLC of the leaf after its neighbour leaf
has been deleted (and there were only two leaves, so the branch was deleted).
We retrieve it from `LEAF_KEY_C` row.
This value needs to be the same as the key RLC of the neighbour leaf (neighbour of
the leaf that was deleted) before the leaf was deleted.

We only need to add one nibble to the key RLC.

### Leaf key in added branch: neighbour leaf in the added branch (S)

It needs to be ensured that the hash of the drifted leaf is in the parent branch
at `drifted_pos` position.

Rows:
```
Leaf key S
Leaf value S
Leaf key C
Leaf value C
Drifted leaf (leaf in added branch)
```

Add case (S branch is placeholder):
```
  Branch S           || Branch C             
  Placeholder branch || Added branch
  Leaf S             || Leaf C
                      || Drifted leaf (this is Leaf S drifted into Added branch)
```

We need to compute the RLC of the drifted leaf. We compute the intermediate RLC
from the bytes in `LEAF_DRIFTED` row. And we retrieve the value from `LEAF_VALUE_S` row
(where there is the same leaf, but before it drifted down into a new branch).

Then we execute the lookup into a keccak table: `lookup(leaf_rlc, branch_child_at_drifted_pos_rlc)`.

### Leaf key in added branch: neighbour leaf in the deleted branch (C)

It needs to be ensured that the hash of the drifted leaf is in the parent branch
at `drifted_pos` position.

Rows:
```
Leaf key S
Leaf value S
Leaf key C
Leaf value C
Drifted leaf (leaf in added branch)
```

Delete case (C branch is placeholder):
```
  Branch S                        || Branch C             
  Branch to be deleted            || Placeholder branch
  Leaf S (leaf to be deleted)     || Leaf C
  Leaf to be drifted one level up || 
```

We need to compute the RLC of the leaf that is a neighbour leaf of the leaf that is to be deleted.
We compute the intermediate RLC from the bytes in `LEAF_DRIFTED` row.
And we retrieve the value from `LEAF_VALUE_C` row
(where there is the same leaf, but after it was moved one level up because of the deleted branch).

Then we execute the lookup into a keccak table: `lookup(leaf_rlc, branch_child_at_drifted_pos_rlc)`.

### Range lookups

Range lookups ensure that `s_main`, `c_main.rlp1`, `c_main.rlp2` columns are all bytes (between 0 - 255).

## Storage leaf non-existing-storage constraints

A storage leaf occupies 6 rows.
Contrary as in the branch rows, the `S` and `C` leaves are not positioned parallel to each other.
The rows are the following:
```
LEAF_KEY_S
LEAF_VALUE_S
LEAF_KEY_C
LEAF_VALUE_C
LEAF_DRIFTED
LEAF_NON_EXISTING
```

An example of leaf rows:
```
[226 160 49 236 194 26 116 94 57 104 160 78 149 112 228 66 91 193 143 168 1 156 104 2 129 150 181 70 209 102 156 32 12 104 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13]
[226 160 49 236 194 26 116 94 57 104 160 78 149 112 228 66 91 193 143 168 1 156 104 2 129 150 181 70 209 102 156 32 12 104 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]
[1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 14]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15]
[1 160 58 99 87 1 44 26 58 224 161 125 48 76 153 32 49 3 130 217 104 235 204 75 23 113 244 28 107 48 66 5 181 112 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 19]
```

In the above example, there is a wrong leaf case (see `s_rlp1` being 1 in the last row).
The constrainst here are analogue to the ones in `account_non_existing.rs`, but here it is for the
non existing storage instead of non existing account. However, more cases need to be handled for storage
because there can appear 1 (named `short`) or 2 RLP bytes (named `long`),
while for account there are always 2. Also, the selectors need
to be obtained differently - for example, when we are checking the leaf in the first (storage) level,
we are checking whether we are behind the account leaf (for account proof we are checking whether we
are in the first level).

Lookups:
The `non_existing_storage_proof` lookup is enabled in `LEAF_NON_EXISTING` row.

### Non existing storage proof leaf key RLC (leaf not in first level, branch not placeholder)

#### Storage leaf key acc s_advice0 (short)

If there is an even number of nibbles stored in a leaf, `s_bytes0` needs to be 32.

#### Storage key RLC (short)

Differently as for the other proofs, the storage-non-existing proof compares `key_rlc`
with the key stored in `STORAGE_NON_EXISTING` row, not in `LEAF_KEY` row.

The crucial thing is that we have a wrong leaf at the key (not exactly the same, just some starting
set of nibbles is the same) where we are proving there is no leaf.
If there would be a leaf at the specified key, it would be positioned in the branch where
the wrong leaf is positioned. Note that the position is determined by the starting set of nibbles.
Once we add the remaining nibbles to the starting ones, we need to obtain the enquired key.
There is a complementary constraint which makes sure the remaining nibbles are different for wrong leaf
and the non-existing leaf (in the case of wrong leaf, while the case with nil being in branch
is different).

#### Storage leaf key acc s_bytes1 (long)

If there is an even number of nibbles stored in a leaf, `s_bytes1` needs to be 32.

#### Storage key RLC (long)

Same as for `Storage key RLC (long)`, but here for the cases when there are two RLP bytes.

#### Wrong leaf sum check (short and long)

We compute the RLC of the key bytes in the `LEAF_NON_EXISTING` row. We check whether the computed
value is the same as the one stored in `accs.acc_c.rlc` column.

#### Wrong leaf sum_prev check (short and long)

We compute the RLC of the key bytes in the `STORAGE_NON_EXISTING` row. We check whether the computed
value is the same as the one stored in `accs.acc_c.mult` column.

#### Key of a leaf is different than key being inquired

The key in the `LEAF_KEY` row and the key in the LEAF_NON_EXISTING row are different.

#### Nil object in parent branch

In case when there is no wrong leaf, we need to check there is a nil object in the parent branch.
Note that the constraints in `branch.rs` ensure that `sel2` is 1 if and only if there is a nil object
at `modified_node` position. We check that in case of no wrong leaf in
the non-existing-storage proof, `is_nil_object` is 1.

### Non existing storage proof leaf key RLC

Ensuring that the storage does not exist when there is only one storage key in the storage trie.
Note 1: The hash of the only storage is checked to be the storage root in `leaf_value.rs`.
Note 2: There is no nil_object case checked in this gate, because it is covered in the gate
above. That is because when there is a branch (with nil object) in the first level,
it automatically means the leaf is not in the first level.

### Non existing account proof leaf address RLC (leaf in first level)

Similarly as the gate above, but for the account leaf being in the first level.

### Key of wrong leaf and the enquired key are of the same length

#### The number of nibbles in the wrong leaf and the enquired key are the same

This constraint is to prevent the attacker to prove that some key does not exist by setting
some arbitrary number of nibbles in the storage leaf which would lead to a desired RLC.

### s_main.bytes[i] = 0 when key ends

Key RLC is computed over all of `(s_main.bytes[0]), s_main.bytes[1], ..., s_main.bytes[31], c_main.rlp1, c_main.rlp2`
because we do not know the key length in advance.
To prevent changing the key and setting `s_main.bytes[i]` (or `c_main.rlp1/c_main.rlp2`) for
`i > key_len + 1` to get the desired key RLC, we need to ensure that
`s_main.bytes[i] = 0` for `i > key_len + 1`.

Note that the number of the key bytes in the `LEAF_NON_EXISTING` row needs to be the same as
the number of the key bytes in the `LEAF_KEY` row.

### Range lookups

Range lookups ensure that `s_main`, `c_main.rlp1`, `c_main.rlp2` columns are all bytes (between 0 - 255).
Note that `c_main.bytes` columns are not used.
