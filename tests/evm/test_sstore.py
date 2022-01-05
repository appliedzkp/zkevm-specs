import pytest

TESTING_DATA = (
    (
        Transaction(caller_address=rand_address(), callee_address=rand_address()),
        bytes([i for i in range(32, 0, -1)]),
        bytes([i for i in range(0, 32, 1)]),
        False,
    ),
    (
        Transaction(caller_address=rand_address(), callee_address=rand_address()),
        bytes([i for i in range(32, 0, -1)]),
        bytes([i for i in range(0, 32, 1)]),
        True,
    ),
)

@pytest.mark.parametrize("tx, slot_be_bytes, value_be_bytes, result", TESTING_DATA)
def test_sstore(tx: Transaction, slot_be_bytes: bytes, value_be_bytes: bytes, result: bool):
    rlc_store = RLCStore()

    storage_slot = rlc_store.to_rlc(bytes(reversed(slot_be_bytes)))
    value = rlc_store.to_rlc(bytes(reversed(value_be_bytes)))

    # PUSH32 STORAGE_SLOT PUSH32 VALUE SSTORE STOP
    bytecode = Bytecode(f"7f{slot_be_bytes.hex()}7f{value_be_bytes.hex()}5500")
    bytecode_hash = rlc_store.to_rlc(bytecode.hash, 32)

    tables = Tables(
        tx_table=set(tx.table_assignments(rlc_store)),
        bytecode_table=set(bytecode.table_assignments(rlc_store)),
        rw_table=set(
            [   
                (9, RW.Read, RWTableTag.Stack, 1, 1022, storage_slot, 0, 0),
                (10, RW.Read, RWTableTag.Stack, 1, 1023, value, 0, 0),
                (11, RW.Write, RWTableTag.AccountStorage, tx.callee_address, storage_slot, value, 0, 0),
                (12, RW.Write, RWTableTag.TxAccessListStorageSlot, 1, tx.callee_address, storage_slot, 1, 0),
            ]
        ),
    )

    verify_steps(
        rlc_store=rlc_store,
        tables=tables,
        # TODO:
        steps=[
        ],
    )
