import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_parse_while_loop() -> None:
    input = tokenize('test', 'while true do x = x + 1')
    expected = ast.WhileLoop(
        condition=ast.Literal(value=True),
        body=ast.BinaryOp(
            left=ast.Identifier(name='x'),
            op='=',
            right=ast.BinaryOp(
                left=ast.Identifier(name='x'),
                op='+',
                right=ast.Literal(value=1)
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
