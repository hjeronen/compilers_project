import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parse_unary_op() -> None:
    input = tokenize('test', 'not a')
    expected = ast.UnaryOp(
        location,
        op='not',
        expr=ast.Identifier(location, name='a')
    )

    assert parse(input) == expected


def test_also_parse_second_unary_op() -> None:
    input = tokenize('test', '- a')
    expected = ast.UnaryOp(
        location,
        op='-',
        expr=ast.Identifier(location, name='a')
    )

    assert parse(input) == expected


def test_recognize_unary_op_after_operator() -> None:
    input = tokenize('test', 'a - - b')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='-',
        right=ast.UnaryOp(
            location,
            op='-',
            expr=ast.Identifier(location, name='b')
        )
    )

    assert parse(input) == expected


def test_expression_in_unary_op() -> None:
    input = tokenize('test', 'a + - (b or c)')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='+',
        right=ast.UnaryOp(
            location,
            op='-',
            expr=ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='b'),
                op='or',
                right=ast.Identifier(location, name='c')
            )
        )
    )

    assert parse(input) == expected
