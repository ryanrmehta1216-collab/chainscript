import re

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line:{self.line})"

TOKEN_SPECIFICATION = [
    ('COMMENT',       r'//.*'),
    ('NUMBER',        r'\b\d+(\.\d+)?\b'),
    ('STRING',        r'"[^"\\]*(?:\\.[^"\\]*)*"'),
    ('EQUALS_EQ',     r'=='),
    ('NOT_EQ',        r'!='),
    ('EQUALS',        r'='),
    ('PLUS',          r'\+'),
    ('LBRACE',        r'\{'),
    ('RBRACE',        r'\}'),
    ('LPAREN',        r'\('),
    ('RPAREN',        r'\)'),
    ('LBRACKET',      r'\['),
    ('RBRACKET',      r'\]'),
    ('COLON',         r':'),
    ('COMMA',         r','),
    ('KEYWORD',       r'\b(AGENT|MODEL|ROLE|TEMPERATURE|SET|INVOKE|WITH|USING|MEMORY|AS|JUDGE|IF|THEN|ELSE|ENDIF|WHILE|DO|ENDWHILE|FUNCTION|RETURN|TRY|CATCH|WRITE|READ|RUN_SHELL|CONTAINS)\b'),
    ('IDENTIFIER',    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('NEWLINE',       r'\n'),
    ('SKIP',          r'[ \t]+'),
    ('MISMATCH',      r'.'),
]

def lex(code):
    tokens = []
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)
    
    for line_num, line in enumerate(code.split('\n'), 1):
        for mo in re.finditer(tok_regex, line):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind in ['SKIP', 'COMMENT']: continue
            elif kind == 'STRING': tokens.append(Token('STRING', value[1:-1], line_num))
            elif kind == 'NUMBER': tokens.append(Token('NUMBER', float(value) if '.' in value else int(value), line_num))
            elif kind == 'MISMATCH': raise SyntaxError(f"Lexical Error: Unexpected '{value}' on line {line_num}")
            elif kind != 'NEWLINE': tokens.append(Token(kind, value, line_num))
                
    return tokens