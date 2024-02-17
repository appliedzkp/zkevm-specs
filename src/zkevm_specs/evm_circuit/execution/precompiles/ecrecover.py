from dataclasses import dataclass
from zkevm_specs.evm_circuit.instruction import Instruction
from zkevm_specs.evm_circuit.table import (
    CallContextFieldTag,
    FixedTableTag,
    RW,
)
from zkevm_specs.util import FQ, Word, EcrecoverGas
from zkevm_specs.util.arithmetic import RLC

SECP256K1N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


@dataclass(frozen=True)
class PrecompileAuxData:
    msg_hash: Word
    sig_v: Word
    sig_r: Word
    sig_s: Word
    recovered_addr: FQ
    input_rlc: FQ
    output_rlc: FQ


def ecRecover(instruction: Instruction):
    is_success = instruction.call_context_lookup(CallContextFieldTag.IsSuccess, RW.Read)
    address_word = instruction.call_context_lookup_word(CallContextFieldTag.CalleeAddress)
    address = instruction.word_to_address(address_word)
    instruction.fixed_lookup(
        FixedTableTag.PrecompileInfo,
        FQ(instruction.curr.execution_state),
        address,
        FQ(EcrecoverGas),
    )

    # Get msg_hash, signature and recovered address from aux_data
    aux_data: PrecompileAuxData = instruction.curr.aux_data[0]
    msg_hash = aux_data.msg_hash
    sig_v = aux_data.sig_v
    sig_r = aux_data.sig_r
    sig_s = aux_data.sig_s
    recovered_addr = aux_data.recovered_addr
    keccak_randomness: FQ = instruction.curr.aux_data[1]

    is_recovered = FQ(instruction.is_zero(recovered_addr) != FQ(1))

    # Verify input and output
    input_bytes = bytearray(b"")
    input_bytes.extend(msg_hash.int_value().to_bytes(32, "little"))
    input_bytes.extend(sig_v.int_value().to_bytes(32, "little"))
    input_bytes.extend(sig_r.int_value().to_bytes(32, "little"))
    input_bytes.extend(sig_s.int_value().to_bytes(32, "little"))
    input_rlc = RLC(bytes(reversed(input_bytes)), keccak_randomness, n_bytes=128).expr()
    instruction.constrain_equal(aux_data.input_rlc, input_rlc)

    output_rlc = RLC(
        bytes(reversed(recovered_addr.n.to_bytes(32, "little"))), keccak_randomness, n_bytes=32
    ).expr()
    instruction.constrain_equal(aux_data.output_rlc, output_rlc)

    # is_success is always true
    # ref: https://github.com/ethereum/execution-specs/blob/master/src/ethereum/shanghai/vm/precompiled_contracts/ecrecover.py
    instruction.constrain_equal(is_success, FQ(1))

    # verify r and s
    sig_r_upper_bound, _ = instruction.compare_word(sig_r, Word(SECP256K1N))
    sig_s_upper_bound, _ = instruction.compare_word(sig_s, Word(SECP256K1N))
    sig_r_is_non_zero = FQ(instruction.is_zero_word(sig_r) != FQ(1))
    sig_s_is_non_zero = FQ(instruction.is_zero_word(sig_s) != FQ(1))
    valid_r_s = instruction.is_equal(
        sig_r_upper_bound + sig_s_upper_bound + sig_r_is_non_zero + sig_s_is_non_zero, FQ(4)
    )

    # verify v
    is_equal_27 = instruction.is_equal_word(sig_v, Word(27))
    is_equal_28 = instruction.is_equal_word(sig_v, Word(28))
    valid_v = instruction.is_equal(is_equal_27 + is_equal_28, FQ(1))

    if valid_r_s + valid_v == FQ(2):
        # sig table lookups
        instruction.sig_lookup(
            msg_hash, sig_v.lo.expr() - FQ(27), sig_r, sig_s, recovered_addr, is_recovered
        )
    else:
        instruction.constrain_zero(is_recovered)
        instruction.constrain_zero(recovered_addr)

    # Restore caller state to next StepState
    instruction.step_state_transition_to_restored_context(
        rw_counter_delta=instruction.rw_counter_offset,
        return_data_offset=FQ.zero(),
        return_data_length=FQ(32) if is_recovered == FQ(1) else FQ.zero(),
        gas_left=instruction.curr.gas_left - EcrecoverGas,
    )
