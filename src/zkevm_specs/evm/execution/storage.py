from ..instruction import Instruction, Transition

def sload(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)
    instruction.constrain_equal(opcode, Opcode.SLOAD)

    tx_id = instruction.call_context_lookup(CallContextFieldTag.TxId)
    account_address = instruction.tx_lookup(tx_id, TxContextFieldTag.CalleeAddress)

    storage_slot = instruction.stack_pop()
    instruction.storage_read(tx_id, account_address, storage_slot)
    value = instruction.stack_push()

    # TDOO: deal with gas correctly
    instruction.constrain_same_context_state_transition(
        opcode,
        rw_counter=Transition.delta(3),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(0),
    )


def sstore(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)
    instruction.constrain_equal(opcode, Opcode.SSTORE)

    tx_id = instruction.call_context_lookup(CallContextFieldTag.TxId)
    account_address = instruction.tx_lookup(tx_id, TxContextFieldTag.CalleeAddress)
    is_persistent = instruction.call_context_lookup(CallContextFieldTag.IsPersistent)
    rw_counter_end_of_reversion = instruction.call_context_lookup(CallContextFieldTag.RWCounterEndOfReversion)

    storage_slot = instruction.stack_pop()
    value = instruction.stack_pop()
    self.add_storage_slot_to_access_list_with_reversion(
        tx_id, account_address, storage_slot, is_persistent, rw_counter_end_of_reversion
    )

    # TDOO: deal with gas correctly
    # TODO: constrain_new_context_state_transition?
    instruction.constrain_same_context_state_transition(
        opcode,
        rw_counter=Transition.delta(3),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(-2),
    )
