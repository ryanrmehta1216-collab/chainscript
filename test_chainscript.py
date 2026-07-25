import pytest
from lexer import lex
from parser_ast import Parser, AgentDefNode
from interpreter import Environment
from analyzer import SemanticAnalyzer, SemanticError

# Test 1: Lexer Tokenization
def test_lexer_tokenization():
    code = 'AGENT Dev { MODEL "llama3" }'
    tokens = lex(code)
    token_types = [t.type for t in tokens]
    assert "KEYWORD" in token_types
    assert "IDENTIFIER" in token_types

# Test 2: Parser AST Construction
def test_parser_agent():
    code = 'AGENT Reviewer { MODEL "llama3" ROLE "Check code" }'
    tokens = lex(code)
    ast = Parser(tokens).parse()
    assert len(ast) == 1
    assert isinstance(ast[0], AgentDefNode)
    assert ast[0].name == "Reviewer"

# Test 3: Environment Scoping
def test_environment_scoping():
    parent_env = Environment()
    parent_env.set("x", 10)
    child_env = Environment(parent=parent_env)
    assert child_env.get("x") == 10  # Inherited scope

# Test 4: Analyzer Catches Undeclared Agent
def test_analyzer_undeclared_agent():
    code = 'INVOKE FakeAgent WITH "hello" AS res'
    tokens = lex(code)
    ast = Parser(tokens).parse()
    analyzer = SemanticAnalyzer()
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)
    