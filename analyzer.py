from parser_ast import *

class SemanticError(Exception):
    """Custom exception raised when static analysis detects a semantic error."""
    pass

class SemanticAnalyzer:
    """Pass 1 Analyzer: Scans the AST before execution to validate:
    - Invocation of undeclared agents
    - Calls to undefined functions or incorrect argument counts
    - References to uninitialized variables
    - Scope integrity across functions, conditions, and error handlers
    """
    def __init__(self):
        self.declared_agents = set()
        self.functions = {}  # Maps function_name -> param_count
        # Stack of variable scopes for lexical scope verification
        self.scopes = [set()]

    def current_scope(self):
        return self.scopes[-1]

    def is_var_declared(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def declare_var(self, name):
        if name:
            self.current_scope().add(name)

    def analyze(self, ast_nodes):
        # Pass 1a: Pre-scan AST to hoist and register all Agent and Function declarations
        self._register_declarations(ast_nodes)

        # Pass 1b: Recursively check AST for semantic errors
        for node in ast_nodes:
            self.visit(node)

    def _register_declarations(self, nodes):
        """Recursively registers top-level and block-nested agents and functions."""
        if not nodes:
            return
        for node in nodes:
            if isinstance(node, AgentDefNode):
                self.declared_agents.add(node.name)
            elif isinstance(node, FunctionDefNode):
                self.functions[node.name] = len(node.params)
                self._register_declarations(node.body)
            elif isinstance(node, IfNode):
                self._register_declarations(node.then_branch)
                if node.else_branch:
                    self._register_declarations(node.else_branch)
            elif isinstance(node, WhileNode):
                self._register_declarations(node.body)
            elif isinstance(node, TryCatchNode):
                self._register_declarations(node.try_body)
                self._register_declarations(node.catch_body)

    def visit(self, node):
        if node is None:
            return

        if isinstance(node, AgentDefNode):
            for expr in node.props.values():
                self.visit(expr)

        elif isinstance(node, SetNode):
            self.visit(node.expr)
            self.declare_var(node.var_name)

        elif isinstance(node, VarNode):
            if not self.is_var_declared(node.name):
                raise SemanticError(f"Semantic Error: Variable '{node.name}' referenced before assignment.")

        elif isinstance(node, InvokeNode):
            if node.agent_name not in self.declared_agents:
                raise SemanticError(f"Semantic Error: Invoking undeclared agent '{node.agent_name}'.")
            self.visit(node.input_expr)
            if node.memory_var and not self.is_var_declared(node.memory_var):
                raise SemanticError(f"Semantic Error: Memory variable '{node.memory_var}' referenced before assignment.")
            if node.target_var:
                self.declare_var(node.target_var)

        elif isinstance(node, JudgeNode):
            if node.agent_name not in self.declared_agents:
                raise SemanticError(f"Semantic Error: Judge gate using undeclared agent '{node.agent_name}'.")
            self.visit(node.input_expr)
            if node.target_var:
                self.declare_var(node.target_var)

        elif isinstance(node, FunctionDefNode):
            # Create isolated lexical scope for function parameters and body
            func_scope = set(node.params)
            self.scopes.append(func_scope)
            for stmt in node.body:
                self.visit(stmt)
            self.scopes.pop()

        elif isinstance(node, FunctionCallNode):
            if node.name not in self.functions:
                raise SemanticError(f"Semantic Error: Call to undefined function '{node.name}'.")
            expected_args = self.functions[node.name]
            if len(node.args) != expected_args:
                raise SemanticError(f"Semantic Error: Function '{node.name}' expects {expected_args} argument(s), got {len(node.args)}.")
            for arg in node.args:
                self.visit(arg)

        elif isinstance(node, ReturnNode):
            if node.expr:
                self.visit(node.expr)

        elif isinstance(node, IfNode):
            self.visit(node.condition)
            for stmt in node.then_branch:
                self.visit(stmt)
            if node.else_branch:
                for stmt in node.else_branch:
                    self.visit(stmt)

        elif isinstance(node, WhileNode):
            self.visit(node.condition)
            for stmt in node.body:
                self.visit(stmt)

        elif isinstance(node, TryCatchNode):
            for stmt in node.try_body:
                self.visit(stmt)
            # Create isolated scope for CATCH block containing the error variable
            catch_scope = {node.error_var} if node.error_var else set()
            self.scopes.append(catch_scope)
            for stmt in node.catch_body:
                self.visit(stmt)
            self.scopes.pop()

        elif isinstance(node, RunShellNode):
            self.visit(node.command_expr)
            if node.target_var:
                self.declare_var(node.target_var)

        elif isinstance(node, WriteFileNode):
            self.visit(node.file_expr)
            self.visit(node.data_expr)

        elif isinstance(node, ReadFileNode):
            self.visit(node.file_expr)

        elif isinstance(node, BinaryOpNode):
            self.visit(node.left)
            self.visit(node.right)

        elif isinstance(node, DictNode):
            for val in node.pairs.values():
                self.visit(val)

        elif isinstance(node, ListNode):
            for elem in node.elements:
                self.visit(elem)

        elif isinstance(node, LiteralNode):
            pass