import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation, Token


filename = 'test'

location = AnyLocation(
    file=filename,
    line=0,
    column=0
)


def test_binary_op() -> None:
    input = tokenize('test', '55 + 7')
    expected = ast.BinaryOp(
        left=ast.Literal(value=55),
        op='+',
        right=ast.Literal(value=7)
    )
    assert parse(input) == expected


def test_integers_and_identifiers() -> None:
    input = tokenize('test', 'a - 7')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.Literal(value=7)
    )
    assert parse(input) == expected


def test_left_associativity() -> None:
    input = tokenize('test', 'a - 7 + 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='+',
        right=ast.Literal(value=2)
    )

    assert parse(input) == expected


# def test_right_associativity() -> None:
#     input = tokenize('test', 'a - 7 + 2')
#     expected = ast.BinaryOp(
#         left=ast.Identifier(name='a'),
#         op='-',
#         right=ast.BinaryOp(
#             left=ast.Literal(value=7),
#             op='+',
#             right=ast.Literal(value=2)
#         )
#     )

#     assert parse(input) == expected


def test_parse_parenthesis() -> None:
    input = tokenize('test', 'a - (7 + 2)')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.BinaryOp(
            left=ast.Literal(value=7),
            op='+',
            right=ast.Literal(value=2)
        )
    )

    assert parse(input) == expected


def test_loose_terms_at_end_raises_exception() -> None:
    input = tokenize('test', 'a + b c')
    unexpected = input[3]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(exec_info.value) == error


def test_empty_string() -> None:
    input = tokenize('test', '')

    assert parse(input) == None


def test_missing_operator_raises_exception() -> None:
    input = tokenize('test', 'a b + c')
    unexpected = input[1]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(exec_info.value) == error


def test_missing_opening_parenthesis_raises_exception() -> None:
    input = tokenize('test', '5 - 2) + 3')
    unexpected = input[3]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(exec_info.value) == error


def test_missing_closing_parenthesis_raises_exception() -> None:
    input = tokenize('test', '5 - (2 + 3')
    unexpected = input[5]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'{unexpected.location}: expected ")"'
    assert str(exec_info.value) == error
