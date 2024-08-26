# MCOPY opcode

## Procedure

The `MCOPY` opcode pops `dest_offset`, `offset` and `size` from the stack.
It then copies `size` bytes in the current environment from memory at an `offset` to the memory at a `dest_offset`. For out-of-bounds scenarios - the memory is extended with respective gas cost applied.

The gas cost of `MCOPY` opcode consists of two parts:

1. A constant gas cost: `3 gas`
2. A dynamic gas cost: cost of memory expansion and copying (variable depending on the `size` copied to memory)

## Constraints

1. OpcodeId check

- opId == OpcodeId(0x5E)

2. State Transition

- rw_counter += 3 stack_reads
- stack_pointer += 3
- pc += 1
- gas += 3 + dynamic_gas_cost
- reversible_write_counter += 1
- memory_size
  - `prev_memory_size` if `size = 0`
  - `max(prev_memory_size, (offset + size + 31) / 32)` if `size > 0`

3. Lookups: 4

   1. `dest_offset` is at the 1st position of the stack
   2. `offset` is at the 2nd position of the stack
   3. `size` is at the 3rd position of the stack
   4. CopyTable lookup

## Exceptions

1. stack underflow: `1022 <= stack_pointer <= 1024`
2. out of gas: remaining gas is not enough
