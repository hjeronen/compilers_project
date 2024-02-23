import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_binary_op() -> None:
    input = tokenize('test', '55 + 7')
    expected = ast.BinaryOp(
        left=ast.Literal(value=55),
        op='+',
        right=ast.Literal(value=7)
    )
    assert parse(input) == expected


def test_loose_terms_at_end_raises_exception() -> None:
    input = tokenize('test', 'a + b c')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_missing_term_raises_exception() -> None:
    input = tokenize('test', '5 - 2 +')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected integer, identifier, keyword, boolean literal or unary operator'
    assert str(excep_info.value) == error


def test_missing_operator_raises_exception() -> None:
    input = tokenize('test', 'a b + c')
    unexpected = input[1]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_consecutive_operators_raises_exception() -> None:
    input = tokenize('test', '5 - + 2')
    unexpected = input[2]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected integer, identifier, keyword, boolean literal or unary operator'
    assert str(excep_info.value) == error


def test_multiply_operator_precedence() -> None:
    input = tokenize('test', 'a * 7 - 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='*',
            right=ast.Literal(value=7)
        ),
        op='-',
        right=ast.Literal(value=2)
    )

    assert parse(input) == expected


def test_division_operator_precedence() -> None:
    input = tokenize('test', 'a - 7 / 2')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.BinaryOp(
            left=ast.Literal(value=7),
            op='/',
            right=ast.Literal(value=2)
        )
    )

    assert parse(input) == expected
