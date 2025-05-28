from enum import Enum, auto

class TokenType(Enum):
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    ASSIGN = auto()      # =
    PRINT = auto()       # /out или >
    INPUT = auto()       # /in
    IF = auto()
    WHILE = auto()
    COLON = auto()       # :
    SEMICOLON = auto()   # ;
    OP = auto()          # + - * / % && || < > <= >= == != !
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    EOF = auto()
    ERROR = auto() 