# MPT circuit scope

The analysis of the MPT circuit scope has been done
[here](https://hackmd.io/nI_STO5HQ4G-ugKnQEzctg?view).
It was analyzed what trie transformations need to be supported by the MPT circuit.
In what follows we explain the correspondence between the transformations and the implementation.

## Trie transformations

Notation:

- L Leaf without branch {L local_path}
- B Branch { node1 node2 .... node16 value} (note value is always empty)
- BL Leaf inside a branch {BL local_path value}(note value is ommited by default)
- H Hash
- E Extension {E local_path}
- a full path is the path from the root
- a local path is the path contained inside a leaf, extension or branch (in the case of branch is the position in the array).

Note: only insert is considered as delete is its inverse - the implementation of insert and delete is
the same, it is just that S and C proof are reversed.

### Insert in an empty trie

Create al L node

```
{L}
```

There are no nodes in the S tree. There is only one L node in the C trie.

Note that when there is no leaf in S proof, a placeholder (an empty leaf) is added to maintain
the layout (having a placeholder leaf in S proof in the same rows as there is a newly added leaf in C proof).
So in the case of adding a leaf to an empty trie, we will have a placeholder leaf in
S proof and a newly added leaf in a C proof.

Two cases need to be considered: account leaf and storage leaf.

#### Account leaf

For the account leaf, the constraints are implemented in `account_leaf` folder.
The selector `not_first_level` is used to check whether we are in the first level or not. Being in the first
level means we are adding a leaf to an empty trie.
The case for being in the first level needs to be handled in all `account_leaf` files, except in
`account_leaf_nonce_balance.rs`, where mostly intermediate RLCs are checked and there are no checks
that involve parent element (parent element being trie root when in the first level).
Also it is not needed for `account_leaf_key_in_added_branch.rs`:
a leaf cannot appear in the first element when it is added to a new branch. Just as a note -
in `account_leaf_key_in_added_branch.rs` we need to check whether the parent element is in a first
level or not.

In `account_leaf_key.rs` we need to consider being in the first level when computing the account
address RLC - when in the first level we do not take the value from the parent branch as there is none,
all 64 nibbles of the address are stored in a leaf.
In `account_leaf_storage_codehash.rs` we need to compare the leaf RLC (its hash) with the element in
the parent branch or with trie root if in the first level.
In `account_non_existing.rs` we need to ensure that the leaf is a placeholder when we are in an empty trie.

#### Storage leaf

For the storage leaf, the constraints are implemented in `storage_leaf` folder.
Similarly as for the account leaf we need to check whether we are in the first level or not. But here
we need to check whether we are in the first storage level - this is done by checking whether the storage
leaf appears immediately after the account leaf. Also, instead of checking the hash of the leaf being
the state trie root, we check whether it is the storage trie root.

The constraints are analogous to the account leaf ones, but there are also many differences: the storage
leaf RLP bytes that determine the leaf length can appear in two versions (1 byte or 2 bytes), we do
not have a nonce, balance, storage trie root, and codehash here, we only have a leaf value. Nevertheless,
as far as the first level checks go, the constraints are analogous (`leaf_key.rs`, `leaf_value.rs`).

### Insert when branching occurs in a B

E.g. L full path = 123 E 7890

If L overflows, set hash inthe branch and create a new L node
By overflows it is meant that the node exceeds 31 bytes and is thus hashed.
```
{E 123}
   {. . h . . . . . . . . h . . . . . . .}
=> insert 123 E 7890
{E 123}
   {. . h . . . . . . . . h . *H . . . . .}
```
                              *{L 7890}
If L does NOT overflows, set BL node inside B
```
{E 123}
   {. . h . . . . . . . . h . . . . . . .}
=> insert 123 E 7890
{E 123}
   {. . h . . . . . . . . h . *{L 7890} . . . . .}
```

The hash of a leaf (or raw leaf if shorter than 32 bytes) is checked to be at the proper position
in the parent branch in `account_leaf_storage_codehash.rs` for account leaf and in
`leaf_value.rs` for storage leaf.
Note that the account leaf is always hashed as it is always longer than 31 bytes. For storage leaf
we use a selector `not_hashed` in `leaf_value.rs` to consider the two cases.

### Insert when branching occurs in L

(1) Optionally create an extension if between the existing leaf and the leaf to insert shares a prefix in local_path

```
{E 123}
  {. . h . . . . . . . . H . . . . . . .}
                         {L 456789}
=> insert 123 B 456 AAA
{E 123}
  {. . h . . . . . . . . *H . . . . . . .}
                         *{E 456}
                           *{. . . . . . . . . . . . . . . .}
(2) After, create BL or L.
```

This case is handled in the same way as the case below (branching in BL).

### Insert when branching occurs in BL

If NOT overflows is embeded into branch
```
{. . H . . . . . . . . {456789 BL} . . . . . . .}
=> insert B456 7 99
{. . H . . . . . . . . *H . . . . . .}
                       *{E B456}
                          *{. . . . . . . {BL 89} . {BL 99} . . . . . . .}
```

If overflows a new leaf is created

```
{. . H . . . . . . . . {BL 456789} . . . . . . .}
=> insert B456 7 99
{. . H . . . . . . . . *H . . . . . .}
                        *{E B456}
                          *{. . . . . . . {BL 89} . H . . . . . . .}
                                                    *{BL 99}
```

When a leaf is added to the position where some leaf already existed,
a new branch is inserted. The constraints for an account leaf in a newly added branch are implemented
in `account_leaf_key_in_added_branch.rs` and for a storage leaf in `leaf_key_in_added_branch.rs`.

Note that a branch placeholder is inserted to maintain the layout. That means that a placeholder
branch is in S proof in the same rows as the newly added branch in C proof.

### Insert when branching occurs in E

If branching is not in the last nibble
```
{E 1234}
   { . . . . . 5 . 7 . . . . . . . . . }
=> insert 1111
{E 1}
   { . 1 2 . . . . . . . . . . . . . . }  
         {E 3 4}
            { . . . . . 5 . 7 . . . . . . . . . }
       {x 11}
```

If branching is in the last nibble
```
{E 1234}
   { . . . . . 5 . 7 . . . . . . . . . }
=> insert 1233
{E 123}
   { . . . 3 4 . . . . . . . . . . . . }
             { . . . . . 5 . 7 . . . . . . . . . }
           {x 3}
```

For cases when a leaf is added to a branch that is inside an extension node, it needs to be checked
that the branch hash is in the extension node `extension_node.rs`. Also, it needs to be checked that
the intermediate address or key RLC (depending whether in account proof or storage proof) is properly
computed - extension node nibbles need to be considered (`extension_node_key.rs`).

For cases when additional extension node need to be inserted, the implementation is not ready yet.

### Update L & Update BL

If overflows and the node is a branch, embed the node inside the branch
```
{. . . . . . . H . . . H  . . . .}
                       {L}
=>
{. . . . . . . H . . . *L . . . .}
```

else: update L node
```
{. . . . . . . H . . . L  . . . .}
=>
{. . . . . . . H . . . *L . . . .}
```

Updating requires checking everything what is checked for inserting a new leaf, but here we do not
have a placeholder leaf or a placeholder branch.
The checks that are common are:

 * checks that the change occurs only at the given address/key - all other branch rows
 are the same in S and C proof (`branch.rs`)
 * checks that the modification propagates properly by changed hashes in all the parent elements up
 to the root (`branch_hash_in_parent.rs`, `extension_node.rs`)
 * checks that the hash of the element is in the parent branch or the same as trie root
 (`account_leaf_storage_codehash.rs` and `leaf_value.rs`)
 * checks that the node RLC is properly computed (`branch_rlc.rs` for branches, `account_leaf_key.fs`,
 `account_leaf_nonce_balance.rs`, `account_leaf_storage_codehash.rs` for account leaf, and
 `leaf_key.rs` and `leaf_value.rs` for storage leaf, `extension_node.rs` for extension node)
 * checks that the intermediate address or key RLC (depending whether we are in account or storage proof)
 is properly computed (`branch_key.rs` for branches, `extension_node_key.rs` for extension nodes).