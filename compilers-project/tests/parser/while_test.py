import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parse_while_loop() -> None:
    input = tokenize('test', 'while true do x = x + 1')
    expected = ast.WhileLoop(
        location,
        condition=ast.Literal(location, value=True),
        body=ast.BinaryOp(
            location,
            left=ast.Identifier(location, name='x'),
            op='=',
            right=ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='x'),
                op='+',
                right=ast.Literal(location, value=1)
            )
        )
    )

    assert parse(input) == expected


def test_missing_do_raises_error() -> None:
    input = tokenize('test', 'while true x = x + 1')
    unexpected = input[2]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected "do"'
    assert str(excep_info.value) == error
