import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_single_literal() -> None:
    input = tokenize('test', '11')
    assert parse(input) == ast.Literal(location, value=11)


def test_integers_and_identifiers() -> None:
    input = tokenize('test', 'a - 7')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='-',
        right=ast.Literal(location, value=7)
    )
    assert parse(input) == expected


def test_empty_string() -> None:
    input = tokenize('test', '')

    assert parse(input) == None


def test_multiple_top_level_expressions_allowed() -> None:
    input = tokenize('test', 'f(x); f(y)')
    expected = ast.Block(
        location,
        statements=[
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='x')
                ]
            ),
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='y')
                ]
            )
        ]
    )

    assert parse(input) == expected


def test_top_level_expression_without_semicolon_raises_exception() -> None:
    input = tokenize('test', 'var x = 0 { var x = 0 }')
    unexpected = input[4]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error
