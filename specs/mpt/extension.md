# Extension node

## When is extension node added to the trie (and not a branch)

Let us say we add a new account `A1` to the trie. Let the account `A1` have the address
(in nibbles):
``` 
[8, 15, 1, 8, 7, ...]
``` 

Let us say there already exists an account `A` in the trie with the following nibbles:
```
[8, 15, 1, 8, 4, ...]
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

Thus we have:
```
                              Branch0
Node_0_0 Node_0_1 ...              Node_0_8                 ... Node_0_15
                                      |
                        Node_1_0 Node_1_1 ... Node_1_15
                                                  |
                                                  A
```

Now, we want to add `A1`. We cannot replace `A` with a branch because we would need to put both,
`A` and `A1` at position 1 (see the third nibble). We check how many nibbles from the third nibble on
the two accounts share and put these nibbles in the extension node. These nibbles are: `[1, 8]`.
So we have an extension of `[1, 8]` and then we place a branch `Branch2`. We put `A` in `Branch2`
at position 4 and we put `A1` in `Branch2` at position 7.

So we have:
```
                                             Branch0
Node_0_0 Node_0_1 ...                       Node_0_8                                   ... Node_0_15
                                               |
                           Node_1_0 Node_1_1 ...             Node_1_15
                                                                 |
                                        nil nil nil nil Node_2_4 nil nil Node_2_7 nil ... nil
                                                            |                |
                                                            A                A1
```

Extension node contains two parts: extension nibbles and hash of the underlying branch.
In our case, the extension node would contain `[1, 8]` and `Branch2` hash. Note that before `A1` has been
added, `Node_1_15` was the hash of `A`. After `A1` was added, `Node_1_15` is the hash of the extension node.

## getProof

The extension node returned by `getProof` contains the extension nibbles and the hash of the underlying branch.
An example extension node returned by `getProof` might be:
```
[228 130 0 150 160 215 121 207 40 14 160 149 115 175 222 139 45 208 88 81 65 226 190 111 191 208 252 147 90 105 163 154 4 132 52 204 121]
```

The first byte in this example (`228 = 192 + 36`) denotes the length (`36`) of the RLP stream (number of bytes behind the first byte).
The second byte (`130 = 128 + 2`) denotes the length of the bytes that contain the nibbles (`2`).
The third and fourth bytes are (compressed) nibbles.
The fifth byte (`160 = 128 + 32`) denotes the length of the hash of the underlying branch (`32`).
The remaning bytes represent the hash of the underlying branch.

The compressed nibbles are `[0, 150]`.
The nibbles of this extension node are: `[9, 4]` (`150 = 9 * 16 + 4`).
When the number of nibbles is even, the first byte of the compressed nibbles is always `0`.
When the number of nibbles is odd, the first byte is `16` + the first nibble.

For example, in `[226,16,160,172,105,12...`
we have only one nibble (`0`) and the compressed nibbles occupy only one byte (the second byte `16 = 16 + 0`).

In
`[223,16,221,198,132,32,0,0,0,1,198,132,32,0,0,0,1,128,128,128,128,128,128,128,128,128,128,128,128,128,128,128]`
we again have only one nibble, but the branch RLP stream is shorter than 32 bytes and is thus not hashed.
The third byte (`221 = 192 + 29`) denotes the length of the branch (`29).

A similar example but with more nibbles is:
```
[247,160,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,213,128,194,32,1,128,194,32,1,128,128,128,128,128,128,128,128,128,128,128,128,128]
```
Note that here the compressed nibbles are: `[16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]`,
thus all nibbles are `0`.

When the extension node contains more than `55` bytes:
```
[248,58,159,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,217,128,196,130,32,0,1,128,196,130,32,0,1,128,128,128,128,128,128,128,128,128,128,128,128,128]
```
In this case the second byte (`58`) denotes the length of the remaining stream. The third byte (`159 = 128 + 31`) denotes the
length of the bytes that store nibbles (`31`).

## Witness

Let us observe the following extension node:
```
[228 130 0 150 160 215 121 207 40 14 160 149 115 175 222 139 45 208 88 81 65 226 190 111 191 208 252 147 90 105 163 154 4 132 52 204 121]
[228 130 0 150 160 208 13 115 5 131 97 180 161 37 184 30 176 46 254 113 83 244 235 231 202 172 66 172 99 25 151 249 73 32 160 1 218]
```

The witness prepared
```
[130 0 150 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[160 215 121 207 40 14 160 149 115 175 222 139 45 208 88 81 65 226 190 111 191 208 252 147 90 105 163 154 4 132 52 204 121 0]
[0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[160 208 13 115 5 131 97 180 161 37 184 30 176 46 254 113 83 244 235 231 202 172 66 172 99 25 151 249 73 32 160 1 218 0]
```

The third row (`ExtensionBranchRowType::Nibbles`) contains the second nibbles of the key (the first row).
The range check `0 - 15` is applied on the third row (`ExtensionBranchRowType::Nibbles`) in `MainRLPGadget`.


TODO

## ExtensionGadget

`ExtensionGadget` (used in `ExtensionBranchConfig`) computes the state (key RLC, key multiplier, number of nibbles)
after the extension node nibbles.

```
pub(crate) struct ExtensionGadget<F> {
    rlp_key: ListKeyGadget<F>,
    is_not_hashed: LtGadget<F, 2>,
    is_key_part_odd: Cell<F>,
    mult_key: Cell<F>,

    // Post extension state
    post_state: Option<ExtState<F>>,
}
```




# Obsolete (to be updated)



## Extension node key constraints

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
[1 0 1 0 248 81 0 248 81 0 14 1 0 6 1 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 29 143 36 49 6 106 55 88 195 10 34 208 147 134 155 181 100 142 66 21 255 171 228 168 85 11 239 170 233 241 171 242 0 160 29 143 36 49 6 106 55 88 195 10 34 208 147 134 155 181 100 142 66 21 255 171 228 168 85 11 239 170 233 241 171 242 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[0 160 135 117 154 48 1 221 143 224 133 179 90 254 130 41 47 5 101 84 204 111 220 62 215 253 155 107 212 69 138 221 91 174 0 160 135 117 154 48 1 221 143 224 133 179 90 254 130 41 47 5 101 84 204 111 220 62 215 253 155 107 212 69 138 221 91 174 1]
[0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 128 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
[226 30 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 160 30 252 7 160 150 158 68 221 229 48 73 181 91 223 120 156 43 93 5 199 95 184 42 20 87 178 65 243 228 156 123 174 0 16]
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 160 30 252 7 160 150 158 68 221 229 48 73 181 91 223 120 156 43 93 5 199 95 184 42 20 87 178 65 243 228 156 123 174 0 17]
```

The last two rows present the extension node. This might be a bit misleading, because the extension
node appears in the trie above the branch (the first 17 rows).

The constraints in `extension_node_key.rs` check the intermediate
key RLC (address RLC) in the extension node is properly computed. Here, we need to take into
account the extension node nibbles and the branch `modified_node`.

Other constraints for extension nodes, like checking that the branch hash
is in the extension node (the bytes `[30 252 ... 174]` in extension node rows present the hash
of the underlying branch) or checking the hash of the extension is in the parent node are
checking in `extension_node.rs`.

### Extension node key RLC

When we have a regular branch (not in extension node), the key RLC is simple to compute:
```
key_rlc = key_rlc_prev + modified_node * key_rlc_mult_prev * selMult
```

The multiplier `selMult` being 16 or 1 depending on the number (even or odd) number
of nibbles used in the levels above.

Extension node makes it more complicated because we need to take into account its nibbles
too. If there are for example two nibbles in the extension node `n1` and `n2` and if we
assume that there have been even nibbles in the levels above, then:

```
key_rlc = key_rlc_prev + n1 * key_rlc_mult_prev * 16 + n2 * key_rlc_mult_prev * 1 +
    modified_node * key_rlc_mult_prev * r * 16     
```

#### Extension node row S and C key RLC are the same

Currently, the extension node S and extension node C both have the same key RLC -
however, sometimes extension node can be replaced by a shorter extension node
(in terms of nibbles), this is still to be implemented.

#### Long even sel1 extension node key RLC

We check the extension node intermediate RLC for the case when we have
long even nibbles (meaning there is an even number of nibbles and this number is bigger than 1)
and sel1 (branch `modified_node` needs to be multiplied by 16).

#### Long even sel1 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
```
key_rlc_branch = key_rlc_ext_node + modified_node * mult_prev * mult_diff * 16
```

Note that the multiplier used is `mult_prev * mult_diff`. This is because `mult_prev`
is the multiplier to be used for the first extension node nibble, but we then
need to take into account the number of nibbles in the extension node to have
the proper multiplier for the `modified_node`. `mult_diff` stores the power or `r`
such that the desired multiplier is `mult_prev * mult_diff`.
However, `mult_diff` needs to be checked to correspond to the length of the nibbles
(see `mult_diff` lookups below).

We check branch key RLC in `IS_EXTENSION_NODE_C` row (and not in branch rows),
otherwise +rotation would be needed
because we first have branch rows and then extension rows.

#### Long even sel1 extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = mult_prev * mult_diff`.

While we can use the expression `mult_prev * mult_diff` in the constraints in this file,
we need to have `key_rlc_mult_branch` properly stored because it is accessed from the
child nodes when computing the key RLC in child nodes.

#### Long odd sel2 first_nibble second_nibble

In some cases we need to store some helper values in `BRANCH.IS_EXTENSION_NODE_C` row.

For example in `long odd sel2` case. Long odd means there are odd number of nibbles and this
number is bigger than 1. `sel2` means there are odd number of nibbles above the branch. As long odd
means there are odd number of nibbles in the extension node, there are even
number of nibbles above the extension node:
`nibbles_above_branch = nibbles_above_ext_node + ext_node_nibbles`.

The example could be:
[228, 130, 16 + 3, 9*16 + 5, 0, ...]

In this example, we have three nibbles: `[3, 9, 5]`. Because the number of nibbles
is odd, we have the first nibble already at position `s_main.bytes[0]` (16 is added to the
first nibble in `hexToCompact` function). As opposed, in the example below where we have
two nibbles, we have 0 at `s_main.bytes[0]`:
[228,130,0,149,160,114,253,150,133,18,192,156,19,241,162,51,210,24,1,151,16,48,7,177,42,60,49,34,230,254,242,79,132,165,90,75,249]

To get the first nibble we need to compute `s_main.bytes[0] - 16`.

The additional helper values are needed in this case because
we have odd number of nibbles in the extension node.
When we have an even number of nibbles this is not needed, because all we need
is `n1 * 16 + n2`, `n3 * 16 + n4`, ... and we already have nibbles stored in that format
in the extension node.
When odd number, we have `n1 + 16`, `n2 * 16 + n3`, `n4 * 16 + n5`,...,
but we need `n1 * 16 + n2`, `n3 * 16 + n4`,... (actually we need this only if there
are also even number of nibbles above the extension node as is the case in long odd sel2).

To get `n1 * 16 + n2`, `n3 * 16 + n4`,...
from
`n1 + 16`, `n2 * 16 + n3`, `n4 * 16 + n5`,...
we store the nibbles `n3`, `n5`,... in
`BRANCH.IS_EXTENSION_NODE_C` row.

`BRANCH.IS_EXTENSION_NODE_S` and `BRANCH.IS_EXTENSION_NODE_C` rows of our example are thus:
[228, 130, 16 + 3, 9*16 + 5, 0, ...]
[5, 0, ...]

We name the values in `BRANCH.IS_EXTENSION_NODE_C` as `second_nibbles`.
Using the knowledge of `second_nibble` of the pair, we can compute `first_nibble`.
Having a list of `first_nibble` and `second_nibble`, we can compute the key RLC.

However, we need to check that the list of `second_nibbles` is correct. For example having
`first_nibble = 9 = ((9*16 + 5) - 5) / 16`
we check:
`first_nibble * 16 + 5 = s_main.bytes[1]`.

#### Long odd sel2 extension node key RLC

We check the extension node intermediate RLC for the case when we have
long odd nibbles (meaning there is an odd number of nibbles and this number is bigger than 1)
and sel2 (branch `modified_node` needs to be multiplied by 1).

Note that for the computation of the intermediate RLC we need `first_nibbles` and
`second_nibbles` mentioned in the constraint above.

#### Long odd sel2 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
```
key_rlc_branch = key_rlc_ext_node + modified_node * mult_prev * mult_diff * 1
```

#### Long odd sel2 extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = mult_prev * mult_diff * r_table[0]`.

Note that compared to `Long even sel1` case, we have an additional factor
`r` here. This is because we have even number of nibbles above the extension node
and then we have odd number of nibbles in the extension node: this means the multiplier
for `n1` (which is stored in `s_main.bytes[0]`) will need a multiplier  `key_rlc_mult_branch * r`.
For `n3` we will need a multiplier  `key_rlc_mult_branch * r^2`,...
The difference with `Long even sel1` is that here we have an additional nibble in
`s_main.bytes[0]` which requires an increased multiplier.

#### Short sel1 extension node key RLC

Short means there is one nibble in the extension node
sel1 means there are even number of nibbles above the branch,
so there are odd number of nibbles above the extension node in this case:
`nibbles_above_branch = nibbles_above_ext_node + 1`.

We check the extension node intermediate RLC for the case when we have
one nibble and sel1 (branch `modified_node` needs to be multiplied by 16).

#### Short sel1 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
`key_rlc_branch = key_rlc_ext_node + modified_node * mult_prev * mult_diff * 16`.

Note: `mult_diff = r` because we only have one nibble in the extension node.

#### Short sel1 extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = mult_prev * r_table[0]`.

#### Long even sel2 first_nibble second_nibble

`Long even sel2` case is similar to `Long odd sel1` case above - similar in a way
that we need helper values for `first_nibbles`.

Here we have an even number of nibbles in the extension node and this number is bigger than 1.
And `sel2` means branch `modified_node` needs to be multiplied by 1, which is the same as
saying there are odd number of nibbles above the branch.
It holds: `nibbles_above_branch = nibbles_above_ext_node + ext_node_nibbles`.
That means we have an odd number of nibbles above extension node.

Example:
`[228, 130, 0, 9*16 + 5, 0, ...]` // we only have two nibbles here (`even`)
`[5, 0, ...]`

We cannot use directly `n1 * 16 + n2` (`9*16 + 5` in the example) when computing the key RLC
because there is an odd number of nibbles above the extension node.
So we first need to compute: `key_rlc_prev_branch + n1 * key_rlc_mult_prev_branch`.
Which is the same as:
`key_rlc_prev_branch + (s_main.bytes[1] - second_nibble)/16 * key_rlc_mult_prev_branch`.

We then continue adding the rest of the nibbles.
In our example there is only one more nibble, so the extension node key RLC is:
`key_rlc_prev_branch + (s_main.bytes[1] - second_nibble)/16 * key_rlc_mult_prev_branch + first_nibble * key_rlc_mult_prev_branch * r * 16`.
Note that we added a factor `r` because we moved to a new pair of nibbles (a new byte).

In this constraints we check whether the list of `second_nibbles` is correct.

#### Long even sel2 extension node key RLC

We check the extension node intermediate RLC for the case when we have
long even nibbles (meaning there is an even number of nibbles and this number is bigger than 1)
and `sel2` (branch `modified_node` needs to be multiplied by 1).

Note that for the computation of the intermediate RLC we need `first_nibbles` and
`second_nibbles` mentioned in the constraint above.

#### Long even sel2 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
```
key_rlc_branch = key_rlc_ext_node + modified_node * key_rlc_mult_prev_branch * mult_diff * 1
```

#### Long even sel2 extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = key_rlc_mult_prev_branch * mult_diff * r_table[0]`.

#### Long odd sel1 extension node key RLC

`Long odd` means there is an odd number of nibbles and the number is bigger than 1.
`sel1` means there is an even number of nibbles above the branch.
Thus, there is an odd number of nibbles above the extension node.
Because of an odd number of nibbles in the extension node, we have the first
nibble `n1` stored in `s_main.bytes[0]` (actually `n1 + 16`). We multiply it with 
`key_rlc_mult_prev_branch`. Further nibbles are already paired in `s_main.bytes[i]`
for `i > 0` and we do not need information about `second_nibbles`.

#### Long odd sel1 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
```
key_rlc_branch = key_rlc_ext_node + modified_node * key_rlc_mult_prev_branch * mult_diff * 16
```

#### Long odd sel1 extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = key_rlc_mult_prev_branch * mult_diff`.

#### Short sel2 extension node key RLC

`Short` means there is only one nibble in the extension node.
`sel2` means there are odd number of nibbles above the branch. 
That means there are even number of nibbles above the extension node.

Because of `short`, we have the first (and only) nibble in `s_main.rlp2`.
We add this nibble to the previous key RLC to obtain the extension node key RLC.

#### Short sel2 extension node > branch key RLC

Once we have extension node key RLC computed we need to take into account also the nibble
corresponding to the branch (this nibble is `modified_node`):
`key_rlc_branch = key_rlc_ext_node + modified_node * key_rlc_mult_prev_branch`.

Note that there is no multiplication by power of `r` needed because `modified_node`
nibble uses the same multiplier as the nibble in the extension node as the two
of them form a byte in a key.

#### Short sel2 branch extension node > branch key RLC mult

We need to check that the multiplier stored in a branch is:
`key_rlc_mult_branch = key_rlc_mult_prev_branch * r`.

Note that we only need to multiply by `r`, because only one key byte is used
in this extension node (one nibble in extension node + modified node nibble).

#### s_main.bytes[i] = 0 for short

We need to ensure `s_main.bytes` are all 0 when short - the only nibble is in `s_main.rlp2`.
For long version, the constraints to have 0s after nibbles end in `s_main.bytes` are
implemented using `key_len_lookup`.

### Extension node key mult_diff

It needs to be checked that `mult_diff` value corresponds to the number
of the extension node nibbles. The information about the number of nibbles
is encoded in `s_main.rlp2` - except in `short` case, but in this case we only
have one nibble and we already know what value should have `mult_diff`.
Thus, we check whether `(RMult, s_main.rlp2, mult_diff)` is in `fixed_table`.

### Extension node second_nibble

It needs to be checked that `second_nibbles` stored in `IS_EXTENSION_NODE_C` row
are all between 0 and 15.

### s_main.bytes[i] = 0 after last extension node nibble

Note that for a short version (only one nibble), all
`s_main.bytes` need to be 0 (the only nibble is in `s_main.rlp2`) - this is checked
separately.

### Range lookups

Range lookups ensure that the values in columns are all bytes (0 - 255).

## Extension node constraints

### Extension node RLC

#### s_main RLC

The intermediate RLC after `s_main` bytes needs to be properly computed.

#### c_rlp2 = 160

When the branch is hashed, we have `c_rlp2 = 160` because it specifies the length of the
hash: `32 = 160 - 128`.

#### Hashed extension node RLC

Check whether the extension node RLC is properly computed.
The RLC is used to check whether the extension node is a node at the appropriate position
in the parent node. That means, it is used in a lookup to check whether
`(extension_node_RLC, node_hash_RLC)` is in the keccak table.

#### Non-hashed extension node RLC

Check whether the extension node (non-hashed) RLC is properly computed.
The RLC is used to check whether the non-hashed extension node is a node at the appropriate position
in the parent node. That means, there is a constraint to ensure that
`extension_node_RLC = node_hash_RLC` for some `node` in parent branch.

### Extension node selectors & RLP

#### Extension node selectors are boolean

We first check that the selectors in branch init row are boolean.

We have the following selectors in branch init:
```
is_ext_short_c16
is_ext_short_c1
is_ext_long_even_c16
is_ext_long_even_c1
is_ext_long_odd_c16
is_ext_long_odd_c1
```

`short` means there is only one nibble in the extension node, `long` means there
are at least two. `even` means the number of nibbles is even, `odd` means the number
of nibbles is odd. `c16` means that above the branch there are even number of
nibbles (the same as saying that `modified_node` of the branch needs to be
multiplied by 16 in the computation of the key RLC), `c1` means
that above the branch there are odd number of
nibbles (the same as saying that `modified_node` of the branch needs to be
multiplied by 1 in the computation of the key RLC).

#### Bool check extension node selectors sum

Only one of the six options can appear. When we have an extension node it holds:
`is_ext_short_c16 + is_ext_short_c1 + is_ext_long_even_c16 + is_ext_long_even_c1 + is_ext_long_odd_c16 + is_ext_long_odd_c1 = 1`.
And when it is a regular branch:
`is_ext_short_c16 + is_ext_short_c1 + is_ext_long_even_c16 + is_ext_long_even_c1 + is_ext_long_odd_c16 + is_ext_long_odd_c1 = 0`.

Note that if the attacker sets `is_extension_node = 1`
for a regular branch (or `is_extension_node = 0` for the extension node),
the final key RLC check fails because key RLC is computed differently
for extension nodes and regular branches - a regular branch occupies only one
key nibble (`modified_node`), while extension node occupies at least one additional
nibble (the actual extension of the extension node).

#### Branch c16/c1 selector - extension c16/c1 selector

`is_branch_c16` and `is_branch_c1` information is duplicated with
extension node selectors when we have an extension node (while in case of a regular
branch the extension node selectors do not hold this information).
That means when we have an extension node and `is_branch_c16 = 1`,
there is `is_ext_short_c16 = 1` or
`is_ext_long_even_c16 = 1` or `is_ext_long_odd_c16 = 1`.

We have such a duplication to reduce the expression degree - for example instead of
using `is_ext_long_even * is_branch_c16` we just use `is_ext_long_even_c16`.

But we need to check that `is_branch_c16` and `is_branch_c1` are consistent
with extension node selectors.

#### Long & even implies s_bytes0 = 0

This constraint prevents the attacker to set the number of nibbles to be even
when it is not even.
Note that when it is not even it holds `s_bytes0 != 0` (hexToCompact adds 16).

If the number of nibbles is 1, like in
`[226,16,160,172,105,12...`
there is no byte specifying the length.
If the number of nibbles is bigger than 1 and it is even, like in
`[228,130,0,149,160,114,253,150,133,18,192,156,19,241,162,51,210,24,1,151,16,48,7,177,42,60,49,34,230,254,242,79,132,165,90,75,249]`
the second byte (`s_main.rlp2`) specifies the length (we need to subract 128 to get it),
the third byte (`s_main.bytes[0]`) is 0.

#### One nibble & hashed branch RLP

We need to check that the length specified in `s_main.rlp1` corresponds to the actual
length of the extension node.

For example, in
`[226,16,160,172,105,12...`
we check that `226 - 192 = 1 + 32 + 1`.
1 is for `s_main.rlp2`, 32 is for 32 bytes of the branch hash,
1 is for the byte 160 which denotes the length
of the hash (128 + 32).

#### One nibble & non-hashed branch RLP

We need to check that the length specified in `s_main.rlp1` corresponds to the actual
length of the extension node.

For example, in
`[223,16,221,198,132,32,0,0,0,1,198,132,32,0,0,0,1,128,128,128,128,128,128,128,128,128,128,128,128,128,128,128]`
we check that `223 - 192 = 1 + 29 + 1`.
1 is for `s_main.rlp2`,
29 is for the branch RLP (which is not hashed because it is shorter than 32 bytes),
1 is for `c_main.bytes[0]` which denotes the length of the branch RLP.

####  More than one nibble & hashed branch & ext not longer than 55 RLP

We need to check that the length specified in `s_main.rlp1` corresponds to the actual
length of the extension node.

For example, in
`[228,130,0,149,160,114,253...`
we check that `228 - 192 = (130 - 128) + 1 + 32 + 1`.
1 is for `s_main.rlp2` which specifies the length of the nibbles part,
32 is for the branch hash,
1 is for the byte 160 which denotes the length
of the hash (128 + 32).

#### More than one nibble & non-hashed branch & ext not longer than 55 RLP

We need to check that the length specified in `s_main.rlp1` corresponds to the actual
length of the extension node.

We check that `s_main.rlp1 - 192` = `s_main.rlp2 - 128 + 1 + c_main.bytes[0] - 192 + 1`.

#### Extension longer than 55 RLP: s_rlp1 = 248

When extension node RLP is longer than 55 bytes, the RLP has an additional byte
at second position and the first byte specifies the length of the substream
that specifies the length of the RLP. The substream is always just one byte: `s_main.rlp2`.
And `s_main.rlp1 = 248` where `248 = 247 + 1` means the length of 1 byte.

Example:
`[248,67,160,59,138,106,70,105,186,37,13,38,205,122,69,158,202,157,33,95,131,7,227,58,235,229,3,121,188,90,54,23,236,52,68,161,160,...`

#### Hashed branch & ext longer than 55 RLP"

We need to check that the length specified in `s_main.rlp2` corresponds to the actual
length of the extension node.

Example:
`[248,67,160,59,138,106,70,105,186,37,13,38,205,122,69,158,202,157,33,95,131,7,227,58,235,229,3,121,188,90,54,23,236,52,68,161,160,...`

We check that `s_main.rlp2 = (s_main.bytes[0] - 128) + 1 + 32 + 1`.
`s_main.bytes[0] - 128` specifies the extension node nibbles part, 
1 is for `s_main.rlp2` which specifies the length of the RLP stream,
32 is for the branch hash,
1 is for the byte 160 which denotes the length of the hash (128 + 32). 

#### Non-hashed branch & ext longer than 55 RLP

We need to check that the length specified in `s_main.rlp2` corresponds to the actual
length of the extension node.

We check that `s_main.rlp2 = (s_main.bytes[0] - 128) + 1 + c_main.bytes[0] - 192 + 1`.
`s_main.bytes[0] - 128` specifies the extension node nibbles part, 
1 is for `s_main.rlp2` which specifies the length of the RLP stream,
`c_main.bytes[0] - 192` is for the branch RLP (which is not hashed because it is shorter than 32 bytes),
1 is for the byte 160 which denotes the length of the hash (128 + 32). 
                 
### Extension node branch hash in extension row

Check whether branch hash is in the extension node row - we check that the branch hash RLC
(computed over the first 17 rows) corresponds to the extension node hash stored in
the extension node row. That means `(branch_RLC, extension_node_hash_RLC`) needs to
be in a keccak table.

### Extension node branch hash in extension row (non-hashed branch)

#### Non-hashed branch in extension node

Check whether branch is in extension node row (non-hashed branch) -
we check that the branch RLC is the same as the extension node branch part RLC
(RLC computed over `c_main.bytes`).

Note: there need to be 0s after branch ends in the extension node `c_main.bytes`
(see below).

### c_main.bytes[i] = 0 after the last non-hashed branch byte 

There are 0s after non-hashed branch ends in `c_main.bytes`.

### Account first level extension node hash - compared to root

When we have an extension node in the first level of the account trie,
its hash needs to be compared to the root of the trie.

Note: the branch counterpart is implemented in `branch_hash_in_parent.rs`.

### Extension node in first level of storage trie - hash compared to the storage root

When extension node is in the first level of the storage trie, we need to check whether
`hash(ext_node) = storage_trie_root`. We do this by checking whether
`(ext_node_RLC, storage_trie_root_RLC)` is in the keccak table.

Note: extension node in the first level cannot be shorter than 32 bytes (it is always hashed).

### Extension node hash in parent branch

Check whether the extension node hash is in the parent branch.
That means we check whether
`(extension_node_RLC, node_hash_RLC)` is in the keccak table where `node` is a parent
brach child at `modified_node` position.

Note: do not check if it is in the first storage level (see `storage_root_in_account_leaf.rs`).

### Extension node in parent branch (non-hashed extension node)

#### Non-hashed extension node in parent branch

When an extension node is not hashed, we do not check whether it is in a parent 
branch using a lookup (see above), instead we need to check whether the branch child
at `modified_node` position is exactly the same as the extension node.

### Extension node number of nibbles (not first level)

We need to make sure the total number of nibbles is 64. This constraint ensures the number
of nibbles used (stored in branch init) is correctly computed - nibbles up until this
extension node + nibbles in this extension node.
Once in a leaf, the remaining nibbles stored in a leaf need to be added to the count.
The final count needs to be 64.

#### Nibbles number when one nibble

When there is only one nibble in the extension node, `nibbles_count` changes
for 2: one nibble and `modified_node` in a branch.

#### Nibbles number when even number of nibbles & ext not longer than 55

When there is an even number of nibbles in the extension node,
we compute the number of nibbles as: `(s_rlp2 - 128 - 1) * 2`.
By `s_rlp2 - 128` we get the number of bytes where nibbles are compressed, but
then we need to subtract 1 because `s_main.bytes[0]` does not contain any nibbles
(it is just 0 when even number of nibbles).

In the example below it is: `(130 - 128 - 1) * 2`.
`[228,130,0,149,160,114,253...`

#### Nibbles num when odd number (>1) of nibbles & ext not longer than 55

When there is an odd number of nibbles in the extension node,
we compute the number of nibbles as: `(s_rlp2 - 128) * 2`.
By `s_rlp2 - 128` we get the number of bytes where nibbles are compressed. We
multiply by 2 to get the nibbles, but then subtract 1 because in
`s_main.bytes[0]` there is only 1 nibble.

#### Nibbles num when even number of nibbles & ext longer than 55

When there is an even number of nibbles in the extension node and the extension
node is longer than 55 bytes, the number of bytes containing the nibbles
is given by `s_main.bytes[0]`.
We compute the number of nibbles as: `(s_bytes0 - 128 - 1) * 2`.
By `s_bytes0 - 128` we get the number of bytes where nibbles are compressed, but
then we need to subtract 1 because `s_main.bytes[1]` does not contain any nibbles
(it is just 0 when even number of nibbles).

#### Nibbles num when odd number (>1) of nibbles & ext longer than 55

When there is an odd number of nibbles in the extension node and the extension,
node is longer than 55 bytes, the number of bytes containing the nibbles
is given by `s_main.bytes[0]`.
We compute the number of nibbles as: `(s_main.bytes[0] - 128) * 2`.
By `s_main.bytes[0] - 128` we get the number of bytes where nibbles are compressed. We
multiply by 2 to get the nibbles, but then subtract 1 because in
`s_main.bytes[1]` there is only 1 nibble.

Example:
`[248,58,159,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,217,128,196,130,32,0,1,128,196,130,32,0,1,128,128,128,128,128,128,128,128,128,128,128,128,128]`

### Extension node number of nibbles (first level)

#### Nibbles num when one nibble (first level account)

When there is one nibble in the extension node and we are in the first account
level in the trie, the nibbles count has to be 2 (1 for nibble, 1 for
`modified_node` in a branch).

Note that we distinguish between first level in the account trie and first level
in the storage trie just because we have different selectors to trigger the
constraint for these two cases.





