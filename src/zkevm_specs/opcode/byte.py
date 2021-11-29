from typing import Sequence

from ..encoding import U8, is_circuit_code


@is_circuit_code
def check_byte(
    v8s: Sequence[U8],
    i8s: Sequence[U8],
    r8s: Sequence[U8],
):
    assert len(v8s) == len(i8s) == len(r8s) == 32

    # Any index value >= 256 always returns all zeros
    msb_sum_zero = sum(i8s[1:]) == 0

    # Byte 0:
    # Check byte per byte if we need to copy the value
    # to result. We're only directly checking the LSB byte
    # of the index here, so also make sure the byte
    # is only copied when index < 256.
    r = 0
    for i in range(32):
        selected = i8s[0] == i
        r += v8s[i] * msb_sum_zero * selected
    # Result needs to match the selected byte
    # (or equal to 0 when index >= 32)
    assert r == r8s[0]

    # Byte 1 to 31:
    for i in range(1, 32):
        assert r8s[i] == 0
