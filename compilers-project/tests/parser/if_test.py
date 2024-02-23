import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_if_statement() -> None:
    input = tokenize('test', 'if a then b + c else x * y')
    expected = ast.IfStatement(
        condition=ast.Identifier(name='a'),
        true_branch=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='+',
            right=ast.Identifier(name='c')
        ),
        false_branch=ast.BinaryOp(
            left=ast.Identifier(name='x'),
            op='*',
            right=ast.Identifier(name='y')
        )
    )

    assert parse(input) == expected


def test_if_statement_without_else() -> None:
    input = tokenize('test', 'if a then b + c')
    expected = ast.IfStatement(
        condition=ast.Identifier(name='a'),
        true_branch=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='+',
            right=ast.Identifier(name='c')
        ),
        false_branch=None
    )

    assert parse(input) == expected


def test_if_as_sub_statement() -> None:
    input = tokenize('test', '1 + if true then 2 else 3')
    expected = ast.BinaryOp(
        left=ast.Literal(value=1),
        op='+',
        right=ast.IfStatement(
            condition=ast.Literal(value=True),
            true_branch=ast.Literal(value=2),
            false_branch=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected
