from ..instruction import Instruction, Transition
from ..table import CopyDataTypeTag
from zkevm_specs.util import FQ


def exp(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)

    # integer base, RLC encoded
    base_rlc = instruction.stack_pop()
    # integer exponent, RLC encoded
    exponent_rlc = instruction.stack_pop()
    # integer result of the exponential operation modulo 2**256, RLC encoded
    exp_rlc = instruction.stack_push()

    copy_rwc_inc, aux_value = instruction.copy_lookup(
        instruction.curr.call_id,
        CopyDataTypeTag.Exp,
        instruction.curr.call_id,
        CopyDataTypeTag.Exp,
        FQ.zero(),
        instruction.rlc_to_fq(exponent_rlc, n_bytes=31),
        FQ.zero(),
        instruction.rlc_to_fq(exponent_rlc, n_bytes=31),
        instruction.curr.rw_counter + instruction.rw_counter_offset,
    )

    instruction.constrain_zero(copy_rwc_inc)
    instruction.constrain_equal(exp_rlc, instruction.rlc_encode(aux_value, n_bytes=32))

    # TODO(rohit): 50 * exponent_byte_size
    dynamic_gas_cost = 0

    instruction.step_state_transition_in_same_context(
        opcode,
        rw_counter=Transition.delta(3),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(1),
        dynamic_gas_cost=dynamic_gas_cost,
    )
