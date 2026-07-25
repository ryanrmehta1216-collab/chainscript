class ASTNode: pass

# --- Core Nodes ---
class AgentDefNode(ASTNode):
    def __init__(self, name, props): self.name, self.props = name, props
class SetNode(ASTNode):
    def __init__(self, var_name, expr): self.var_name, self.expr = var_name, expr
class InvokeNode(ASTNode):
    def __init__(self, agent_name, input_expr, memory_var, target_var):
        self.agent_name, self.input_expr, self.memory_var, self.target_var = agent_name, input_expr, memory_var, target_var
class JudgeNode(ASTNode):
    def __init__(self, input_expr, agent_name, target_var):
        self.input_expr, self.agent_name, self.target_var = input_expr, agent_name, target_var

# --- New: Functions & Control Flow ---
class FunctionDefNode(ASTNode):
    def __init__(self, name, params, body): self.name, self.params, self.body = name, params, body
class FunctionCallNode(ASTNode):
    def __init__(self, name, args): self.name, self.args = name, args
class ReturnNode(ASTNode):
    def __init__(self, expr): self.expr = expr
class WhileNode(ASTNode):
    def __init__(self, condition, body): self.condition, self.body = condition, body
class TryCatchNode(ASTNode):
    def __init__(self, try_body, error_var, catch_body):
        self.try_body, self.error_var, self.catch_body = try_body, error_var, catch_body

# --- IO & Built-ins ---
class WriteFileNode(ASTNode):
    def __init__(self, file_expr, data_expr): self.file_expr, self.data_expr = file_expr, data_expr
class ReadFileNode(ASTNode):
    def __init__(self, file_expr): self.file_expr = file_expr
class RunShellNode(ASTNode):
    def __init__(self, command_expr, target_var): self.command_expr, self.target_var = command_expr, target_var
class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch): self.condition, self.then_branch, self.else_branch = condition, then_branch, else_branch

# --- Data Types ---
class VarNode(ASTNode):
    def __init__(self, name): self.name = name
class LiteralNode(ASTNode):
    def __init__(self, value): self.value = value
class DictNode(ASTNode):
    def __init__(self, pairs): self.pairs = pairs
class ListNode(ASTNode):
    def __init__(self, elements): self.elements = elements

class Parser:
    def __init__(self, tokens):
        self.tokens, self.pos = tokens, 0

    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def consume(self, expected_type=None, expected_value=None):
        token = self.peek()
        if not token: raise SyntaxError("Unexpected end of input.")
        if expected_type and token.type != expected_type: raise SyntaxError(f"Line {token.line}: Expected {expected_type}, got '{token.value}'")
        if expected_value and token.value != expected_value: raise SyntaxError(f"Line {token.line}: Expected '{expected_value}', got '{token.value}'")
        self.pos += 1
        return token

    def parse(self):
        statements = []
        # We need to check if the token TYPE is RBRACE, not its value
        while self.peek() and self.peek().value not in ["ENDIF", "ELSE", "ENDWHILE"] and self.peek().type != "RBRACE":
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.peek()

        if token.value == "AGENT":
            self.consume("KEYWORD", "AGENT")
            name = self.consume("IDENTIFIER").value
            self.consume("LBRACE")
            props = {}
            while self.peek() and self.peek().type != "RBRACE":
                prop_key = self.consume("KEYWORD").value
                props[prop_key] = self.parse_expression()
            self.consume("RBRACE")
            return AgentDefNode(name, props)

        elif token.value == "FUNCTION":
            self.consume("KEYWORD", "FUNCTION")
            name = self.consume("IDENTIFIER").value
            self.consume("LPAREN")
            params = []
            if self.peek().type != "RPAREN":
                params.append(self.consume("IDENTIFIER").value)
                while self.peek().type == "COMMA":
                    self.consume("COMMA")
                    params.append(self.consume("IDENTIFIER").value)
            self.consume("RPAREN")
            self.consume("LBRACE")
            body = self.parse()
            self.consume("RBRACE")
            return FunctionDefNode(name, params, body)

        elif token.value == "RETURN":
            self.consume("KEYWORD", "RETURN")
            return ReturnNode(self.parse_expression())

        elif token.value == "TRY":
            self.consume("KEYWORD", "TRY")
            self.consume("LBRACE")
            try_body = self.parse()
            self.consume("RBRACE")
            self.consume("KEYWORD", "CATCH")
            err_var = self.consume("IDENTIFIER").value
            self.consume("LBRACE")
            catch_body = self.parse()
            self.consume("RBRACE")
            return TryCatchNode(try_body, err_var, catch_body)

        elif token.value == "WHILE":
            self.consume("KEYWORD", "WHILE")
            cond = self.parse_expression()
            self.consume("KEYWORD", "DO")
            body = self.parse()
            self.consume("KEYWORD", "ENDWHILE")
            return WhileNode(cond, body)

        elif token.value == "SET":
            self.consume("KEYWORD", "SET")
            var_name = self.consume("IDENTIFIER").value
            self.consume("EQUALS")
            return SetNode(var_name, self.parse_expression())

        elif token.value == "INVOKE":
            self.consume("KEYWORD", "INVOKE")
            agent_name = self.consume("IDENTIFIER").value
            self.consume("KEYWORD", "WITH")
            input_expr = self.parse_expression()
            mem, target = None, None
            if self.peek() and self.peek().value == "USING":
                self.consume("KEYWORD", "USING")
                self.consume("KEYWORD", "MEMORY")
                mem = self.consume("IDENTIFIER").value
            if self.peek() and self.peek().value == "AS":
                self.consume("KEYWORD", "AS")
                target = self.consume("IDENTIFIER").value
            return InvokeNode(agent_name, input_expr, mem, target)

        elif token.value == "JUDGE":
            self.consume("KEYWORD", "JUDGE")
            input_expr = self.parse_expression()
            self.consume("KEYWORD", "USING")
            agent_name = self.consume("IDENTIFIER").value
            self.consume("KEYWORD", "AS")
            target = self.consume("IDENTIFIER").value
            return JudgeNode(input_expr, agent_name, target)

        # Standard IF, WRITE, READ, RUN_SHELL logic remains identical
        elif token.value == "IF":
            self.consume("KEYWORD", "IF")
            cond = self.parse_expression()
            self.consume("KEYWORD", "THEN")
            then_b = self.parse()
            else_b = None
            if self.peek() and self.peek().value == "ELSE":
                self.consume("KEYWORD", "ELSE")
                else_b = self.parse()
            self.consume("KEYWORD", "ENDIF")
            return IfNode(cond, then_b, else_b)

        elif token.value == "WRITE":
            self.consume("KEYWORD", "WRITE")
            return WriteFileNode(self.parse_expression(), self.parse_expression())
        
        elif token.value == "RUN_SHELL":
            self.consume("KEYWORD", "RUN_SHELL")
            cmd = self.parse_expression()
            tgt = None
            if self.peek() and self.peek().value == "AS":
                self.consume("KEYWORD", "AS")
                tgt = self.consume("IDENTIFIER").value
            return RunShellNode(cmd, tgt)
            
        elif token.type == "IDENTIFIER":
            # Might be a function call acting as a statement
            ident = self.consume("IDENTIFIER").value
            if self.peek() and self.peek().type == "LPAREN":
                self.consume("LPAREN")
                args = []
                if self.peek().type != "RPAREN":
                    args.append(self.parse_expression())
                    while self.peek().type == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expression())
                self.consume("RPAREN")
                return FunctionCallNode(ident, args)
            else:
                raise SyntaxError(f"Line {token.line}: Unexpected standalone identifier '{ident}'")
        else:
            raise SyntaxError(f"Line {token.line}: Unknown command '{token.value}'")

    def parse_expression(self):
        left = self.parse_primary()
        while self.peek() and self.peek().value in ["+", "==", "!=", "CONTAINS"]:
            left = BinaryOpNode(left, self.consume().value, self.parse_primary())
        return left

    def parse_primary(self):
        token = self.peek()
        if token.value == "READ":
            self.consume("KEYWORD", "READ")
            return ReadFileNode(self.parse_primary())
        elif token.type in ["STRING", "NUMBER"]:
            return LiteralNode(self.consume().value)
        elif token.type == "IDENTIFIER":
            ident = self.consume("IDENTIFIER").value
            # Check if it's a function call inside an expression!
            if self.peek() and self.peek().type == "LPAREN":
                self.consume("LPAREN")
                args = []
                if self.peek().type != "RPAREN":
                    args.append(self.parse_expression())
                    while self.peek().type == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expression())
                self.consume("RPAREN")
                return FunctionCallNode(ident, args)
            return VarNode(ident)
        elif token.type == "LBRACE":
            self.consume("LBRACE")
            pairs = {}
            if self.peek() and self.peek().type != "RBRACE":
                key = self.consume("STRING").value
                self.consume("COLON")
                pairs[key] = self.parse_expression()
                while self.peek().type == "COMMA":
                    self.consume("COMMA")
                    key = self.consume("STRING").value
                    self.consume("COLON")
                    pairs[key] = self.parse_expression()
            self.consume("RBRACE")
            return DictNode(pairs)
        elif token.type == "LBRACKET":
            self.consume("LBRACKET")
            elements = []
            if self.peek() and self.peek().type != "RBRACKET":
                elements.append(self.parse_expression())
                while self.peek().type == "COMMA":
                    self.consume("COMMA")
                    elements.append(self.parse_expression())
            self.consume("RBRACKET")
            return ListNode(elements)
        else:
            raise SyntaxError(f"Line {token.line}: Unexpected token '{token.value}'")