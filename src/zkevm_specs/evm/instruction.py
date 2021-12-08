from __future__ import annotations
from enum import IntEnum, auto
from typing import Optional, Sequence, Tuple, Union

from ..util import Array4, Array8, linear_combine, RLCStore
from .opcode import Opcode
from .step import StepState
from .table import (
    AccountFieldTag, CallContextFieldTag, Tables,
    FixedTableTag, TxContextFieldTag, RW, RWTableTag,
)


class ConstraintUnsatFailure(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class TransitionKind(IntEnum):
    Persistent = auto()
    Delta = auto()
    To = auto()


class Transition:
    kind: TransitionKind
    value: Optional[int]

    def __init__(self, kind: TransitionKind, value: Optional[int] = None) -> None:
        self.kind = kind
        self.value = value

    def persistent() -> Transition:
        return Transition(TransitionKind.Persistent)

    def delta(delta: int):
        return Transition(TransitionKind.Delta, delta)

    def to(to: int):
        return Transition(TransitionKind.To, to)


class Instruction:
    rlc_store: RLCStore
    tables: Tables
    curr: StepState
    next: StepState

    # helper numbers
    cell_offset: int = 0
    rw_counter_offset: int = 0
    program_counter_offset: int = 0
    stack_pointer_offset: int = 0
    state_write_counter_offset: int = 0

    def __init__(self, rlc_store: RLCStore, tables: Tables, curr: StepState, next: StepState) -> None:
        self.rlc_store = rlc_store
        self.tables = tables
        self.curr = curr
        self.next = next

    def constrain_zero(self, value: int):
        assert value == 0

    def constrain_equal(self, lhs: int, rhs: int):
        self.constrain_zero(lhs - rhs)

    def constrain_bool(self, value: int):
        assert value in [0, 1]

    def constrain_transfer(
        self,
        sender_address: int,
        receiver_address: int,
        value: int,
        gas_fee: int = 0,
        is_persistent: bool = True,
        rw_counter_end_of_reversion: int = 0,
    ):
        sender_balance, sender_balance_prev = self.account_write(
            sender_address, AccountFieldTag.Balance, is_persistent, rw_counter_end_of_reversion)
        receiver_balance, receiver_balance_prev = self.account_write(
            receiver_address, AccountFieldTag.Balance, is_persistent, rw_counter_end_of_reversion)

        value_with_gas_fee, overflow = self.add_word(value, gas_fee)
        self.constrain_zero(overflow)

        result, carry = self.add_word(value_with_gas_fee, sender_balance)
        self.constrain_equal(sender_balance_prev, result)
        self.constrain_zero(carry)

        result, carry = self.add_word(value, receiver_balance_prev)
        self.constrain_equal(receiver_balance, result)
        self.constrain_zero(carry)

    def constrain_state_transition(self, **kwargs: Transition):
        for key in [
            'rw_counter',
            'call_id',
            'is_root',
            'is_create',
            'opcode_source',
            'program_counter',
            'stack_pointer',
            'gas_left',
            'memory_size',
            'state_write_counter',
            'last_callee_id',
            'last_callee_returndata_offset',
            'last_callee_returndata_length',
        ]:
            curr, next = getattr(self.curr, key), getattr(self.next, key)
            transition = kwargs.get(key, Transition.persistent())
            if transition.kind == TransitionKind.Persistent:
                assert next == curr, \
                    ConstraintUnsatFailure(f"state {key} should be persistent as {curr}, but got {next}")
            elif transition.kind == TransitionKind.Delta:
                assert next == curr + transition.value, \
                    ConstraintUnsatFailure(f"state {key} should transit to ${curr + transition.value}, but got {next}")
            elif transition.kind == TransitionKind.To:
                assert next == transition.value, \
                    ConstraintUnsatFailure(f"state {key} should transit to ${transition.value}, but got {next}")
            else:
                raise ValueError("unreacheable")

    def constrain_new_context_state_transition(
        self,
        rw_counter: Transition,
        call_id: Transition,
        is_root: Transition,
        is_create: Transition,
        opcode_source: Transition,
        gas_left: Transition,
        state_write_counter: Transition,
    ):
        self.constrain_state_transition(
            rw_counter=rw_counter,
            call_id=call_id,
            is_root=is_root,
            is_create=is_create,
            opcode_source=opcode_source,
            gas_left=gas_left,
            state_write_counter=state_write_counter,
            # Initailization unconditionally
            program_counter=Transition.to(0),
            stack_pointer=Transition.to(1024),
            memory_size=Transition.to(0),
            last_callee_id=Transition.to(0),
            last_callee_returndata_offset=Transition.to(0),
            last_callee_returndata_length=Transition.to(0),
        )

    def constrain_same_context_state_transition(
        self,
        opcode: int,
        rw_counter: Transition = Transition.persistent(),
        program_counter: Transition = Transition.persistent(),
        stack_pointer: Transition = Transition.persistent(),
        memory_size: Transition = Transition.persistent(),
        dynamic_gas_cost: int = 0,
    ):
        gas_cost = Opcode(opcode).constant_gas_cost() + dynamic_gas_cost

        self.int_to_bytes(self.curr.gas_left - gas_cost, 8)

        self.constrain_state_transition(
            rw_counter=rw_counter,
            program_counter=program_counter,
            stack_pointer=stack_pointer,
            memory_size=memory_size,
            gas_left=Transition.delta(-gas_cost),
        )

    def is_zero(self, value: int) -> bool:
        return value == 0

    def is_equal(self, lhs: int, rhs: int) -> bool:
        return self.is_zero(lhs - rhs)

    def continuous_selectors(self, t: int, n: int) -> Sequence[int]:
        return [i < t for i in range(n)]

    def select(self, condition: bool, when_true: int, when_false: int) -> int:
        return when_true if condition else when_false

    def pair_select(self, value: int, lhs: int, rhs: int) -> Tuple[bool, bool]:
        return value == lhs, value == rhs

    def add_word(self, a: int, b: int) -> Tuple[int, bool]:
        a_bytes = self.rlc_to_bytes(a, 32)
        b_bytes = self.rlc_to_bytes(b, 32)

        a_lo = self.bytes_to_int(a_bytes[:16])
        a_hi = self.bytes_to_int(a_bytes[16:])
        b_lo = self.bytes_to_int(b_bytes[:16])
        b_hi = self.bytes_to_int(b_bytes[16:])
        carry_lo, c_lo = divmod(a_lo + b_lo, 1 << 128)
        carry_hi, c_hi = divmod(a_hi + b_hi + carry_lo, 1 << 128)

        c_bytes = c_lo.to_bytes(16, 'little') + c_hi.to_bytes(16, 'little')

        return self.rlc_store.to_rlc(c_bytes), carry_hi

    def mul_word_with_u64(self, word: int, u64: int) -> Tuple[int, int]:
        word_bytes = self.rlc_to_bytes(word, 32)

        word_q1 = self.bytes_to_int(word_bytes[:8])
        word_q2 = self.bytes_to_int(word_bytes[8:16])
        word_q3 = self.bytes_to_int(word_bytes[16:24])
        word_q4 = self.bytes_to_int(word_bytes[24:])

        carry_q1, result_q1 = divmod(word_q1 * u64, 1 << 64)
        carry_q2, result_q2 = divmod(word_q2 * u64 + carry_q1, 1 << 64)
        carry_q3, result_q3 = divmod(word_q3 * u64 + carry_q2, 1 << 64)
        carry_q4, result_q4 = divmod(word_q4 * u64 + carry_q3, 1 << 64)

        result_bytes = \
            result_q1.to_bytes(8, 'little') + \
            result_q2.to_bytes(8, 'little') + \
            result_q3.to_bytes(8, 'little') + \
            result_q4.to_bytes(8, 'little')

        return self.rlc_store.to_rlc(result_bytes), carry_q4

    def rlc_to_bytes(self, value: int, n_bytes: int) -> Sequence[int]:
        bytes = self.rlc_store.to_bytes(value)
        if len(bytes) > n_bytes and any(bytes[n_bytes:]):
            raise ConstraintUnsatFailure(f"{value} is too many bytes to fit {n_bytes} bytes")
        return list(bytes) + (n_bytes - len(bytes)) * [0]

    def bytes_to_rlc(self, bytes: Sequence[int]) -> int:
        return self.rlc_store.to_rlc(bytes)

    def int_to_bytes(self, value: int, n_bytes: int) -> Sequence[int]:
        try:
            return value.to_bytes(n_bytes, 'little')
        except OverflowError:
            raise ConstraintUnsatFailure(f"{value} is too many bytes to fit {n_bytes} bytes")

    def bytes_to_int(self, bytes: Sequence[int]) -> int:
        assert len(bytes) <= 31, "too many bytes to composite an integer in field"
        return linear_combine(bytes, 256)

    def byte_range_lookup(self, input: int):
        self.tables.fixed_lookup([FixedTableTag.Range256, input, 0, 0])

    def fixed_lookup(self, tag: FixedTableTag, inputs: Sequence[int]) -> Array4:
        return self.tables.fixed_lookup([tag] + inputs)

    def tx_lookup(self, tx_id: int, tag: TxContextFieldTag, index: int = 0) -> int:
        return self.tables.tx_lookup([tx_id, tag, index])[3]

    def bytecode_lookup(self, bytecode_hash: int, index: int) -> int:
        return self.tables.bytecode_lookup([bytecode_hash, index])[2]

    def rw_lookup(self, rw: RW, tag: RWTableTag, inputs: Sequence[int], rw_counter: Optional[int] = None) -> Array8:
        if rw_counter is None:
            rw_counter = self.curr.rw_counter + self.rw_counter_offset
            self.rw_counter_offset += 1

        return self.tables.rw_lookup([rw_counter, rw, tag] + inputs)

    def r_lookup(self, tag: RWTableTag, inputs: Sequence[int]) -> Array8:
        return self.rw_lookup(RW.Read, tag, inputs)

    def w_lookup(
        self,
        tag: RWTableTag,
        inputs: Sequence[int],
        is_persistent: bool = True,
        rw_counter_end_of_reversion: int = 0,
    ) -> Array8:
        row = 8 * [None]

        if tag.write_only_persistent():
            if is_persistent:
                row = self.rw_lookup(RW.Write, tag, inputs)
            return row

        row = self.rw_lookup(RW.Write, tag, inputs)

        if tag.write_with_reversion():
            rw_counter = rw_counter_end_of_reversion - self.curr.state_write_counter
            self.curr.state_write_counter += 1

            if not is_persistent:
                # Swap value and value_prev
                inputs = row[3:]
                if tag == RWTableTag.TxAccessListAccount:
                    inputs[2], inputs[3] = inputs[3], inputs[2]
                elif tag == RWTableTag.TxAccessListStorageSlot:
                    inputs[3], inputs[4] = inputs[4], inputs[3]
                elif tag == RWTableTag.Account:
                    inputs[2], inputs[3] = inputs[3], inputs[2]
                elif tag == RWTableTag.AccountStorage:
                    inputs[3], inputs[4] = inputs[4], inputs[3]
                elif tag == RWTableTag.AccountDestructed:
                    inputs[2], inputs[3] = inputs[3], inputs[2]
                self.rw_lookup(RW.Write, tag, inputs, rw_counter=rw_counter)

        return row

    def opcode_lookup(self) -> int:
        index = self.curr.program_counter + self.program_counter_offset
        self.program_counter_offset += 1

        return self.opcode_lookup_at(index)

    def opcode_lookup_at(self, index: int) -> int:
        if self.curr.is_root and self.curr.is_create:
            return self.tx_lookup(self.curr.opcode_source, TxContextFieldTag.Calldata, index)
        else:
            return self.bytecode_lookup(self.curr.opcode_source, index)

    def call_context_lookup(self, tag: CallContextFieldTag, rw: RW = RW.Read, call_id: Union[int, None] = None) -> int:
        if call_id is None:
            call_id = self.curr.call_id

        return self.rw_lookup(rw, RWTableTag.CallContext, [call_id, tag])[5]

    def stack_pop(self) -> int:
        stack_pointer_offset = self.stack_pointer_offset
        self.stack_pointer_offset += 1
        return self.stack_lookup(False, stack_pointer_offset)

    def stack_push(self) -> int:
        self.stack_pointer_offset -= 1
        return self.stack_lookup(True, self.stack_pointer_offset)

    def stack_lookup(self, rw: RW, stack_pointer_offset: int) -> int:
        stack_pointer = self.curr.stack_pointer + stack_pointer_offset
        return self.rw_lookup(rw, RWTableTag.Stack, [self.curr.call_id, stack_pointer])[5]

    def account_write(
        self,
        account_address: int,
        account_field_tag: AccountFieldTag,
        is_persistent: bool = True,
        rw_counter_end_of_reversion: int = 0,
    ) -> Tuple[int, int]:
        row = self.w_lookup(
            RWTableTag.Account,
            [account_address, account_field_tag],
            is_persistent,
            rw_counter_end_of_reversion,
        )
        return row[5], row[6]

    def account_read(self, account_address: int, account_field_tag: AccountFieldTag) -> Tuple[int, int]:
        row = self.r_lookup(RWTableTag.Account, [account_address, account_field_tag])
        return row[5], row[6]

    def add_account_to_access_list(
        self,
        tx_id: int,
        account_address: int,
        is_persistent: bool = True,
        rw_counter_end_of_reversion: int = 0,
    ) -> bool:
        row = self.w_lookup(
            RWTableTag.TxAccessListAccount,
            [tx_id, account_address],
            is_persistent,
            rw_counter_end_of_reversion,
        )
        return row[5] - row[6]

    def add_storage_slot_to_access_list(
        self,
        tx_id: int,
        account_address: int,
        storage_slot: int,
        is_persistent: bool = True,
        rw_counter_end_of_reversion: int = 0,
    ) -> bool:
        row = self.w_lookup(
            RWTableTag.TxAccessListAccount,
            [tx_id, account_address, storage_slot],
            is_persistent,
            rw_counter_end_of_reversion,
        )
        return row[5] - row[6]
