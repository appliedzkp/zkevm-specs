# Start

`StartConfig` ensures the initial values in the [memory](main.md) lookup tables are set properly.
The memory mechanism is used for `MainData`, `ParentData`, and `KeyData`.

## MainData

For `MainData`, the `StartConfig` sets `proof_type`, `is_below_account`, `address_rlc`,
`root_prev`, and `root`.

The `proof_type` is set to one of the following:
 - NonceChanged = 1
 - BalanceChanged = 2
 - CodeHashExists = 3
 - AccountDestructed = 4
 - AccountDoesNotExist = 5
 - StorageChanged = 6
 - StorageDoesNotExist = 7

`is_below_account` is set to `false` as the proof always start with an account proof.
This value is later updated to `true` in the account leaf before the rows of the storage proof
begin - `is_below_account` acts as a selector to trigger constraints that are needed in the
first level of the storage proof (for example, checking the storage trie root being in the 
account leaf).

`address_rlc` is set to the account address RLC. This value is updated in the account leaf
to the storage key RLC.

`root_prev` and `root` are set to the previous and current root of the state trie.
These two values never change in the proof rows.

## ParentData

For `ParentData`, the `StartConfig` sets `rlc`, `is_root`, `is_placeholder`, and
`drifted_parent_rlc`.

`rlc` is set to the root of the state trie. This value is used to check that the RLC
of the node below is `rlc`. In the start case, this means that the RLC of the top element
of the trie is `rlc`. In the branch case, this means that the RLC of the modified element
in the branch is `rlc`. In the account leaf case, this means that the RLC of the top element
of the storage trie is `rlc`.

`is_root` is set to `true`. This value is set to `false` in all subsequent nodes.

`is_placeholder` is set to `false`. This value is set to `true` in the branches
that appear only as a placeholder in one of the two parallel proofs - in some cases
one of the proofs has one branch less than the other (details in branch documentation).

`drifted_parent_rlc` is set to the root of the state trie. This value is different from
`rlc` only in the case of a placeholder branch.

## KeyData

For `KeyData`, the `StartConfig` sets `rlc`, `mult`, `num_nibbles`, `is_odd`,
`drifted_rlc`, `drifted_mult`, `drifted_num_nibbles`, and `drifted_is_odd`.

`rlc` is set to `0`. This value is used for an intermediate address (or storage key when in storage proof) RLC.
In a branch, this value is updated by a modified nibble. In an extension node, this value is updated by extension
node nibbles. In an account leaf, this value is set to `0` as from this point on it is used for the storage key RLC).

`mult` value is set to `1`. This value stores the multiplier to be used for computing `rlc`.
For example:
```
rlc = 0
mult = 1

rlc = branch1_nibble * mult         // rlc after first branch
mult = r

rlc = rlc + branch2_nibble * mult   // rlc after second branch
mult = mult * r
```

`num_nibbles` is set to `0`. This value stores the number of branch / extension node nibbles that appeared up
to the current row. It is incremented by `1` in a branch node and by the number of extension node nibbles
in an extension node (plus `1` due to the position in branch).

`is_odd` is set to `false`. This value stores the information whether `num_nibbles` is odd or even.
This information is needed because the compact encoding of the remaining nibbles in the leaf is affected by
`num_nibbles` being odd or even.

`drifted_rlc` is set to `0`. This value is needed only when branch is a placeholder. In this case,
the underlying leaf (the placeholder branch appears only directly above the leaf) needs to use `rlc`
from the branch above the placeholder branch - `drifted_rlc` stores this value.

`drifted_mult` is set to `1`. Like for `drifted_rlc`, this value is needed only when branch is a placeholder.

`drifted_num_nibbles` is set to `0`. Like for `drifted_rlc` and `drifted_mult`,
this value is needed only when branch is a placeholder.

`drifted_is_odd` is set to `false`. Like for the above three values,
this value is needed only when branch is a placeholder.