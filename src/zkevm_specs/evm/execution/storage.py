from ..instruction import Instruction, Transition
from ..opcode import Opcode
from ..table import CallContextFieldTag, TxContextFieldTag

COLD_SLOAD_COST = 2100
WARM_STORAGE_READ_COST = 100
SLOAD_GAS = 100
SSTORE_SET_GAS = 20000
SSTORE_RESET_GAS = 2900
SSTORE_CLEARS_SCHEDULE = 15000

def sload(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)
    instruction.constrain_equal(opcode, Opcode.SLOAD)

    tx_id = instruction.call_context_lookup(CallContextFieldTag.TxId)
    rw_counter_end_of_reversion = instruction.call_context_lookup(CallContextFieldTag.RWCounterEndOfReversion)
    is_persistent = instruction.call_context_lookup(CallContextFieldTag.IsPersistent)
    callee_address = instruction.tx_lookup(tx_id, TxContextFieldTag.CalleeAddress)

    storage_slot = instruction.stack_pop()
    warm = instruction.access_list_storage_slot_read(tx_id, callee_address, storage_slot)

    # TODO: Use intrinsic gas (EIP 2028, 2930)
    dynamic_gas_cost = WARM_STORAGE_READ_COST if warm else COLD_SLOAD_COST

    instruction.storage_slot_read(callee_address, storage_slot)
    instruction.add_storage_slot_to_access_list_with_reversion(
        tx_id, callee_address, storage_slot, is_persistent, rw_counter_end_of_reversion
    )
    value = instruction.stack_push()

    instruction.constrain_same_context_state_transition(
        opcode,
        rw_counter=Transition.delta(5),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(0),
        state_write_counter=Transition.delta(1),
        dynamic_gas_cost=dynamic_gas_cost,
    )


def sstore(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)
    instruction.constrain_equal(opcode, Opcode.SSTORE)

    tx_id = instruction.call_context_lookup(CallContextFieldTag.TxId)
    rw_counter_end_of_reversion = instruction.call_context_lookup(CallContextFieldTag.RWCounterEndOfReversion)
    is_persistent = instruction.call_context_lookup(CallContextFieldTag.IsPersistent)
    callee_address = instruction.tx_lookup(tx_id, TxContextFieldTag.CalleeAddress)

    storage_slot = instruction.stack_pop()
    value = instruction.stack_pop()
    instruction.access_list_storage_slot_read(tx_id, callee_address, storage_slot)

    # TODO: Use intrinsic gas (EIP 2028, 2930)
    dynamic_gas_cost = 0

    instruction.storage_slot_write_with_reversion(
        callee_address, storage_slot, is_persistent, rw_counter_end_of_reversion
    )
    instruction.add_storage_slot_to_access_list_with_reversion(
        tx_id, callee_address, storage_slot, is_persistent, rw_counter_end_of_reversion
    )

    instruction.constrain_same_context_state_transition(
        opcode,
        rw_counter=Transition.delta(5),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(2),
        state_write_counter=Transition.delta(2),
        dynamic_gas_cost=dynamic_gas_cost,
    )
