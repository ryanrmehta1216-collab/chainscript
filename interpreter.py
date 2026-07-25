import json, subprocess, ollama
from parser_ast import *

class ReturnException(Exception):
    def __init__(self, value): self.value = value

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'")

    def set(self, name, value):
        self.vars[name] = value

class Agent:
    def __init__(self, name, model="llama3", role="", temperature=0.7):
        self.name, self.model, self.role, self.temperature = name, model, role, float(temperature)

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.agents = {}
        self.functions = {}
        self.memories = {}

    def evaluate(self, node):
        if isinstance(node, LiteralNode): return node.value
        elif isinstance(node, VarNode): return self.current_env.get(node.name)
        elif isinstance(node, DictNode): return {k: self.evaluate(v) for k, v in node.pairs.items()}
        elif isinstance(node, ListNode): return [self.evaluate(e) for e in node.elements]
        
        elif isinstance(node, AgentDefNode):
            model = self.evaluate(node.props.get("MODEL", LiteralNode("llama3")))
            role = self.evaluate(node.props.get("ROLE", LiteralNode("Assistant")))
            temp = self.evaluate(node.props.get("TEMPERATURE", LiteralNode(0.7)))
            self.agents[node.name] = Agent(node.name, model, role, temp)
            print(f"[Engine] Registered Agent '{node.name}'")

        elif isinstance(node, FunctionDefNode):
            self.functions[node.name] = node
            print(f"[Engine] Registered Function '{node.name}'")

        elif isinstance(node, FunctionCallNode):
            if node.name not in self.functions: raise RuntimeError(f"Unknown function '{node.name}'")
            func = self.functions[node.name]
            if len(node.args) != len(func.params): raise RuntimeError(f"Function {node.name} expects {len(func.params)} args, got {len(node.args)}")
            
            # Lexical Scoping: Create new isolated environment
            call_env = Environment(parent=self.global_env)
            for param, arg_expr in zip(func.params, node.args):
                call_env.set(param, self.evaluate(arg_expr))
            
            prev_env = self.current_env
            self.current_env = call_env
            try:
                for stmt in func.body: self.evaluate(stmt)
            except ReturnException as ret:
                self.current_env = prev_env
                return ret.value
            self.current_env = prev_env
            return None

        elif isinstance(node, ReturnNode):
            raise ReturnException(self.evaluate(node.expr))

        elif isinstance(node, TryCatchNode):
            try:
                for stmt in node.try_body: self.evaluate(stmt)
            except ReturnException as r:
                # CRITICAL FIX: Let return statements pass through the try/catch!
                raise r
            except Exception as e:
                print(f"[Engine] Caught Exception: {str(e)}")
                self.current_env.set(node.error_var, str(e))
                for stmt in node.catch_body: self.evaluate(stmt)

        elif isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                for stmt in node.body: self.evaluate(stmt)

        elif isinstance(node, BinaryOpNode):
            l, r = self.evaluate(node.left), self.evaluate(node.right)
            if node.op == "+": return str(l) + str(r)
            elif node.op == "==": return str(l).upper().strip() == str(r).upper().strip()
            elif node.op == "!=": return str(l).upper().strip() != str(r).upper().strip()
            elif node.op == "CONTAINS": return str(r).lower() in str(l).lower()

        elif isinstance(node, SetNode):
            val = self.evaluate(node.expr)
            self.current_env.set(node.var_name, val)
            return val

        elif isinstance(node, ReadFileNode):
            with open(self.evaluate(node.file_expr), 'r', encoding='utf-8') as f: return f.read()

        elif isinstance(node, WriteFileNode):
            path, data = self.evaluate(node.file_expr), self.evaluate(node.data_expr)
            out = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            with open(path, 'w', encoding='utf-8') as f: f.write(out)

        elif isinstance(node, RunShellNode):
            res = subprocess.run(self.evaluate(node.command_expr), shell=True, capture_output=True, text=True)
            out = res.stdout.strip() if res.returncode == 0 else res.stderr.strip()
            if node.target_var: self.current_env.set(node.target_var, out)
            return out

        elif isinstance(node, InvokeNode):
            agent = self.agents.get(node.agent_name)
            prompt = self.evaluate(node.input_expr)
            print(f"[AI] Invoking '{agent.name}'...")
            msgs = [{'role': 'system', 'content': agent.role}, {'role': 'user', 'content': str(prompt)}]
            out = ollama.chat(model=agent.model, messages=msgs, options={'temperature': agent.temperature})['message']['content']
            if node.target_var: self.current_env.set(node.target_var, out)
            return out

        elif isinstance(node, JudgeNode):
            agent = self.agents.get(node.agent_name)
            data = self.evaluate(node.input_expr)
            print(f"[Logic Gate] '{agent.name}' is judging...")
            msgs = [{'role': 'system', 'content': agent.role + " Reply ONLY 'PASS' or 'FAIL'."}, {'role': 'user', 'content': str(data)}]
            res = ollama.chat(model=agent.model, messages=msgs, options={'temperature': 0.0})['message']['content'].upper()
            verdict = "PASS" if "PASS" in res else "FAIL"
            self.current_env.set(node.target_var, verdict)
            return verdict

        elif isinstance(node, IfNode):
            if self.evaluate(node.condition):
                for stmt in node.then_branch: self.evaluate(stmt)
            elif node.else_branch:
                for stmt in node.else_branch: self.evaluate(stmt)

    def run(self, ast_nodes):
        for node in ast_nodes: self.evaluate(node)