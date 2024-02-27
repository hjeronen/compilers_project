import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parsing_function_call() -> None:
    input = tokenize('test', 'f(x, y + z)')
    expected = ast.FunctionCall(
        location,
        name=ast.Identifier(location, name='f'),
        args=[
            ast.Identifier(location, name='x'),
            ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='y'),
                op='+',
                right=ast.Identifier(location, name='z')
            )
        ]
    )

    assert parse(input) == expected


def test_function_with_longer_name() -> None:
    input = tokenize('test', 'print_out(x)')
    expected = ast.FunctionCall(
        location,
        name=ast.Identifier(location, name='print_out'),
        args=[
            ast.Identifier(location, name='x')
        ]
    )

    assert parse(input) == expected
