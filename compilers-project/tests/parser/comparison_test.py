import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_comparison_operator() -> None:
    input = tokenize('test', '1 < 2 + 3')
    expected = ast.BinaryOp(
        left=ast.Literal(value=1),
        op='<',
        right=ast.BinaryOp(
            left=ast.Literal(value=2),
            op='+',
            right=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected


def test_consecutive_comparisons_raises_exception() -> None:
    input = tokenize('test', '1 < 2 < 3')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_consecutive_comparisons_with_parentheses_allowed() -> None:
    input = tokenize('test', '(1 < 2) < 3')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(value=1),
            op='<',
            right=ast.Literal(value=2)
        ),
        op='<',
        right=ast.Literal(value=3)
    )

    assert parse(input) == expected
