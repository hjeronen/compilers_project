import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_if_statement() -> None:
    input = tokenize('test', 'if a then b + c else x * y')
    expected = ast.IfStatement(
        location,
        condition=ast.Identifier(location, name='a'),
        true_branch=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='b'),
            op='+',
            right=ast.Identifier(location, name='c')
        ),
        false_branch=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='x'),
            op='*',
            right=ast.Identifier(location, name='y')
        )
    )

    assert parse(input) == expected


def test_if_statement_without_else() -> None:
    input = tokenize('test', 'if a then b + c')
    expected = ast.IfStatement(
        location,
        condition=ast.Identifier(location, name='a'),
        true_branch=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='b'),
            op='+',
            right=ast.Identifier(location, name='c')
        ),
        false_branch=None
    )

    assert parse(input) == expected


def test_if_as_sub_statement() -> None:
    input = tokenize('test', '1 + if true then 2 else 3')
    expected = ast.BinaryOp(
        location,
        left=ast.Literal(location, value=1),
        op='+',
        right=ast.IfStatement(
            location,
            condition=ast.Literal(location, value=True),
            true_branch=ast.Literal(location, value=2),
            false_branch=ast.Literal(location, value=3)
        )
    )

    assert parse(input) == expected
