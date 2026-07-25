# ⛓️ ChainScript Pro: Autonomous Agentic DSL & Local LLM Orchestration Engine

**ChainScript** is a two-pass compiled domain-specific language (DSL) and execution engine written in Python. It is engineered specifically for deterministic multi-agent orchestration, state-driven control flow, and local LLM execution.

By decoupling agent coordination from traditional object-oriented Python frameworks (such as LangChain, AutoGen, or CrewAI), ChainScript provides a lightweight, human-readable language syntax. It features static scope verification, neural quality gates, lexical variable binding, and native system-level execution primitives without the performance overhead or dependency sprawl of heavy Python frameworks.

---

## ⚡ Why ChainScript? (Eliminating Python Framework Bloat)

Traditional Python agentic frameworks suffer from massive abstraction layers, deep call stacks, heavy memory footprints, and non-deterministic control flows. ChainScript replaces thousands of lines of Python boilerplate with a lightweight, domain-specific grammar.

### 📊 Efficiency & Architectural Comparison

| Feature / Metric | Python Frameworks (LangChain / AutoGen) | ChainScript Pro OS |
| :--- | :--- | :--- |
| **Code Footprint** | 40–80+ lines of Python per agent loop | **5–15 lines** of clean `.chain` code |
| **Dependency Overhead** | Hundreds of transitive PyPI dependencies | **Zero runtime dependencies** (pure Python engine + local Ollama) |
| **Execution Validation** | Runtime crashes during deep execution | **Pass 1 Static Semantic Analysis** catches bugs before execution |
| **Control Flow** | Complex callback trees, state graphs, or hidden abstractions | **Native Turing-complete primitives** (`WHILE`, `IF/ELSE`, `TRY/CATCH`) |
| **Memory Scoping** | Global state mutations or opaque context objects | **Lexical Scope Stack (`Environment`)** with frame inheritance |
| **Safety & Evaluation** | Loose string matching or expensive wrapper classes | **Deterministic `JUDGE` Gates** enforcing binary outcomes |

---

### 🥊 Code Comparison: Agent Loop with Feedback

#### Traditional Python / LangChain Style (~50 Lines of Boilerplate)
```python
import os
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# High setup overhead, dynamic typing issues, deep object wrapping
dev_llm = Ollama(model="llama3", temperature=0.2)
rev_llm = Ollama(model="llama3", temperature=0.0)

dev_prompt = PromptTemplate(input_variables=["spec"], template="Write code for: {spec}")
rev_prompt = PromptTemplate(input_variables=["code"], template="Check this code: {code}. Reply PASS or FAIL.")

dev_chain = LLMChain(llm=dev_llm, prompt=dev_prompt)
rev_chain = LLMChain(llm=rev_llm, prompt=rev_prompt)

status = "FAIL"
attempts = 0
spec = "Write a python function that prints Hello World"

while status == "FAIL" and attempts < 3:
    attempts += 1
    print(f"Attempt: {attempts}")
    code = dev_chain.run(spec=spec)
    evaluation = rev_chain.run(code=code)
    if "PASS" in evaluation.upper():
        status = "PASS"
        with open("final_code.py", "w") as f:
            f.write(code)
    else:
        print("Retrying...")
```

#### ChainScript Equivalent (Clean, Declarative, Statically Checked)
```chainscript
AGENT Developer { MODEL "llama3" ROLE "Write Python code." TEMPERATURE 0.2 }
AGENT Reviewer  { MODEL "llama3" ROLE "Check for syntax errors." TEMPERATURE 0.0 }

SET spec = "Write a python function that prints Hello World"
SET status = "FAIL"

WHILE status == "FAIL" DO
    INVOKE Developer WITH spec AS code
    JUDGE code USING Reviewer AS status
    
    IF status == "PASS" THEN
        WRITE "final_code.py" code
    ENDIF
ENDWHILE
```

---

## 🏛️ Compiler & Interpreter Architecture

ChainScript processes `.chain` source files through a **5-stage compilation and execution pipeline**:

```text
  [.chain Source File]
           │
           ▼
     [ 1. Lexer ]           ──> Stream of typed Tokens with line tracking (lexer.py)
           │
           ▼
     [ 2. Parser ]          ──> Abstract Syntax Tree (AST) construction (parser_ast.py)
           │
           ▼
[ 3. Semantic Analyzer ]    ──> Pass 1: Static Scope, Agent & Function Validation (analyzer.py)
           │
           ▼
   [ 4. Interpreter ]       ──> Pass 2: Tree-Walking AST Evaluation & Ollama IPC (interpreter.py)
           │
           ▼
  [ 5. OS & I/O Engine ]    ──> Shell execution, disk persistence, and output logging
```

### Architectural Breakdown

#### 1. Lexical Analysis (`lexer.py`)
Tokenizes raw `.chain` source code into strongly-typed `Token` objects. Uses prioritized regex specifications to handle string literal escape sequences, keyphrase identifiers, numbers, operators, and line comments (`//`).

#### 2. Abstract Syntax Tree Parser (`parser_ast.py`)
A custom **Recursive Descent Parser** that converts token streams into structured AST nodes (`AgentDefNode`, `InvokeNode`, `JudgeNode`, `FunctionDefNode`, `IfNode`, etc.) without reliance on third-party parser tools like PLY or ANTLR.

#### 3. Static Semantic Analyzer (`analyzer.py` - Pass 1)
Traverses the AST prior to execution to enforce compile-time safety constraints:
* **Agent Binding:** Verifies that all `INVOKE` and `JUDGE` statements reference explicitly declared agents.
* **Lexical Scope Verification:** Validates variable references against a dynamic scope stack to prevent runtime variable lookup errors.
* **Function Arity Enforcement:** Validates argument counts on function calls against function parameter declarations.
* **Scope Hoisting:** Pre-registers function signatures and agent definitions across nested blocks.

#### 4. Tree-Walking Interpreter (`interpreter.py` - Pass 2)
Evaluates validated AST nodes sequentially. Features:
* **Lexical Environment Hierarchy:** Implements parent-linked `Environment` frames for variable binding inside functions, conditionals, and error blocks.
* **Unwinding Mechanics:** Handles function return states using controlled stack unwinding via custom `ReturnException` primitives.
* **Local LLM IPC:** Connects directly to local Ollama daemon instances via `ollama.chat` with custom model configurations and temperature controls.

---

## 🚀 Key Primitives & Features

* **Native Agent Declarations:** Personas are declared as top-level language entities (`AGENT`, `MODEL`, `ROLE`, `TEMPERATURE`).
* **Deterministic Quality Gates (`JUDGE`):** Transforms unstructured, stochastic LLM outputs into strictly bounded binary verdicts (`PASS` / `FAIL`) to govern conditional logic.
* **System Shell Primitives (`RUN_SHELL`):** Runs native OS-level commands and captures output streams into variables.
* **Fault-Tolerant Error Handling (`TRY / CATCH`):** Traps runtime failures (such as model timeouts or OS shell errors) into isolated catch scopes.
* **Built-in File I/O (`WRITE`, `READ`):** Directly reads from and writes to local disk files without importing external libraries.

---

## 📝 Complete Language Example: Autonomous Self-Correction Loop

```chainscript
// 1. Declare AI Agent Personas
AGENT Developer { 
    MODEL "llama3" 
    ROLE "Write clean Python code." 
    TEMPERATURE 0.2 
}

AGENT Reviewer { 
    MODEL "llama3" 
    ROLE "Perform static analysis on code. Respond ONLY with PASS or FAIL." 
    TEMPERATURE 0.0 
}

// 2. Define Function with Scoped Exception Handling
FUNCTION generate_candidate(prompt) {
    TRY {
        INVOKE Developer WITH prompt AS candidate_code
        RETURN candidate_code
    } CATCH err {
        RUN_SHELL "echo Generation failed with error: " + err
        RETURN "ERROR"
    }
}

// 3. Initialize Global State
SET prompt = "Write a python function that calculates fibonacci numbers."
SET status = "FAIL"
SET attempts = 0

// 4. Turing-Complete Loop with Neural Evaluation Gate
WHILE status == "FAIL" DO
    SET attempts = attempts + 1
    RUN_SHELL "echo 'Executing attempt: " + attempts + "'"
    
    SET code = generate_candidate(prompt)
    
    // Evaluate via Neural Logic Gate
    JUDGE code USING Reviewer AS status
    
    IF status == "PASS" THEN
        WRITE "fibonacci.py" code
        RUN_SHELL "echo 'Successfully generated quality code!'"
    ELSE
        RUN_SHELL "echo 'Quality check failed. Retrying...'"
    ENDIF
    
    // Hard break safety condition
    IF attempts == 3 THEN
        RUN_SHELL "echo 'Max attempts reached. Aborting pipeline.'"
        SET status = "PASS"
    ENDIF
ENDWHILE
```

---

## 📜 Formal Language Grammar (EBNF)

```ebnf
Program         ::= Statement*
Statement       ::= AgentDef | FuncDef | SetStmt | InvokeStmt | JudgeStmt 
                  | IfStmt | WhileStmt | TryCatchStmt | WriteFile | RunShell | ReturnStmt

AgentDef        ::= "AGENT" Identifier "{" PropList "}"
PropList        ::= ( ("MODEL" Expression) | ("ROLE" Expression) | ("TEMPERATURE" Expression) )*

FuncDef         ::= "FUNCTION" Identifier "(" ParamList? ")" "{" Statement* "}"
ParamList       ::= Identifier ("," Identifier)*

SetStmt         ::= "SET" Identifier "=" Expression
InvokeStmt      ::= "INVOKE" Identifier "WITH" Expression ("USING" "MEMORY" Identifier)? ("AS" Identifier)?
JudgeStmt       ::= "JUDGE" Expression "USING" Identifier "AS" Identifier

IfStmt          ::= "IF" Expression "THEN" Statement* ("ELSE" Statement*)? "ENDIF"
WhileStmt       ::= "WHILE" Expression "DO" Statement* "ENDWHILE"
TryCatchStmt    ::= "TRY" "{" Statement* "}" "CATCH" Identifier "{" Statement* "}"

WriteFile       ::= "WRITE" Expression Expression
RunShell        ::= "RUN_SHELL" Expression ("AS" Identifier)?
ReturnStmt      ::= "RETURN" Expression?

Expression      ::= Primary ( ("+" | "==" | "!=" | "CONTAINS") Primary )*
Primary         ::= Literal | Identifier | FuncCall | ReadFile | DictLiteral | ListLiteral
```

---

## 🧪 Testing & Verification

ChainScript includes an automated unit test suite (`test_chainscript.py`) built with `pytest` to test all phases of the engine:

```bash
# Run automated test suite
pytest
```

### Test Coverage
* **Lexer Verification:** Correct tokenization of keywords, literals, and symbol boundaries.
* **Parser Validation:** AST construction for control flow and agent declarations.
* **Environment Scoping:** Scope stack inheritance and dynamic lookups.
* **Static Analyzer Error Catching:** Verifies compile-time detection of undeclared variables, undefined agents, and invalid function call signatures.

---

## 🛠️ Installation & Getting Started

### Prerequisites
1. **Python 3.10+**
2. **Ollama** installed and running locally:
   ```bash
   ollama serve
   ollama pull llama3
   ```

### Setup Steps
```bash
# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/ChainScript.git](https://github.com/YOUR_USERNAME/ChainScript.git)
cd ChainScript

# 2. Install dependencies
pip install ollama pytest

# 3. Install custom VS Code Syntax Highlighting extension
python install_ext.py

# 4. Run the test suite
pytest

# 5. Execute a ChainScript file
python main.py agent_pipeline.chain
```

---

## 🎨 VS Code Integration

ChainScript comes with an automated syntax highlighter installer (`install_ext.py`). Running this script injects a custom TextMate grammar extension into your local Visual Studio Code installation directory (`~/.vscode/extensions/chainscript-language`), providing syntax highlighting for `.chain` files.