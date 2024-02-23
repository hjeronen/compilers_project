import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_parsing_variable_declaration() -> None:
    input = tokenize('test', '{ var x = 123 }')
    expected = ast.Block(
        statements=[
            ast.VarDeclaration(
                initialize=ast.BinaryOp(
                    left=ast.Identifier(name='x'),
                    op='=',
                    right=ast.Literal(value=123)
                )
            )
        ]
    )

    assert parse(input) == expected


def test_var_outside_block_raises_exception() -> None:
    input = tokenize('test', 'var x = 123')
    unexpected = input[0]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: unexpected keyword "var"'
    assert str(excep_info.value) == error


def test_var_only_allowed_on_top_level() -> None:
    input = tokenize('test', '{ if a < b then var x = 3 }')
    unexpected = input[6]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: unexpected keyword "var"'
    assert str(excep_info.value) == error
