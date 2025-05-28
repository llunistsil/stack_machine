import logging
from typing import List, Tuple
from src.isa import *

class DataPath:
    def __init__(self, code: bytes, input_tokens: List[Tuple[int, str]]):
        self.memory = Memory()
        self.memory.initialize(code)
        self.stack = []
        self.pc = 0
        self.input_events = sorted(input_tokens, key=lambda x: x[0])
        self.int_enabled = True
        self.int_stack = []
        self.handling_int = False

    def push(self, value: int):
        if len(self.stack) >= STACK_SIZE:
            raise StackOverflowError()
        self.stack.append(value & 0xFFFFFFFF)

    def pop(self) -> int:
        if not self.stack:
            raise StackUnderflowError()
        return self.stack.pop()

    def check_interrupt(self, tick: int):
        while self.input_events and tick >= self.input_events[0][0]:
            if self.int_enabled and not self.handling_int:
                self.trigger_interrupt()
            else:
                self.input_events[0] = (tick + 1, self.input_events[0][1])
            break

    def trigger_interrupt(self):
        self.handling_int = True
        self.int_stack.append((self.pc, self.stack.copy(), self.int_enabled))
        self.pc = INTERRUPT_TABLE['input']
        tick, char = self.input_events.pop(0)
        self.memory.write_word(INPUT_PORT, ord(char))

class ControlUnit:
    def __init__(self, data_path: DataPath):
        self.data_path = data_path
        self.ticks = 0
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger("cpu_trace")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("simulation.log", mode="w")
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def log_instruction(self, cmd: Command, pc: int):
        prefix = "[INT] " if self.data_path.handling_int else ""
        hex_code = self.data_path.memory.mem[pc:pc + 4].hex().upper()
        mnemonic = f"{cmd.opcode.name.lower()} #{cmd.operand}" if cmd.operand else cmd.opcode.name.lower()
        self.logger.debug(f"{prefix}{pc:04X} - {hex_code} - {mnemonic}")

    def tick(self):
        self.ticks += 1

    def fetch_execute(self):
        while self.pc_in_bounds():
            try:
                self.data_path.check_interrupt(self.ticks)

                cmd_bytes = self.data_path.memory.mem[self.data_path.pc:self.data_path.pc + 4]
                cmd = decode_command(cmd_bytes)
                self.log_instruction(cmd, self.data_path.pc)

                self.data_path.pc += 4

                self.tick()
                self.execute(cmd)
                if cmd.opcode == Opcode.HALT:
                    break
            except Exception as e:
                logging.error("Error at 0x%04X: %s", self.data_path.pc, e)
                break

    def pc_in_bounds(self) -> bool:
        return 0 <= self.data_path.pc < self.data_path.memory.code_size

    def execute(self, cmd: Command):
        op = cmd.opcode
        arg = cmd.operand or 0

        if op == Opcode.PUSH:
            self.data_path.push(arg)
        elif op == Opcode.POP:
            self.data_path.pop()
        elif op == Opcode.ADD:
            b = self.data_path.pop()
            a = self.data_path.pop()
            self.data_path.push(a + b)
        elif op == Opcode.SUB:
            b = self.data_path.pop()
            a = self.data_path.pop()
            self.data_path.push(a - b)
        elif op == Opcode.MUL:
            b = self.data_path.pop()
            a = self.data_path.pop()
            self.data_path.push(a * b)
        elif op == Opcode.DIV:
            b = self.data_path.pop()
            a = self.data_path.pop()
            self.data_path.push(a // b if b != 0 else 0)
        elif op == Opcode.LOAD:
            addr = self.data_path.pop()
            self.data_path.push(self.data_path.memory.read_word(addr))
        elif op == Opcode.STORE:
            addr = self.data_path.pop()
            val = self.data_path.pop()
            self.data_path.memory.write_word(addr, val)
        elif op == Opcode.JMP:
            self.data_path.pc = arg
        elif op == Opcode.JZ:
            val = self.data_path.pop()
            if val == 0:
                self.data_path.pc = arg
        elif op == Opcode.EI:
            self.data_path.int_enabled = True
        elif op == Opcode.DI:
            self.data_path.int_enabled = False
        elif op == Opcode.IRET:
            pc, stack, int_enabled = self.data_path.int_stack.pop()
            self.data_path.pc = pc
            self.data_path.stack = stack
            self.data_path.int_enabled = int_enabled
            self.data_path.handling_int = False

def simulate(code: bytes, input_schedule):
    dp = DataPath(code, input_schedule)
    cu = ControlUnit(dp)
    cu.fetch_execute()
    print(f"[DEBUG] Output buffer: {''.join(dp.memory.output)}")
    print(f"[DEBUG] PC: {dp.pc:04X}")
    print(f"[DEBUG] Stack: {dp.stack}")
    return ''.join(dp.memory.output), cu.ticks