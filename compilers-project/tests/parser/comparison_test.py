import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_comparison_operator() -> None:
    input = tokenize('test', '1 < 2 + 3')
    expected = ast.BinaryOp(
        location,
        left=ast.Literal(location, value=1),
        op='<',
        right=ast.BinaryOp(
            location,
            left=ast.Literal(location, value=2),
            op='+',
            right=ast.Literal(location, value=3)
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
        location,
        left=ast.BinaryOp(
            location,
            left=ast.Literal(location, value=1),
            op='<',
            right=ast.Literal(location, value=2)
        ),
        op='<',
        right=ast.Literal(location, value=3)
    )

    assert parse(input) == expected
