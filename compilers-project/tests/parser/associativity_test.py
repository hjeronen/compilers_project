import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_left_associativity() -> None:
    input = tokenize('test', 'a - 7 + 2')
    expected = ast.BinaryOp(
        location,
        left=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='a'),
            op='-',
            right=ast.Literal(location, value=7)
        ),
        op='+',
        right=ast.Literal(location, value=2)
    )

    assert parse(input) == expected


def test_right_associativity() -> None:
    input = tokenize('test', 'a - 7 = 2')
    expected = ast.BinaryOp(
        location,
        left=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='a'),
            op='-',
            right=ast.Literal(location, value=7)
        ),
        op='=',
        right=ast.Literal(location, value=2)
    )

    assert parse(input) == expected


def test_left_associativity_continues_after_right() -> None:
    input = tokenize('test', 'a - 7 = 2 + 2 - 3')
    expected = ast.BinaryOp(
        location,
        left=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='a'),
            op='-',
            right=ast.Literal(location, value=7)
        ),
        op='=',
        right=ast.BinaryOp(
            location,
            left=ast.BinaryOp(
                location,
                left=ast.Literal(location, value=2),
                op='+',
                right=ast.Literal(location, value=2)
            ),
            op='-',
            right=ast.Literal(location, value=3)
        )
    )

    assert parse(input) == expected


def test_continuous_right_associativity() -> None:
    input = tokenize('test', 'a = b = c')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='=',
        right=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='b'),
            op='=',
            right=ast.Identifier(location, name='c')
        )
    )

    assert parse(input) == expected
