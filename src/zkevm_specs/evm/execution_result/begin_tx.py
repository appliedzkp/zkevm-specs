from ...util import linear_combine, EMPTY_CODE_HASH
from ..step import Step
from ..table import TxTableTag, CallTableTag, RWTableTag
from .execution_result import ExecutionResult


def begin_tx(curr: Step, next: Step, r: int, is_first_step: bool):
    assert curr.core.call_id == curr.core.rw_counter

    tx_id = curr.call_lookup(CallTableTag.TxId)
    depth = curr.call_lookup(CallTableTag.Depth)

    if is_first_step:
        assert curr.core.rw_counter == 1
        assert tx_id == 1
        assert depth == 1

    tx_caller_address = curr.tx_lookup(tx_id, TxTableTag.CallerAddress)
    tx_callee_address = curr.tx_lookup(tx_id, TxTableTag.CalleeAddress)
    tx_value = curr.tx_lookup(tx_id, TxTableTag.Value)
    bytes_value = curr.decompress(tx_value, 32, r)
    tx_is_create = curr.tx_lookup(tx_id, TxTableTag.IsCreate)

    # Verify nonce
    tx_nonce = curr.tx_lookup(tx_id, TxTableTag.Nonce)
    nonce_prev = curr.w_lookup(RWTableTag.AccountNonce, [tx_caller_address])[1]
    assert tx_nonce == nonce_prev

    # TODO: Buy gas (EIP 1559)
    tx_gas = curr.tx_lookup(tx_id, TxTableTag.Gas)

    # TODO: Use intrinsic gas (EIP 2028, 2930)
    next_gas_left = tx_gas \
        - (53000 if tx_is_create else 21000)
    curr.bytes_range_lookup(next_gas_left, 8)

    # Prepare access list of caller
    curr.w_lookup(RWTableTag.TxAccessListAccount, [tx_id, tx_caller_address, 1])

    # Verify transfer
    rw_counter_end_of_revert = curr.call_lookup(CallTableTag.RWCounterEndOfRevert)
    is_persistent = curr.call_lookup(CallTableTag.IsPersistent)

    curr.assert_transfer(tx_caller_address, tx_callee_address, bytes_value,
                         is_persistent, rw_counter_end_of_revert, r)

    if tx_is_create:
        # TODO: Verify receiver address
        # TODO: Set next.call.opcode_source to tx_id
        raise NotImplementedError
    else:
        # Prepare access list of callee
        curr.w_lookup(RWTableTag.TxAccessListAccount, [tx_id, tx_callee_address, 1])

        code_hash = curr.r_lookup(RWTableTag.AccountCodeHash, [tx_callee_address])[0]
        is_empty_code_hash = curr.is_equal(code_hash, linear_combine(EMPTY_CODE_HASH, r))

        # TODO: Handle precompile
        if is_empty_code_hash:
            curr.assert_step_transition(
                next,
                rw_counter_diff=curr.rw_counter_diff,
                execution_result=ExecutionResult.BEGIN_TX,
                call_id=next.core.rw_counter,
            )
            assert next.peek_allocation(2) == tx_id + 1

            # TODO: Refund caller and tip coinbase
        else:
            # Setup next call's context
            tx_calldata_length = curr.tx_lookup(tx_id, TxTableTag.CalldataLength)

            [
                caller_address,
                callee_address,
                calldata_offset,
                calldata_length,
                value,
                is_static,
            ] = [
                curr.call_lookup(tag) for tag in [
                    CallTableTag.CallerAddress,
                    CallTableTag.CalleeAddress,
                    CallTableTag.CalldataOffset,
                    CallTableTag.CalldataLength,
                    CallTableTag.Value,
                    CallTableTag.IsStatic,
                ]
            ]

            assert caller_address == tx_caller_address
            assert callee_address == tx_callee_address
            assert value == tx_value
            assert calldata_offset == 0
            assert calldata_length == tx_calldata_length
            assert is_static == False

            curr.assert_step_transition(
                next,
                rw_counter_diff=curr.rw_counter_diff,
                execution_result_not=ExecutionResult.BEGIN_TX,
                is_root=True,
                is_create=tx_is_create,
                opcode_source=code_hash,
                program_counter=0,
                stack_pointer=1024,
                gas_left=next_gas_left,
                memory_size=0,
                state_write_counter=0,
                last_callee_id=0,
                last_callee_returndata_offset=0,
                last_callee_returndata_length=0,
            )
