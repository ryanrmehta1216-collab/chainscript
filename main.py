import sys
from lexer import lex
from parser_ast import Parser
from analyzer import SemanticAnalyzer  # <-- Imports the analyzer
from interpreter import Interpreter

def execute_chainscript(source_file):
    print("==================================================")
    print("=== ChainScript Engine Pipeline                ===")
    print("==================================================\n")
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            code = f.read()

        # Step 1: Lexical Analysis
        tokens = lex(code)
        
        # Step 2: AST Parsing
        ast = Parser(tokens).parse()
        
        # Step 3: Run Static Analyzer (Pass 1)
        SemanticAnalyzer().analyze(ast)
        print("[Static Analysis] PASS: Scopes, agents, and variables validated successfully.\n")
        
        # Step 4: Run Interpreter (Pass 2)
        Interpreter().run(ast)
        
        print("\n==================================================")
        print("=== Execution Complete                         ===")
        print("==================================================")
    except Exception as e:
        print(f"\n[Fatal Error] {e}")

if __name__ == "__main__":
    file_to_run = sys.argv[1] if len(sys.argv) > 1 else "agent_pipeline.chain"
    execute_chainscript(file_to_run)