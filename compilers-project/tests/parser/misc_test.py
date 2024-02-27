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
