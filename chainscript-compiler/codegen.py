from parser_ast import StringNode, AgentNode

class CCodeGenerator:
    def __init__(self):
        self.headers = {"#include <stdio.h>", "#include <stdlib.h>"}
        self.indent_level = 0

    def indent(self): return "    " * self.indent_level

    def generate(self, ast):
        c_body = self.visit(ast)
        return "\n".join(sorted(self.headers)) + "\n\n" + c_body

    def visit(self, node):
        return getattr(self, f"visit_{type(node).__name__}", self.generic_visit)(node)

    def generic_visit(self, node): raise NotImplementedError(f"No visit method for {type(node).__name__}")

    def visit_ProgramNode(self, node):
        declarations = []
        implementations = []
        for stmt in node.statements:
            if isinstance(stmt, AgentNode):
                if stmt.name != "main":
                    params_c = ", ".join([f"int {p}" for p in stmt.params])
                    declarations.append(f"int agent_{stmt.name}({params_c});")
                implementations.append(self.visit(stmt))
        return "\n".join(declarations) + "\n\n" + "\n\n".join(implementations)

    def visit_AgentNode(self, node):
        if node.name == "main": header = "int main() {\n"
        else:
            params_c = ", ".join([f"int {p}" for p in node.params])
            header = f"int agent_{node.name}({params_c}) {{\n"
            
        self.indent_level += 1
        body_lines = [f"{self.indent()}{self.visit(stmt)}" for stmt in node.body]
        if node.name == "main": body_lines.append(f"{self.indent()}return 0;")
        self.indent_level -= 1
        return header + "\n".join(body_lines) + "\n}"

    def visit_VarDeclNode(self, node): return f"int {node.name} = {self.visit(node.expr)};"
    def visit_AssignNode(self, node): return f"{node.name} = {self.visit(node.expr)};"
    def visit_ReturnNode(self, node): return f"return {self.visit(node.expr)};"
    def visit_RunNode(self, node): return f"agent_{node.name}({', '.join([self.visit(a) for a in node.args])})"
    
    def visit_OutputNode(self, node):
        if isinstance(node.value, StringNode): return f'printf("%s\\n", "{node.value.value}");'
        return f'printf("%d\\n", {self.visit(node.value)});'

    def visit_IfNode(self, node):
        code = f"if ({self.visit(node.condition)}) {{\n"
        self.indent_level += 1
        code += "".join([f"{self.indent()}{self.visit(s)}\n" for s in node.true_body])
        self.indent_level -= 1
        code += f"{self.indent()}}}"
        if node.false_body:
            code += " else {\n"
            self.indent_level += 1
            code += "".join([f"{self.indent()}{self.visit(s)}\n" for s in node.false_body])
            self.indent_level -= 1
            code += f"{self.indent()}}}"
        return code

    def visit_WhileNode(self, node):
        code = f"while ({self.visit(node.condition)}) {{\n"
        self.indent_level += 1
        code += "".join([f"{self.indent()}{self.visit(s)}\n" for s in node.body])
        self.indent_level -= 1
        code += f"{self.indent()}}}"
        return code

    def visit_BinOpNode(self, node): return f"({self.visit(node.left)} {node.op} {self.visit(node.right)})"
    def visit_NumberNode(self, node): return str(node.value)
    def visit_StringNode(self, node): return f'"{node.value}"'
    def visit_VarAccessNode(self, node): return node.name