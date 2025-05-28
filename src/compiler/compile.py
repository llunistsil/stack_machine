from .lexer import Lexer
from .tokens import TokenType
from .translator import Translator

def run(src_file: str, output_file: str):
    with open(src_file, 'r', encoding='utf-8') as f:
        text = f.read()

    lexer = Lexer(text)
    tokens = lexer.lex()

    for token in tokens:
        if token.type == TokenType.ERROR:
            return f'lexer error: {token.value}'

    translator = Translator(tokens)
    translation_result, error = translator.translate()

    if error is not None:
        return f'translator error: {error}'

    with open(output_file, 'wb') as f:
        f.write(translation_result.exe)

    print(f'instructions: {translation_result.instruction_count}')
    return None 