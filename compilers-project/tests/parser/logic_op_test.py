import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_logical_or() -> None:
    input = tokenize('test', 'if a or b or c then d')
    expected = ast.IfStatement(
        location,
        condition=ast.BinaryOp(
            location,
            left=ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='a'),
                op='or',
                right=ast.Identifier(location, name='b')
            ),
            op='or',
            right=ast.Identifier(location, name='c')
        ),
        true_branch=ast.Identifier(location, name='d'),
        false_branch=None
    )

    assert parse(input) == expected


def test_logical_and() -> None:
    input = tokenize('test', 'a and b and c or d')
    expected = ast.BinaryOp(
        location,
        left=ast.BinaryOp(
            location,
            left=ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='a'),
                op='and',
                right=ast.Identifier(location, name='b')
            ),
            op='and',
            right=ast.Identifier(location, name='c')
        ),
        op='or',
        right=ast.Identifier(location, name='d')
    )

    assert parse(input) == expected
