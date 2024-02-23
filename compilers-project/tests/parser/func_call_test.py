import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_parsing_function_call() -> None:
    input = tokenize('test', 'f(x, y + z)')
    expected = ast.FunctionCall(
        name=ast.Identifier(name='f'),
        args=[
            ast.Identifier(name='x'),
            ast.BinaryOp(
                left=ast.Identifier(name='y'),
                op='+',
                right=ast.Identifier(name='z')
            )
        ]
    )

    assert parse(input) == expected


def test_function_with_longer_name() -> None:
    input = tokenize('test', 'print_out(x)')
    expected = ast.FunctionCall(
        name=ast.Identifier(name='print_out'),
        args=[
            ast.Identifier(name='x')
        ]
    )

    assert parse(input) == expected
