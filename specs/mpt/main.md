# Merkle Patricia Trie (MPT) Proof

MPT circuit checks that the modification of the trie state happened correctly.

Let us assume there are two proofs (as returned by `eth getProof`):

- A proof that there exists value `val1` at key `key1` for address `addr` in the state trie with root `root1`.
- A proof that there exists value `val2` at key `key1` for address `addr` in the state trie with root `root2`.

The circuit checks the transition from `val1` to `val2` at `key1` that led to the change
of trie root from `root1` to `root2`.

Similarly, MPT circuit can prove that `nonce`, `balance`, or `codehash` has been changed at
a particular address. But also, the circuit can prove that at the particular address no account exists
(`AccountDoesNotExist` proof), that at the particular storage key no value is stored (`StorageDoesNotExist` proof),
or that at the particular address an account has been deleted.

The circuit exposes a table which looks like:

| Address | ProofType               | Key  | ValuePrev     | Value        | RootPrev  | Root  |
| ------- | ----------------------- | ---- | ------------- | ------------ | --------- | ----- |
| $addr   | NonceChanged            | 0    | $noncePrev    | $nonceCur    | $rootPrev | $root |
| $addr   | BalanceChanged          | 0    | $balancePrev  | $balanceCur  | $rootPrev | $root |
| $addr   | CodeHashExists             | 0    | $codeHashPrev | $codeHashCur | $rootPrev | $root |
| $addr   | AccountDoesNotExist     | 0    | 0             | 0            | $root     | $root |
| $addr   | AccountDestructed       | 0    | 0             | 0            | $rootPrev | $root |
| $addr   | StorageChanged          | $key | $valuePrev    | $value       | $rootPrev | $root |
| $addr   | StorageDoesNotExist     | $key | 0             | 0            | $root     | $root |

Note that `StorageChanged` proof also supports storage leaf creation and storage leaf deletion,
`NonceChanged` also supports account leaf creation with nonce value and the rest of fields set to default, and
`BalanceChanged` also supports account leaf creation with balance value and the rest of fields set to default.

The proof returned by `eth getProof` looks like:

```
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": {
    "accountProof": [
      "0xf90211a...0701bc80",
      "0xf90211a...0d832380",
      "0xf90211a...5fb20c80",
      "0xf90211a...0675b80",
      "0xf90151a0...ca08080"
    ],
    "balance": "0x0",
    "codeHash": "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
    "nonce": "0x0",
    "storageHash": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
    "storageProof": [
      {
        "key": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
        "proof": [
          "0xf90211a...0701bc80",
          "0xf90211a...0d832380"
        ],
        "value": "0x1"
      }
    ]
  }
}
```

In the above case, the account proof contains five elements.
The first four are branches or extension nodes, the last one is an account leaf.
The hash of the account leaf is checked to
be in the fourth element (at the proper position - depends on the account address).
The hash of the fourth element is checked to be in the third element (at the proper position).
When we arrive to the top, the hash of the first element needs to be the same as trie root.

The storage proof in the above case contains two elements.
The first one is branch or extension node, the second element is a storage leaf.
The hash of the storage leaf is checked to
be in the first element at the proper position (depends on the key).

The hash of the first storage proof element (storage root) needs to be checked
to be in the account leaf of the last account proof element.

## Two parallel proofs

This section explains why the MPT circuit handles two parallel proofs at the
same time. One proof presents the state (might be denoted as `S` or `State`) of the trie
before the modification and the othe presents the state
of the trie after modification (might be denoted as `C` or `Change`).

We do not need to include the whole `C` proof in the witness as 15 out of 16 rows stay the same.
At each trie level, there is only one branch child that has been modified.

## Proof type

MPT circuit supports the following proofs:
 - NonceChanged
 - BalanceChanged
 - CodeHashExists
 - AccountDestructed
 - AccountDoesNotExist
 - StorageChanged
 - StorageDoesNotExist
 
## Constraints for different types of nodes

The constraints are grouped according to different trie node types:
 * Account leaf: [account-leaf.md](account-leaf.md)
 * Storage leaf: [storage-leaf.md](storage-leaf.md)
 * Branch and extension node: [branch.md](extension-branch.md)

There is a state machine `StateMachineConfig` that configures constraints for each of the nodes.
```
pub struct StateMachineConfig<F> {
    is_start: Column<Advice>,
    is_branch: Column<Advice>,
    is_account: Column<Advice>,
    is_storage: Column<Advice>,

    start_config: StartConfig<F>,
    branch_config: ExtensionBranchConfig<F>,
    storage_config: StorageLeafConfig<F>,
    account_config: AccountLeafConfig<F>,
}
```

There are no explicitly written constraints to enforce which nodes can follow which nodes, but the proper sequence of nodes
is implicitly implied by constraints for the total number of nibbles and constraints for hash of the node being included in the
parent node. The only explicit constraint of this kind is in `account_leaf.rs` to prevent having two or more account leaves
in the same proof:
```
config.main_data.is_below_account = false
```
A possible attack would be to have two storage proofs one after another (if there is not the whole proof, the total number of
nibbles fails), but the probability is negligible as the second storage trie would need to hash to 0 as it would
be compared to the first storage leaf which stores the default values (`parent_data.rlc = 0`).

The lookups to be executed by other circuits are enabled only in the account and storage rows. Even when there is no leaf returned
by `getProof` (for example for `AccountDestructed`), a placeholder leaf is added to the witness and the lookup is enabled
there (with all the constraints needed to ensure the leaf is only a placeholder). 

To ensure the initial state is set properly, there is the [start gadget](start.md).

## Proof chaining

One proof proves one modification. When two or more modifications are to be
proved to be correct, a chaining between proofs is needed.
That means we need to ensure:

```
current S state trie root = previous C state trie root
```

## Memory

There are certain values that need to be accumulated when traversing through the trie nodes. For example,
the account address RLC is being updated in each branch - the nibble that specifies which branch child is modified
contributes to the account address RLC.

To update the value in the current trie node, the value from the previous node needs to be retrieved.
For this reason, some kind of memory is needed. The circuit 
checks that the "memory" value is correct by executing a lookup.

This is achieved as follows. The previous node stores the value (that has been checked to be correct) in the lookup table (`store` instruction in the table below).
The current node executes the lookup (`load` instruction in the table below) with the value to check whether the "memorized" value is correct. Note that the key is used for a lookup - the key is important because at different stages (meaning different nodes) there are different correct values; the key acts as a counter and it ensures that only the value from the required stage is correct.

<table role="table">
<thead>
<tr>
<th>row</th>
<th>instruction</th>
<th>key</th>
<th>memory_value</th>
</tr>
</thead>
<tbody>
<tr>
<td>0</td>
<td>store(a)</td>
<td>0</td>
<td></td>
</tr>
<tr>
<td>1</td>
<td></td>
<td>1</td>
<td>a</td>
</tr>
<tr>
<td>2</td>
<td>load(key.cur(), a)</td>
<td>1</td>
<td></td>
</tr>
<tr>
<td>3</td>
<td></td>
<td>1</td>
<td></td>
</tr>
<tr>
<td>4</td>
<td>store(b)</td>
<td>1</td>
<td></td>
</tr>
<tr>
<td>5</td>
<td>load(key.cur(), b)</td>
<td>2</td>
<td>b</td>
</tr>
</tbody>
</table>

The memory mechanism is used for `MainData`, `ParentData`, and `KeyData`:

```
pub(crate) struct MainData<F> {
    pub(crate) proof_type: Cell<F>,
    pub(crate) is_below_account: Cell<F>,
    pub(crate) address_rlc: Cell<F>,
    pub(crate) root_prev: Cell<F>,
    pub(crate) root: Cell<F>,
}

pub(crate) struct ParentData<F> {
    pub(crate) rlc: Cell<F>,
    pub(crate) is_root: Cell<F>,
    pub(crate) is_placeholder: Cell<F>,
    pub(crate) drifted_parent_rlc: Cell<F>,
}

pub(crate) struct KeyData<F> {
    pub(crate) rlc: Cell<F>,
    pub(crate) mult: Cell<F>,
    pub(crate) num_nibbles: Cell<F>,
    pub(crate) is_odd: Cell<F>,
    pub(crate) drifted_rlc: Cell<F>,
    pub(crate) drifted_mult: Cell<F>,
    pub(crate) drifted_num_nibbles: Cell<F>,
    pub(crate) drifted_is_odd: Cell<F>,
}
```

## Nodes

There are three different nodes in the MPT:

  * Branch (and its special case Extension node)
  * Account leaf
  * Storage leaf

In the circuit, there is a special node added that marks the beggining and end of
the proof: `StartNode`. An example of the start node:

```
{"start":{"proof_type":"BalanceChanged"},"extension_branch":null,"account":null,"storage":null,"values":[[160,92,69,153,141,251,249,206,112,188,187,128,87,78,215,166,34,146,45,44,119,94,10,35,49,254,90,139,141,204,153,244,144,0],[160,125,24,72,139,179,78,113,251,49,243,102,147,31,42,67,250,44,213,59,218,72,77,153,183,213,188,44,45,1,156,32,62,0]],"keccak_data":[]}
```

Note that `values` contain the hashes of `S` and `C` tries. Also, `keccak_data` is empty as
there is no byte stream for which we need a hash.

An example of the end node:
```
{"start":{"proof_type":"Disabled"},"extension_branch":null,"account":null,"storage":null,"values":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"keccak_data":[]}
```

For each `Node` exactly one of the `start`, `extension_branch`, `account`, and `storage` is set
in the following struct:

```
pub struct Node {
    pub(crate) start: Option<StartNode>,
    pub(crate) extension_branch: Option<ExtensionBranchNode>,
    pub(crate) account: Option<AccountNode>,
    pub(crate) storage: Option<StorageNode>,
    /// MPT node values
    pub values: Vec<Vec<u8>>,
    pub keccak_data: Vec<Vec<u8>>,
}
```

The field `values` contains the RLP stream of a node split into rows and stripped off the
RLP encoding bytes (which are stored in `ExtensionBranchNode`, `AccountNode`, `StorageNode`).

The field `keccak_data` contains the RLP streams for which we need hash values.

## RLP encoding

Each node is a stream of bytes that is RLP encoded.
Some basic RLP constraints are implemented in [MainRLPGadget](gadgets.md), while others,
more node specific, are implemented in node configs. For example, `AccountLeafConfig`
contains constraints like:
```
require!(value_rlp_bytes[0] => RLP_LONG + 1);
```

The `MainRLPGadget` struct:
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

The `RLPItemGadget` determines using the first byte (see the function `decode_rlp` in
`rlp_gadgets.rs`) of the RLP stream what is the type of the stream.
If the first byte is smaller than `192` (`RLP_LIST_SHORT`), the stream is a string, otherwise a list.

```
pub(crate) struct RLPItemGadget<F> {
    pub(crate) value: RLPValueGadget<F>,
    pub(crate) list: RLPListGadget<F>,
}
```

The `MainRLPGadget` ensures the `RLPItemGadget` is properly based on the first byte of the RLP stream.
The node specific constraints are implemented in node configs and use either `RLPValueGadget` or
`RLPListGadget`.

## Placeholders

There are cases when the `S` and `C` proofs are not of the same length:

 * When one proof does not contain a storage leaf. For example, in the `S` proof
   we do not have a leaf as the value at the specified key has not be set yet.
   The value is then set and the `C` proof contains a storage leaf. In this case,
   to preserve the circuit layout, a placeholder storage leaf is added to the `S` proof.
 * When a leaf is replaced by a branch. For example, in the `S` proof we have a leaf at
   some key with nibbles `n1 n2 n3 n4 `, we then set a value at key `n1 n2 n3 n5` - the
   leaf at position `n1 n2 n3` turns into a branch with two leaves at positions `n4` and
   `n5`. In this case, the `S` proof does not have a branch and to preserve the layout we
   add a placeholder branch to it. 
 * When an extension node is replaced by another (shorter or longer) extension node.
   For example, we have an extension node at `n1 n2 n3 n4 n5 n6` with branch with two leaves
   at positions `n` and `m`. If we add a leaf at `n1 n2 n3 n4 n7` where `n5 != n7`,
   a new extension node is inserted at `n1 n2 n3 n4` with a new branch with an extension node
   at position `n5` (with only one nibble `n6`) and a leaf at position `n7`.
   In this case, the `S` proof contains the extension node at `n1 n2 n3 n4 n5 n6` and
   no underlying branch and leaf (the modification happens at `n1 n2 n3 n4 n7` and only
   an extension node is find there), thus we need to add a placeholder branch and a placeholder
   leaf.




