from typing import Sequence, Set, Tuple, Union
from enum import IntEnum, auto

from .opcode import (
    invalid_opcodes,
    state_write_opcodes,
    stack_underflow_pairs,
    stack_overflow_pairs,
    oog_constant_pairs,
)


class FixedTableTag(IntEnum):
    """
    Tag for FixedTable lookup, where the FixedTable is a prebuilt fixed-column
    table.
    """

    Range32 = auto()  # value, 0, 0
    Range64 = auto()  # value, 0, 0
    Range256 = auto()  # value, 0, 0
    Range512 = auto()  # value, 0, 0
    Range1024 = auto()  # value, 0, 0
    InvalidOpcode = auto()  # opcode, 0, 0
    StateWriteOpcode = auto()  # opcode, 0, 0
    StackOverflow = auto()  # opcode, stack_pointer, 0
    StackUnderflow = auto()  # opcode, stack_pointer, 0
    OOGConstant = auto()  # opcode, gas, 0


class TxTableTag(IntEnum):
    """
    Tag for TxTable lookup, where the TxTable is an instance-column table where
    part of it will be built by verifier.
    """

    Nonce = auto()
    Gas = auto()
    GasTipCap = auto()
    GasFeeCap = auto()
    CallerAddress = auto()
    CalleeAddress = auto()
    IsCreate = auto()
    Value = auto()
    CalldataLength = auto()
    Calldata = auto()


class RWTableTag(IntEnum):
    """
    Tag for RWTable lookup, where the RWTable an advice-column table built by
    prover, which will be part of State circuit and each unit read-write data
    will be verified to be consistent between each write.
    """

    TxAccessListAccount = auto()
    TxAccessListStorageSlot = auto()
    TxRefund = auto()

    AccountNonce = auto()
    AccountBalance = auto()
    AccountCodeHash = auto()
    AccountStorage = auto()
    AccountDestructed = auto()

    CallContext = auto()
    Stack = auto()
    Memory = auto()

    # For state writes which affect future execution before reversion, we need
    # to write them with reversion when the write might fail.
    def write_with_reversion(self) -> bool:
        return self in [
            RWTableTag.TxAccessListAccount,
            RWTableTag.TxAccessListStorageSlot,
            RWTableTag.AccountNonce,
            RWTableTag.AccountBalance,
            RWTableTag.AccountCodeHash,
            RWTableTag.AccountStorage,
        ]

    # For state writes which don't affect future execution before reversion, we
    # don't need to write them with reversion, instead we only need to write
    # them (enable the lookup) when is_persistent is True.
    def write_only_persistent(self) -> bool:
        return self in [
            RWTableTag.TxRefund,
            RWTableTag.AccountDestructed,
        ]


class CallContextTag(IntEnum):
    """
    Tag for RWTable lookup with tag CallContext, which is used to index specific
    field of CallContext.
    """

    # The following are read-only data inside a call, they will be written in
    # State circuit directly in their first row, and most of them will be
    # read and checked to be agreed with caller before the beginning of call.
    # It's not like transaction or bytecode that require specifically friendly
    # layout for verification, so maintaining the consistency directly in
    # RWTable seems more intuitive than creating another table for it.
    RWCounterEndOfReversion = auto()  # to know at which point in the future we should revert
    CallerCallId = auto()  # to know caller's id
    TxId = auto()  # to know tx's id
    Depth = auto()  # to know if call too deep
    CallerAddress = auto()
    CalleeAddress = auto()
    CalldataOffset = auto()
    CalldataLength = auto()
    ReturndataOffset = auto()  # for callee to set returndata to caller's memeory
    ReturndataLength = auto()
    Value = auto()
    Result = auto()  # to peek result in the future
    IsPersistent = auto()  # to know if current call is within reverted call or not
    IsStatic = auto()  # to know if state modification is within static call or not

    # The following are used by caller to save its own CallState when it's
    # going to dive into another call, and will be read out to restore caller's
    # CallState in the end by callee.
    # Note that stack and memory could also be included here, but since they
    # need extra constraints on their data format, so we separate them to be
    # different kinds of RWTableTag.
    IsRoot = auto()
    IsCreate = auto()
    OpcodeSource = auto()
    ProgramCounter = auto()
    StackPointer = auto()
    GasLeft = auto()
    MemorySize = auto()
    StateWriteCounter = auto()


class Tables:
    """
    A collection of lookup tables used in EVM circuit.
    """

    fixed_table: Set[Tuple[
        int,  # tag
        int,  # value1
        int,  # value2
        int,  # value3
    ]] = set(
        [(FixedTableTag.Range32, i, 0, 0) for i in range(32)] +
        [(FixedTableTag.Range64, i, 0, 0) for i in range(64)] +
        [(FixedTableTag.Range256, i, 0, 0) for i in range(256)] +
        [(FixedTableTag.Range512, i, 0, 0) for i in range(512)] +
        [(FixedTableTag.Range1024, i, 0, 0) for i in range(1024)] +
        [(FixedTableTag.InvalidOpcode, opcode, 0, 0) for opcode in invalid_opcodes()] +
        [(FixedTableTag.StateWriteOpcode, opcode, 0, 0) for opcode in state_write_opcodes()] +
        [(FixedTableTag.StackUnderflow, opcode, stack_pointer, 0) for (opcode, stack_pointer) in stack_underflow_pairs()] +
        [(FixedTableTag.StackOverflow, opcode, stack_pointer, 0) for (opcode, stack_pointer) in stack_overflow_pairs()] +
        [(FixedTableTag.OOGConstant, opcode, gas, 0) for (opcode, gas) in oog_constant_pairs()]
    )
    tx_table: Set[Tuple[
        int,  # tx_id
        int,  # tag
        int,  # index (or 0)
        int,  # value
    ]]
    bytecode_table: Set[Tuple[
        int,  # bytecode_hash
        int,  # index
        int,  # byte
    ]]
    rw_table: Set[Tuple[
        int,  # rw_counter
        int,  # is_write
        int,  # tag
        int,  # value1
        int,  # value2
        int,  # value3
        int,  # value4
        int,  # value5
    ]]

    def __init__(
        self,
        tx_table: Set[Tuple[int, int, int, int]],
        bytecode_table: Set[Tuple[int, int, int]],
        rw_table: Set[Tuple[int, int, int, int, int, int, int, int]],
    ) -> None:
        self.tx_table = tx_table
        self.bytecode_table = bytecode_table
        self.rw_table = rw_table

    def fixed_lookup(self, inputs: Union[Tuple[int, int, int, int], Sequence[int]]) -> bool:
        return tuple(inputs) in self.fixed_table

    def tx_lookup(self, inputs: Union[Tuple[int, int, int, int], Sequence[int]]) -> bool:
        return tuple(inputs) in self.tx_table

    def bytecode_lookup(self, inputs: Union[Tuple[int, int, int], Sequence[int]]) -> bool:
        return tuple(inputs) in self.bytecode_table

    def rw_lookup(self, inputs: Union[Tuple[int, int, int, int, int, int, int, int], Sequence[int]]) -> bool:
        return tuple(inputs) in self.rw_table
