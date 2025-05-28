from enum import Enum
from dataclasses import dataclass
from typing import Optional

MEMORY_SIZE = 65536
STACK_SIZE = 1024
INPUT_PORT = 0xFF00
OUTPUT_PORT = 0xFF01
INTERRUPT_TABLE = {'input': 0x1000}

class Opcode(Enum):
    PUSH = 0x01
    POP = 0x02
    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13
    JMP = 0x20
    JZ = 0x21
    HALT = 0xFF
    LOAD = 0x50
    STORE = 0x51
    IRET = 0x31
    EI = 0x32
    DI = 0x33

@dataclass
class Command:
    opcode: Opcode
    operand: Optional[int] = 0

class Memory:
    def __init__(self):
        self.mem = bytearray(MEMORY_SIZE)
        self.output = []
        self.code_size = 0
        self.data_ptr = 0x8000

    def initialize(self, code: bytes):
        self.code_size = len(code)
        self.mem[:self.code_size] = code

    def read_word(self, addr: int) -> int:
        return int.from_bytes(self.mem[addr:addr+4], 'little')

    def write_word(self, addr: int, value: int):
        self.mem[addr:addr+4] = value.to_bytes(4, 'little')
        if addr == OUTPUT_PORT:
            self.output.append(chr(value))

    def add_string(self, s: str) -> int:
        addr = self.data_ptr
        for c in s:
            self.write_word(addr, ord(c))
            addr += 4
        self.write_word(addr, 0)
        self.data_ptr = addr + 4
        return addr - len(s) * 4

def encode_command(cmd: Command) -> bytes:
    operand = cmd.operand if cmd.operand else 0
    return (cmd.opcode.value << 24 | operand).to_bytes(4, 'big')

def decode_command(data: bytes) -> Command:
    value = int.from_bytes(data, 'big')
    opcode = Opcode((value >> 24) & 0xFF)
    operand = value & 0xFFFFFF
    return Command(opcode, operand)

class StackOverflowError(Exception): pass
class StackUnderflowError(Exception): pass