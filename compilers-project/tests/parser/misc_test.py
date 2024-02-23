import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_single_literal() -> None:
    input = tokenize('test', '11')
    assert parse(input) == ast.Literal(11)


def test_integers_and_identifiers() -> None:
    input = tokenize('test', 'a - 7')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.Literal(value=7)
    )
    assert parse(input) == expected


def test_empty_string() -> None:
    input = tokenize('test', '')

    assert parse(input) == None
