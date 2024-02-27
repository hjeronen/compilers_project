import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parse_parenthesis() -> None:
    input = tokenize('test', 'a - (7 + 2)')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='-',
        right=ast.BinaryOp(
            location,
            left=ast.Literal(location, value=7),
            op='+',
            right=ast.Literal(location, value=2)
        )
    )

    assert parse(input) == expected


def test_missing_opening_parenthesis_raises_exception() -> None:
    input = tokenize('test', '5 - 2) + 3')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_missing_closing_parenthesis_raises_exception() -> None:
    input = tokenize('test', '5 - (2 + 3')
    unexpected = input[5]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected ")"'
    assert str(excep_info.value) == error
