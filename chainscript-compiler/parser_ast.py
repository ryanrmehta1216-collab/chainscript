# --- AST NODES ---
class ProgramNode:
    def __init__(self, statements): self.statements = statements
class AgentNode:
    def __init__(self, name, params, body): self.name = name; self.params = params; self.body = body
class VarDeclNode:
    def __init__(self, name, expr): self.name = name; self.expr = expr
class AssignNode:
    def __init__(self, name, expr): self.name = name; self.expr = expr
class OutputNode:
    def __init__(self, value): self.value = value
class IfNode:
    def __init__(self, condition, true_body, false_body): self.condition = condition; self.true_body = true_body; self.false_body = false_body
class WhileNode:
    def __init__(self, condition, body): self.condition = condition; self.body = body
class ReturnNode:
    def __init__(self, expr): self.expr = expr
class RunNode:
    def __init__(self, name, args): self.name = name; self.args = args
class BinOpNode:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
class NumberNode:
    def __init__(self, value): self.value = value
class StringNode:
    def __init__(self, value): self.value = value
class VarAccessNode:
    def __init__(self, name): self.name = name

# --- PARSER ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        tok = self.current()
        if tok and tok.type == token_type:
            self.pos += 1
            return tok
        raise SyntaxError(f"Expected token {token_type}, got {tok}")

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            if self.current().type == 'KEYWORD' and self.current().value == 'AGENT':
                statements.append(self.parse_agent())
            else: self.pos += 1
        return ProgramNode(statements)

    def parse_agent(self):
        self.eat('KEYWORD') # AGENT
        name = self.eat('IDENT').value
        params = []
        if self.current() and self.current().type == 'LPAREN':
            self.eat('LPAREN')
            if self.current() and self.current().type == 'IDENT':
                params.append(self.eat('IDENT').value)
                while self.current() and self.current().type == 'COMMA':
                    self.eat('COMMA')
                    params.append(self.eat('IDENT').value)
            self.eat('RPAREN')
        body = self.parse_block()
        return AgentNode(name, params, body)

    def parse_block(self):
        self.eat('LBRACE')
        body = []
        while self.current() and self.current().type != 'RBRACE':
            body.append(self.parse_statement())
        self.eat('RBRACE')
        return body

    def parse_statement(self):
        tok = self.current()
        if tok.type == 'KEYWORD':
            if tok.value == 'INT': return self.parse_var_decl()
            if tok.value == 'OUTPUT': return self.parse_output()
            if tok.value == 'IF': return self.parse_if()
            if tok.value == 'WHILE': return self.parse_while()
            if tok.value == 'RETURN':
                self.eat('KEYWORD')
                return ReturnNode(self.parse_expression())
        elif tok.type == 'IDENT':
            return self.parse_assign()
        raise SyntaxError(f"Unexpected statement token: {tok}")

    def parse_var_decl(self):
        self.eat('KEYWORD')
        name = self.eat('IDENT').value
        self.eat('ASSIGN')
        return VarDeclNode(name, self.parse_expression())

    def parse_assign(self):
        name = self.eat('IDENT').value
        self.eat('ASSIGN')
        return AssignNode(name, self.parse_expression())

    def parse_output(self):
        self.eat('KEYWORD')
        self.eat('LPAREN')
        expr = self.parse_expression()
        self.eat('RPAREN')
        return OutputNode(expr)

    def parse_if(self):
        self.eat('KEYWORD')
        self.eat('LPAREN')
        cond = self.parse_expression()
        self.eat('RPAREN')
        true_body = self.parse_block()
        false_body = []
        if self.current() and self.current().type == 'KEYWORD' and self.current().value == 'ELSE':
            self.eat('KEYWORD')
            false_body = self.parse_block()
        return IfNode(cond, true_body, false_body)
    
    def parse_while(self):
        self.eat('KEYWORD')
        self.eat('LPAREN')
        cond = self.parse_expression()
        self.eat('RPAREN')
        return WhileNode(cond, self.parse_block())

    def parse_expression(self):
        left = self.parse_math()
        if self.current() and self.current().type == 'COMP':
            return BinOpNode(left, self.eat('COMP').value, self.parse_math())
        return left

    def parse_math(self):
        left = self.parse_term()
        while self.current() and self.current().type == 'OP':
            left = BinOpNode(left, self.eat('OP').value, self.parse_term())
        return left

    def parse_term(self):
        tok = self.current()
        if tok.type == 'KEYWORD' and tok.value == 'RUN':
            self.eat('KEYWORD')
            name = self.eat('IDENT').value
            self.eat('LPAREN')
            args = []
            if self.current() and self.current().type != 'RPAREN':
                args.append(self.parse_expression())
                while self.current() and self.current().type == 'COMMA':
                    self.eat('COMMA')
                    args.append(self.parse_expression())
            self.eat('RPAREN')
            return RunNode(name, args)
        elif tok.type == 'NUMBER': return NumberNode(self.eat('NUMBER').value)
        elif tok.type == 'STRING': return StringNode(self.eat('STRING').value)
        elif tok.type == 'IDENT': return VarAccessNode(self.eat('IDENT').value)
        raise SyntaxError(f"Unexpected token in expression: {tok}")