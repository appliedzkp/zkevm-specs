# Simulate EVM storage

from ..encoding import U256

# TODO: should be in state

class Storage:
    def __init__(self):
        self.data = {}

    def read(self, address: U256):
        if address in self.data:
            return self.data[address]
        else:
            return 0

    def write(self, address: U256, value: U256):
        self.data[address] = value

    def op(self, address: U256, value: U256, is_write: bool):
        if is_write:
            # TODO: revert
            self.write(address, value)
        else:
            assert self.read(address) == value
