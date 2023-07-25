from zkevm_specs.evm_circuit.table import CallContextFieldTag, RW
from zkevm_specs.util.param import (
    GAS_COST_ACCOUNT_COLD_ACCESS,
    GAS_COST_FASTEST,
    GAS_COST_WARM_ACCESS,
    N_BYTES_MEMORY_ADDRESS,
)
from ...util import FQ
from ..instruction import Instruction
from ..opcode import Opcode
from ...util import N_BYTES_GAS


def error_oog_memory_copy(instruction: Instruction):
    # retrieve op code associated to oog constant error
    opcode = instruction.opcode_lookup(True)
    (
        is_calldata_copy,
        is_code_copy,
        is_ext_code_copy,
        is_return_data_copy,
    ) = instruction.multiple_select(
        opcode, (Opcode.CALLDATACOPY, Opcode.CODECOPY, Opcode.EXTCODECOPY, Opcode.RETURNDATACOPY)
    )

    # Constrain opcode must be one of CALLDATACOPY, CODECOPY, EXTCODECOPY or RETURNDATACOPY.
    instruction.constrain_equal(
        is_calldata_copy + is_code_copy + is_ext_code_copy + is_return_data_copy, FQ(1)
    )

    # EXTCODECOPY has one more extra stack pop for external address
    stack_offset = 0
    if is_ext_code_copy == FQ(1):
        external_address = instruction.stack_lookup(RW.Read, stack_offset)
        stack_offset += 1
    memory_offset_word = instruction.stack_lookup(RW.Read, stack_offset)
    copy_size_word = instruction.stack_lookup(RW.Read, stack_offset + 2)

    # Get constant gas cost
    if is_ext_code_copy == FQ(1):
        address = instruction.word_to_fq(external_address, N_BYTES_MEMORY_ADDRESS)
        tx_id = instruction.call_context_lookup(CallContextFieldTag.TxId)
        is_warm = instruction.read_account_to_access_list(tx_id, address)
        if is_warm == FQ(1):
            constant_gas = GAS_COST_WARM_ACCESS
        else:
            constant_gas = GAS_COST_ACCOUNT_COLD_ACCESS
    else:
        constant_gas = GAS_COST_FASTEST

    # get dynamic gas cost which includes memory expansion and memory copy
    memory_offset, copy_size = instruction.memory_offset_and_length(
        memory_offset_word, copy_size_word
    )
    _, memory_expansion_gas_cost = instruction.memory_expansion_dynamic_length(
        memory_offset, copy_size
    )
    dynamic_gas = instruction.memory_copier_gas_cost(copy_size, memory_expansion_gas_cost)

    # check gas left is less than total gas required
    gas_not_enough, _ = instruction.compare(
        instruction.curr.gas_left, constant_gas + dynamic_gas, N_BYTES_GAS
    )
    instruction.constrain_equal(gas_not_enough, FQ(1))

    instruction.constrain_error_state(
        instruction.rw_counter_offset + instruction.curr.reversible_write_counter + 1
    )
