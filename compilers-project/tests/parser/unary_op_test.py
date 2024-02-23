import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_parse_unary_op() -> None:
    input = tokenize('test', 'not a')
    expected = ast.UnaryOp(
        op='not',
        expr=ast.Identifier(name='a')
    )

    assert parse(input) == expected


def test_also_parse_second_unary_op() -> None:
    input = tokenize('test', '- a')
    expected = ast.UnaryOp(
        op='-',
        expr=ast.Identifier(name='a')
    )

    assert parse(input) == expected


def test_recognize_unary_op_after_operator() -> None:
    input = tokenize('test', 'a - - b')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.UnaryOp(
            op='-',
            expr=ast.Identifier(name='b')
        )
    )

    assert parse(input) == expected


def test_expression_in_unary_op() -> None:
    input = tokenize('test', 'a + - (b or c)')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='+',
        right=ast.UnaryOp(
            op='-',
            expr=ast.BinaryOp(
                left=ast.Identifier(name='b'),
                op='or',
                right=ast.Identifier(name='c')
            )
        )
    )

    assert parse(input) == expected
