from src.isa import Command, Opcode
from .tokens import TokenType

class TranslationResult:
    def __init__(self, exe, instruction_count):
        self.exe = exe  # bytes или list[int]
        self.instruction_count = instruction_count

class Translator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.data_ptr = 0x8000
        self.instructions = []
        self.var_table = {}  # имя переменной -> адрес
        self.var_addr = 0x9000

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def expect(self, type_):
        tok = self.current()
        if not tok or tok.type != type_:
            return None
        self.advance()
        return tok

    def get_var_addr(self, name):
        if name not in self.var_table:
            self.var_table[name] = self.var_addr
            self.var_addr += 4
        return self.var_table[name]

    def add_cstr(self, s: str) -> int:
        addr = self.data_ptr
        for c in s:
            self.instructions.append(Command(Opcode.PUSH, ord(c)))
            self.instructions.append(Command(Opcode.PUSH, addr))
            self.instructions.append(Command(Opcode.STORE))
            addr += 4
        # null-terminator
        self.instructions.append(Command(Opcode.PUSH, 0))
        self.instructions.append(Command(Opcode.PUSH, addr))
        self.instructions.append(Command(Opcode.STORE))
        self.data_ptr = addr + 4
        return self.data_ptr - (len(s) + 1) * 4

    def translate(self):
        while self.current() and self.current().type is not None:
            tok = self.current()
            if tok.type is None or tok.type.name == 'EOF':
                break
            if tok.type.name == 'PRINT':
                self.advance()
                # > x; или /out 'строка';
                if self.current() and self.current().type == TokenType.STRING:
                    str_tok = self.expect(TokenType.STRING)
                    addr = self.add_cstr(str_tok.value)
                    for i in range(len(str_tok.value)):
                        self.instructions.append(Command(Opcode.PUSH, addr + i * 4))
                        self.instructions.append(Command(Opcode.LOAD))
                        self.instructions.append(Command(Opcode.PUSH, 0xFF01))
                        self.instructions.append(Command(Opcode.STORE))
                elif self.current() and self.current().type == TokenType.IDENT:
                    var_tok = self.expect(TokenType.IDENT)
                    addr = self.get_var_addr(var_tok.value)
                    self.instructions.append(Command(Opcode.PUSH, addr))
                    self.instructions.append(Command(Opcode.LOAD))
                    self.instructions.append(Command(Opcode.PUSH, 0xFF01))
                    self.instructions.append(Command(Opcode.STORE))
                else:
                    return None, 'expected string or variable after /out/>'
                # Ожидаем ;
                if self.current() and self.current().type == TokenType.SEMICOLON:
                    self.advance()
                self.instructions.append(Command(Opcode.HALT))
                break
            elif tok.type.name == 'INPUT':
                self.advance()
                var_tok = self.expect(TokenType.IDENT)
                if not var_tok:
                    return None, 'expected variable after /in'
                addr = self.get_var_addr(var_tok.value)
                self.instructions.append(Command(Opcode.PUSH, 0xFF00))
                self.instructions.append(Command(Opcode.LOAD))
                self.instructions.append(Command(Opcode.PUSH, addr))
                self.instructions.append(Command(Opcode.STORE))
                # Ожидаем ;
                if self.current() and self.current().type == TokenType.SEMICOLON:
                    self.advance()
            else:
                self.advance()
        from src.isa import encode_command
        exe = b''.join(encode_command(cmd) for cmd in self.instructions)
        return TranslationResult(exe, len(self.instructions)), None 