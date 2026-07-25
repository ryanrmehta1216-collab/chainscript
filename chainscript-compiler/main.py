# main.py
import subprocess
import os

# Import your modules
from lexer import Lexer
from parser_ast import Parser
from codegen import CCodeGenerator

def build_chainscript(source_path, output_exe="program.exe"):
    if not os.path.exists(source_path):
        print(f"[ERROR] Source file '{source_path}' not found!")
        return

    # 1. Read source code
    with open(source_path, "r") as f:
        code = f.read()

    print("[1/4] Lexing tokens...")
    tokens = Lexer(code).tokenize()

    print("[2/4] Parsing AST...")
    ast = Parser(tokens).parse()

    print("[3/4] Generating C code...")
    c_code = CCodeGenerator().generate(ast)

    # Write temporary C file
    temp_c = "temp_build.c"
    with open(temp_c, "w") as f:
        f.write(c_code)

    print(f"[4/4] Compiling with GCC -> {output_exe}...")
    try:
        # Call GCC directly via terminal command
        result = subprocess.run(
            ["gcc", temp_c, "-o", output_exe],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n[SUCCESS] Compiled successfully to '{output_exe}'!")
        
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] GCC compilation failed:")
        print(e.stderr)
    finally:
        # Clean up temporary C file
        if os.path.exists(temp_c):
            os.remove(temp_c)

if __name__ == "__main__":
    build_chainscript("test.chain", "my_program.exe")