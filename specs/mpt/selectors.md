# Selectors

It needs to be ensured:

 - The selectors denoting the row type are boolean values.
 - For sets of selectors that are mutually exclusive, it needs to be ensured that
   their sum is 1 (for example the selector for the proof type).
 - The proper order of rows.

#### Type of the row is set

The type of the row needs to be set (if all selectors would be 0 for a row, then all constraints
would be switched off).

#### Selectors need to be boolean values

It needs to be ensured that all selectors are boolean. To trigger the constraints for
a specific row the selectors could be of any nonnegative value, but being booleans
it makes it easier to write the constraints that ensure the subsets of constraints are
mutually exclusive and the constraints to ensure the proper order of rows.

#### is_storage_mod + is_nonce_mod + is_balance_mod + is_account_delete_mod + is_non_existing_account + is_codehash_mod = 1",

The type of the proof needs to be set.

#### Proof type corresponds to boolean proof type selectors

`proof_type` corresponds to `is_storage_mode, is_nonce_mod, ...`.

The correspondence is:
```
is_nonce_mod = 1
is_balance_mod = 2
is_codehash_mod = 3
is_non_existing_account_proof = 4
is_account_delete_mod = 5
is_storage_mod = 6
non_existing_storage_proof = 7
```

### Rows order ensured & proof type cannot change in rows corresponding to one modification

#### Branch init can appear only after certain row types

Branch init can start:

  - after another branch (means after extension node C)
  - after account leaf (account -> storage proof)
  - after storage leaf (after storage mod proof ends)
  - it can be in the first row.

#### Last branch row -> extension node S

Extension node S row follows the last branch row.

#### Extension node S -> extension node C",

Extension node C row follows the extension node S row.

#### Account leaf key S can appear only after certain row types

Account leaf key S can appear after extension node C (last branch row) or after
the last storage leaf row (if only one account in the trie).

#### Account leaf key S -> account leaf key C

Account leaf key C can appear only after account leaf key S.

#### Account leaf key C -> non existing account row

Non existing account row can appear only after account leaf key C row.

#### Non existing account row -> account leaf nonce balance S

Account leaf nonce balance S row can appear only after non existing account row.

#### Account leaf nonce balance S -> account leaf nonce balance C

Account leaf nonce balance C row can appear only after account leaf nonce balance S row. 

#### Account leaf nonce balance C -> account leaf storage codehash S

Account leaf storage codehash S row can appear only after account leaf nonce balance C row. 

#### Account leaf storage codehash S -> account leaf storage codehash C

Account leaf storage codehash C row can appear only after account leaf storage codehash S row. 

#### Account leaf storage codehash C -> account leaf added in branch

Account leaf in added branch row can appear only after account leaf storage codehash C row. 

#### Storage leaf key S follows extension node C or account leaf storage codehash C

Storage leaf key S row can appear after extension node C row or after account leaf storage codehash C.

#### Storage leaf key S -> storage leaf value S

Storage leaf value S row can appear only after storage leaf key S row.

#### Storage leaf value S -> storage leaf key C

Storage leaf key C row can appear only after storage leaf value S row.

#### Storage leaf key C -> storage leaf value C

Storage leaf value C row can appear only after storage leaf key C row.

#### Storage leaf value C -> storage leaf in added branch

Storage leaf in added branch row can appear only after storage leaf value C row.

#### Storage leaf in added branch -> storage leaf non existing row",

Storage non existing row can appear only after storage leaf in added branch.

#### In the first row only certain row types can occur

In the first row only account leaf key S row or branch init row can occur.

### Proof type can change only in certain rows

Proof type can change only in the first row of the first level.