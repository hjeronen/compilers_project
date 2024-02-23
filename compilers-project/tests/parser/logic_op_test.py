import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_logical_or() -> None:
    input = tokenize('test', 'if a or b or c then d')
    expected = ast.IfStatement(
        condition=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name='a'),
                op='or',
                right=ast.Identifier(name='b')
            ),
            op='or',
            right=ast.Identifier(name='c')
        ),
        true_branch=ast.Identifier(name='d'),
        false_branch=None
    )

    assert parse(input) == expected


def test_logical_and() -> None:
    input = tokenize('test', 'a and b and c or d')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name='a'),
                op='and',
                right=ast.Identifier(name='b')
            ),
            op='and',
            right=ast.Identifier(name='c')
        ),
        op='or',
        right=ast.Identifier(name='d')
    )

    assert parse(input) == expected
