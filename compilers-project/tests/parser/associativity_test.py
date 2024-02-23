import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_left_associativity() -> None:
    input = tokenize('test', 'a - 7 + 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='+',
        right=ast.Literal(value=2)
    )

    assert parse(input) == expected


def test_right_associativity() -> None:
    input = tokenize('test', 'a - 7 = 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='=',
        right=ast.Literal(value=2)
    )

    assert parse(input) == expected


def test_left_associativity_continues_after_right() -> None:
    input = tokenize('test', 'a - 7 = 2 + 2 - 3')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='=',
        right=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(value=2),
                op='+',
                right=ast.Literal(value=2)
            ),
            op='-',
            right=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected


def test_continuous_right_associativity() -> None:
    input = tokenize('test', 'a = b = c')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='=',
        right=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='=',
            right=ast.Identifier(name='c')
        )
    )

    assert parse(input) == expected
