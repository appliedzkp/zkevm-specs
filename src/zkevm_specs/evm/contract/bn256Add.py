from ..instruction import Instruction
from ...util import FQ, Bn256AddGas
from ..table import (
    CallContextFieldTag,
    FixedTableTag,
    RW,
)


def bn256Add(instruction: Instruction):
    instruction.fixed_lookup(
        FixedTableTag.PrecompileInfo,
        FQ(instruction.curr.execution_state),
        instruction.call_context_lookup(CallContextFieldTag.CalleeAddress, RW.Read),
        FQ(Bn256AddGas),
    )

    caller_id = instruction.call_context_lookup(CallContextFieldTag.CallerId, RW.Read)
    call_data_offset = instruction.call_context_lookup(CallContextFieldTag.CallDataOffset, RW.Read)
    call_data_length = instruction.call_context_lookup(CallContextFieldTag.CallDataLength, RW.Read)
    return_data_offset = instruction.call_context_lookup(
        CallContextFieldTag.ReturnDataOffset, RW.Read
    )
    return_data_length = instruction.call_context_lookup(
        CallContextFieldTag.ReturnDataLength, RW.Read
    )

    gas_cost = FQ(Bn256AddGas)

    instruction.step_state_transition_to_restored_context(
        rw_counter_delta=instruction.rw_counter_offset,
        return_data_offset=FQ(0),
        return_data_length=return_data_length,
        gas_left=instruction.curr.gas_left - gas_cost,
        caller_id=caller_id,
    )
