import re
from .tokens import TokenType

class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.pos})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def next_token(self):
        while self.pos < self.length:
            c = self.text[self.pos]
            # Пропуск пробелов
            if c.isspace():
                self.pos += 1
                continue
            # Пропуск комментариев
            if c == '#':
                while self.pos < self.length and self.text[self.pos] != '\n':
                    self.pos += 1
                continue
            break
        if self.pos >= self.length:
            return Token(TokenType.EOF, '', self.pos)
        c = self.text[self.pos]
        # Идентификаторы и ключевые слова
        if c.isalpha() or c == '_':
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                self.pos += 1
            value = self.text[start:self.pos]
            if value == 'if':
                return Token(TokenType.IF, value, start)
            if value == 'while':
                return Token(TokenType.WHILE, value, start)
            return Token(TokenType.IDENT, value, start)
        # Числа
        if c.isdigit() or (c in '+-' and self.pos+1 < self.length and self.text[self.pos+1].isdigit()):
            start = self.pos
            if c in '+-':
                self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
            return Token(TokenType.NUMBER, self.text[start:self.pos], start)
        # Строки
        if c == "'":
            start = self.pos
            self.pos += 1
            s = ''
            while self.pos < self.length and self.text[self.pos] != "'":
                s += self.text[self.pos]
                self.pos += 1
            if self.pos < self.length and self.text[self.pos] == "'":
                self.pos += 1
                return Token(TokenType.STRING, s, start)
            else:
                return Token(TokenType.ERROR, 'unterminated string', start)
        # Операторы и спецсимволы
        if self.text.startswith('/out', self.pos):
            self.pos += 4
            return Token(TokenType.PRINT, '/out', self.pos-4)
        if self.text.startswith('/in', self.pos):
            self.pos += 3
            return Token(TokenType.INPUT, '/in', self.pos-3)
        if c == '>':
            self.pos += 1
            return Token(TokenType.PRINT, '>', self.pos-1)
        if c == '=':
            self.pos += 1
            return Token(TokenType.ASSIGN, '=', self.pos-1)
        if c == ':':
            self.pos += 1
            return Token(TokenType.COLON, ':', self.pos-1)
        if c == ';':
            self.pos += 1
            return Token(TokenType.SEMICOLON, ';', self.pos-1)
        if c == '(': 
            self.pos += 1
            return Token(TokenType.LPAREN, '(', self.pos-1)
        if c == ')':
            self.pos += 1
            return Token(TokenType.RPAREN, ')', self.pos-1)
        if c == '[':
            self.pos += 1
            return Token(TokenType.LBRACKET, '[', self.pos-1)
        if c == ']':
            self.pos += 1
            return Token(TokenType.RBRACKET, ']', self.pos-1)
        # Операторы (все двухсимвольные сначала)
        for op in ['&&', '||', '<=', '>=', '==', '!=']:
            if self.text.startswith(op, self.pos):
                self.pos += len(op)
                return Token(TokenType.OP, op, self.pos-len(op))
        if c in '+-*/%<>!':
            self.pos += 1
            return Token(TokenType.OP, c, self.pos-1)
        # Неизвестный символ
        self.pos += 1
        return Token(TokenType.ERROR, c, self.pos-1)

    def lex(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF or tok.type == TokenType.ERROR:
                break
        return tokens 