from ...util import FQ, N_BYTES_U64, RLC
from ..instruction import Instruction, Transition
from ..typing import Sequence


def sar(instruction: Instruction):
    opcode = instruction.opcode_lookup(True)

    a = instruction.stack_pop()
    shift = instruction.stack_pop()
    b = instruction.stack_push()

    (
        a64s,
        b64s,
        a64s_lo,
        a64s_hi,
        shf_div64,
        shf_mod64,
        p_lo,
        p_hi,
        a_is_neg,
    ) = __gen_witness(instruction, a, shift)
    __check_witness(
        instruction,
        a,
        shift,
        b,
        a64s,
        b64s,
        a64s_lo,
        a64s_hi,
        shf_div64,
        shf_mod64,
        p_lo,
        p_hi,
        a_is_neg,
    )

    instruction.step_state_transition_in_same_context(
        opcode,
        rw_counter=Transition.delta(2),
        program_counter=Transition.delta(1),
        stack_pointer=Transition.delta(1),
    )


def __check_witness(
    instruction: Instruction,
    a: RLC,
    shift: RLC,
    b: RLC,
    a64s: Sequence[FQ],
    b64s: Sequence[FQ],
    a64s_lo: Sequence[FQ],
    a64s_hi: Sequence[FQ],
    shf_div64,
    shf_mod64,
    p_lo,
    p_hi,
    a_is_neg,
):
    shf_lt256 = instruction.is_zero(instruction.sum(shift.le_bytes[1:]))

    for idx in range(4):
        offset = idx * N_BYTES_U64

        # a64s constraint
        instruction.constrain_equal(
            a64s[idx],
            instruction.bytes_to_fq(a.le_bytes[offset : offset + N_BYTES_U64]),
        )
        # `a64s[idx] == a64s_lo[idx] + a64s_hi[idx] * p_lo`
        instruction.constrain_equal(a64s[idx], a64s_lo[idx] + a64s_hi[idx] * p_lo)

        # `a64s_lo[idx] < p_lo`
        a64s_lo_lt_p_lo, _ = instruction.compare(a64s_lo[idx], p_lo, N_BYTES_U64)
        instruction.constrain_equal(a64s_lo_lt_p_lo, FQ(1))

    # b64s constraint
    for idx in range(4):
        offset = idx * N_BYTES_U64
        instruction.constrain_equal(
            b64s[idx] * shf_lt256 + a_is_neg * (1 - shf_lt256) * 0xffffffffffffffff,
            instruction.bytes_to_fq(b.le_bytes[offset : offset + N_BYTES_U64]),
        )

    # Constrain both `a` and `b` have same sign.
    b_is_neg = instruction.word_is_neg(b)
    instruction.constrain_equal(
        a_is_neg,
        instruction.word_is_neg(b),
    )

    # merge contraints
    shf_div64_eq0 = instruction.is_zero(shf_div64)
    shf_div64_eq1 = instruction.is_zero(shf_div64 - 1)
    shf_div64_eq2 = instruction.is_zero(shf_div64 - 2)
    shf_div64_eq3 = instruction.is_zero(shf_div64 - 3)
    hi_hi = a_is_neg * (0xffffffffffffffff - p_hi + 1)
    instruction.constrain_equal(
    b64s[0],
    (a64s_hi[0] + a64s_lo[1] * p_hi) * shf_div64_eq0
    + (a64s_hi[1] + a64s_lo[2] * p_hi) * shf_div64_eq1
    + (a64s_hi[2] + a64s_lo[3] * p_hi) * shf_div64_eq2
    + (a64s_hi[3] + hi_hi) * shf_div64_eq3
    + a_is_neg * 0xffffffffffffffff * (1 - shf_div64_eq0 - shf_div64_eq1 - shf_div64_eq2 - shf_div64_eq3),
    )
    instruction.constrain_equal(
    b64s[1],
    (a64s_hi[1] + a64s_lo[2] * p_hi) * shf_div64_eq0
    + (a64s_hi[2] + a64s_lo[3] * p_hi) * shf_div64_eq1
    + (a64s_hi[3] + hi_hi) * shf_div64_eq2
    + a_is_neg * 0xffffffffffffffff * (1 - shf_div64_eq0 - shf_div64_eq1 - shf_div64_eq2),
    )
    instruction.constrain_equal(
    b64s[2], (a64s_hi[2] + a64s_lo[3] * p_hi) * shf_div64_eq0 + (a64s_hi[3] + hi_hi) * shf_div64_eq1
    + a_is_neg * 0xffffffffffffffff * (1 - shf_div64_eq0 - shf_div64_eq1),
    )
    # gupeng
    instruction.constrain_equal(b64s[3], (a64s_hi[3] + hi_hi) *shf_div64_eq0 + a_is_neg * 0xffffffffffffffff * (1 - shf_div64_eq0))

    # shift constraint
    instruction.constrain_equal(
        instruction.bytes_to_fq(shift.le_bytes[:1]),
        shf_mod64 + shf_div64 * 64,
    )

    # `p_lo == pow(2, shf_mod64)` and `p_hi == pow(2, 64 - shf_mod64)`.
    instruction.pow2_lookup(shf_mod64, p_lo)
    instruction.pow2_lookup(64 - shf_mod64, p_hi)


def __gen_witness(instruction: Instruction, a: RLC, shift: RLC):
    shf0 = instruction.bytes_to_fq(shift.le_bytes[:1])
    shf_div64 = FQ(shf0.n // 64)
    shf_mod64 = FQ(shf0.n % 64)
    p_lo = FQ(1 << shf_mod64.n)
    p_hi = FQ(1 << (64 - shf_mod64.n))
    is_neg = instruction.word_is_neg(a)  # * is_opcode_sar

    a64s = instruction.word_to_64s(a)
    a64s_lo = [FQ(0)] * 4
    a64s_hi = [FQ(0)] * 4
    for idx in range(4):
        a64s_lo[idx] = FQ(a64s[idx].n % p_lo.n)
        a64s_hi[idx] = FQ(a64s[idx].n // p_lo.n)

    bb = instruction.select(
        is_neg,
        instruction.neg_word(RLC(-(-instruction.abs_word(a).int_value >> shf0.n))),
        RLC(a.int_value >> shf0.n),
    )
    b64s = [FQ((bb.int_value >> 64 * i) & 0xFFFFFFFFFFFFFFFF) for i in range(4)]

    return (
        a64s,
        b64s,
        a64s_lo,
        a64s_hi,
        shf_div64,
        shf_mod64,
        p_lo,
        p_hi,
        is_neg,
    )
