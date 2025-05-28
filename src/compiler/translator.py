from src.compiler.tokens import TokenType
from src.isa import Command, Opcode, encode_command


class TranslationResult:
    def __init__(self, exe, instruction_count):
        self.exe = exe
        self.instruction_count = instruction_count


class Translator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.data_ptr = 0x8000
        self.instructions = []
        self.var_table = {}
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
        self.instructions.append(Command(Opcode.PUSH, 0))
        self.instructions.append(Command(Opcode.PUSH, addr))
        self.instructions.append(Command(Opcode.STORE))
        self.data_ptr = addr + 4
        return self.data_ptr - (len(s) + 1) * 4

    def translate(self):
        # Обработчик прерываний ввода
        handler_code = [
            Command(Opcode.PUSH, 0xFF00),
            Command(Opcode.LOAD),
            Command(Opcode.PUSH, 0x9000),
            Command(Opcode.STORE),
            Command(Opcode.IRET),
        ]

        # Основной код
        self.instructions = []

        while self.current() and self.current().type is not None:
            tok = self.current()
            if tok.type.name == 'PRINT':
                self.advance()
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
                if self.current() and self.current().type == TokenType.SEMICOLON:
                    self.advance()
            elif tok.type.name == 'INPUT':
                self.advance()
                var_tok = self.expect(TokenType.IDENT)
                if not var_tok:
                    return None, 'expected variable after /in'
                addr = self.get_var_addr(var_tok.value)
                self.instructions.append(Command(Opcode.EI))
                self.instructions.append(Command(Opcode.HALT))
                if self.current() and self.current().type == TokenType.SEMICOLON:
                    self.advance()
            else:
                self.advance()

        # Генерируем бинарник
        main_bin = b''.join(encode_command(c) for c in self.instructions)

        # Заполняем память до 0x1000
        pad_len = 0x1000 - len(main_bin)
        if pad_len < 0:
            pad_len = 0
        padding = b'\x00' * pad_len

        # Обработчик прерываний по адресу 0x1000
        handler_bin = b''.join(encode_command(c) for c in handler_code)

        # Формируем бинарник: [main_code][padding][handler]
        exe = main_bin + padding + handler_bin

        return TranslationResult(exe, len(self.instructions) + len(handler_code)), None
