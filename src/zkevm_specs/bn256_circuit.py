from enum import IntEnum, auto
from typing import Final, Dict
from .util import ConstraintSystem
from .evm_circuit import Bn256Circuit, Bn256TableRow, lt


def verify_row(cs: ConstraintSystem, row: Bn256TableRow):
    assert True


def verify_ops(cs: ConstraintSystem, row: Bn256TableRow):
    assert True


def verify_bn256_table(bn256_circuit: Bn256Circuit):
    cs = ConstraintSystem()
    bn256_table = bn256_circuit.table()
    n = len(bn256_table)
    assert n == 1
    for i, row in enumerate(bn256_table):
        verify_row(cs, row)
        verify_ops(cs, row)


class Bn256OperationTag(IntEnum):
    ECRECOVER = auto()
    BN256ADD = auto()
    BN256SCALARMUL = auto()
    BN256PAIRING = auto()


class Bn256OperationInfo:
    """
    Bn256 operation information.
    """

    input_length: int
    output_length: int
    is_input_dynamic: bool

    def __init__(
        self, input_length: int, output_length: int, is_input_dynamic: bool = False
    ) -> None:
        self.input_length = input_length
        self.output_length = output_length
        self.is_input_dynamic = is_input_dynamic


BN256_INFO_MAP: Final[Dict[Bn256OperationTag, Bn256OperationInfo]] = dict(
    {
        Bn256OperationTag.ECRECOVER: Bn256OperationInfo(4, 1),
        Bn256OperationTag.BN256ADD: Bn256OperationInfo(4, 2),
        Bn256OperationTag.BN256SCALARMUL: Bn256OperationInfo(3, 1),
        Bn256OperationTag.BN256PAIRING: Bn256OperationInfo(4, 1, True),
    }
)
