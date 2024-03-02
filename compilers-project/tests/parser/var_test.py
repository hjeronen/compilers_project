import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parsing_variable_declaration() -> None:
    input = tokenize('test', '{ var x = 123 }')
    expected = ast.Block(
        location,
        statements=[
            ast.VarDeclaration(
                location,
                name=ast.Identifier(location, name='x'),
                value=ast.Literal(location, value=123)
            )
        ]
    )

    assert parse(input) == expected


def test_var_only_allowed_on_top_level() -> None:
    input = tokenize('test', '{ if a < b then var x = 3 }')
    unexpected = input[6]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: unexpected keyword "var"'
    assert str(excep_info.value) == error


def test_top_level_var_without_block_allowed() -> None:
    input = tokenize('test', 'var x = 0')
    expected = ast.VarDeclaration(
        location,
        name=ast.Identifier(location, name='x'),
        value=ast.Literal(location, value=0)
    )

    assert parse(input) == expected


def test_top_level_var_after_block_allowed() -> None:
    input = tokenize('test', '{ var x = 0 } var x = 0')
    expected = ast.Block(
        location,
        statements=[
            ast.Block(
                location,
                statements=[
                    ast.VarDeclaration(
                        location,
                        name=ast.Identifier(location, name='x'),
                        value=ast.Literal(location, value=0)
                    )
                ]
            ),
            ast.VarDeclaration(
                location,
                name=ast.Identifier(location, name='x'),
                value=ast.Literal(location, value=0)
            )
        ]
    )

    assert parse(input) == expected


def test_top_level_var_before_block_allowed() -> None:
    input = tokenize('test', 'var x = 0; { var x = 0 }')
    expected = ast.Block(
        location,
        statements=[
            ast.VarDeclaration(
                location,
                name=ast.Identifier(location, name='x'),
                value=ast.Literal(location, value=0)
            ),
            ast.Block(
                location,
                statements=[
                    ast.VarDeclaration(
                        location,
                        name=ast.Identifier(location, name='x'),
                        value=ast.Literal(location, value=0)
                    )
                ]
            )
        ]
    )

    assert parse(input) == expected


def test_var_value_can_be_expression() -> None:
    input = tokenize('test', 'var x = 0 + 1')
    expected = ast.VarDeclaration(
        location,
        name=ast.Identifier(location, name='x'),
        value=ast.BinaryOp(
            location,
            left=ast.Literal(location, value=0),
            op='+',
            right=ast.Literal(location, value=1)
        )
    )

    assert parse(input) == expected


def test_number_not_allowed_as_var_name() -> None:
    input = tokenize('test', 'var 1 = 0 + 1')
    unexpected = input[1]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected an identifier'
    assert str(excep_info.value) == error
