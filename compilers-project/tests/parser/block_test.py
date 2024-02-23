import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize


def test_parse_block_with_result_expression() -> None:
    input = tokenize('test', '{f(a); x = y; f(x)}')
    expected = ast.Block(
        statements=[
            ast.FunctionCall(
                name=ast.Identifier(name='f'),
                args=[
                    ast.Identifier(name='a')
                ]
            ),
            ast.BinaryOp(
                left=ast.Identifier(name='x'),
                op='=',
                right=ast.Identifier(name='y')
            ),
            ast.FunctionCall(
                name=ast.Identifier(name='f'),
                args=[
                    ast.Identifier(name='x')
                ]
            )
        ]
    )

    assert parse(input) == expected


def test_parse_block_without_result_expression() -> None:
    input = tokenize('test', '{f(a); x = y; f(x);}')
    expected = ast.Block(
        statements=[
            ast.FunctionCall(
                name=ast.Identifier(name='f'),
                args=[
                    ast.Identifier(name='a')
                ]
            ),
            ast.BinaryOp(
                left=ast.Identifier(name='x'),
                op='=',
                right=ast.Identifier(name='y')
            ),
            ast.FunctionCall(
                name=ast.Identifier(name='f'),
                args=[
                    ast.Identifier(name='x')
                ]
            ),
            ast.Literal(value=None)
        ]
    )

    assert parse(input) == expected


def test_parse_block_missing_closing_brace_raises_exception() -> None:
    input = tokenize('test', '{f(a); x = y; f(x)')
    unexpected = input[13]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected ";" or "}}"'
    assert str(excep_info.value) == error


def test_parse_block_missing_opening_brace_raises_exception() -> None:
    input = tokenize('test', 'f(a); x = y; f(x)}')
    unexpected = input[4]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_inner_blocks() -> None:
    input = tokenize('test', '{ while f() do { x = 10; y = if g(x)'
                     + 'then { x = x + 1; x } else { g(x) }; g(y); }; 123 }')
    expected = ast.Block(
        statements=[
            ast.WhileLoop(
                condition=ast.FunctionCall(
                    name=ast.Identifier(name='f'),
                    args=[]
                ),
                body=ast.Block(
                    statements=[
                        ast.BinaryOp(
                            left=ast.Identifier(name='x'),
                            op='=',
                            right=ast.Literal(value=10)
                        ),
                        ast.BinaryOp(
                            left=ast.Identifier(name='y'),
                            op='=',
                            right=ast.IfStatement(
                                condition=ast.FunctionCall(
                                    name=ast.Identifier(name='g'),
                                    args=[
                                        ast.Identifier(name='x')
                                    ]
                                ),
                                true_branch=ast.Block(
                                    statements=[
                                        ast.BinaryOp(
                                            left=ast.Identifier(name='x'),
                                            op='=',
                                            right=ast.BinaryOp(
                                                left=ast.Identifier(name='x'),
                                                op='+',
                                                right=ast.Literal(value=1)
                                            )
                                        ),
                                        ast.Identifier(name='x')
                                    ]
                                ),
                                false_branch=ast.Block(
                                    statements=[
                                        ast.FunctionCall(
                                            name=ast.Identifier(name='g'),
                                            args=[
                                                ast.Identifier(name='x')
                                            ]
                                        )
                                    ]
                                )
                            )
                        ),
                        ast.FunctionCall(
                            name=ast.Identifier(name='g'),
                            args=[
                                ast.Identifier(name='y')
                            ]
                        ),
                        ast.Literal(value=None)
                    ]
                )
            ),
            ast.Literal(value=123)
        ]
    )

    assert parse(input) == expected


def test_missing_semicolon_raises_exception() -> None:
    input = tokenize('test', '{ x = y; f(y) f(x) }')
    unexpected = input[9]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected ";" or "}}"'
    assert str(excep_info.value) == error
