import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_equality_operator() -> None:
    input = tokenize('test', 'a != b and c + 5')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='!=',
            right=ast.Identifier(name='b')
        ),
        op='and',
        right=ast.BinaryOp(
            left=ast.Identifier(name='c'),
            op='+',
            right=ast.Literal(value=5)
        )
    )

    assert parse(input) == expected


def test_consecutive_equalities_raises_exception() -> None:
    input = tokenize('test', 'a != b == c')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_equality_with_comparison() -> None:
    input = tokenize('test', 'a != b < c')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='!=',
        right=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='<',
            right=ast.Identifier(name='c')
        )
    )

    assert parse(input) == expected


def test_parse_reminder() -> None:
    input = tokenize('test', 'a % b == b')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='%',
            right=ast.Identifier(name='b')
        ),
        op='==',
        right=ast.Identifier(name='b')
    )

    assert parse(input) == expected
