import re

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class Lexer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        token_specification = [
            ('KEYWORD',  r'\b(AGENT|OUTPUT|INT|IF|ELSE|WHILE|RUN|RETURN)\b'),
            ('STRING',   r'"[^"]*"'),
            ('NUMBER',   r'\b\d+\b'),
            ('IDENT',    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('COMP',     r'==|!=|<=|>=|<|>'),
            ('ASSIGN',   r'='),
            ('OP',       r'[+\-*/]'),
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('COMMA',    r','),
            ('SKIP',     r'[ \t\n\r]+'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        tokens = []

        for mo in re.finditer(tok_regex, self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP': continue
            elif kind == 'STRING': tokens.append(Token(kind, value[1:-1]))
            elif kind == 'MISMATCH': raise RuntimeError(f'Unexpected character {value!r}')
            else: tokens.append(Token(kind, value))

        return tokens