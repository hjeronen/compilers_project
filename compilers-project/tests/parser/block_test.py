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


def test_inner_blocks_without_semicolons_allowed() -> None:
    input = tokenize('test', '{ { a } { b } }')
    expected = ast.Block(
        statements=[
            ast.Block(
                statements=[
                    ast.Identifier(name='a')
                ]
            ),
            ast.Block(
                statements=[
                    ast.Identifier(name='b')
                ]
            )
        ]
    )

    assert parse(input) == expected


def test_identifiers_without_semicolons_raises_exception() -> None:
    input = tokenize('test', '{ a b }')
    unexpected = input[2]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected ";" or "}}"'
    assert str(excep_info.value) == error


def test_consecutive_semicolons_raises_exception() -> None:
    input = tokenize('test', '{ a;; b }')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected integer, identifier, keyword, boolean literal or unary operator'
    assert str(excep_info.value) == error


def test_if_then_without_semicolons_allowed() -> None:
    input = tokenize('test', '{ if true then { a } b }')
    expected = ast.Block(
        statements=[
            ast.IfStatement(
                condition=ast.Literal(value=True),
                true_branch=ast.Block(
                    statements=[
                        ast.Identifier(name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(name='b')
        ]
    )

    assert parse(input) == expected


def test_if_then_with_semicolons_allowed() -> None:
    input = tokenize('test', '{ if true then { a }; b }')
    expected = ast.Block(
        statements=[
            ast.IfStatement(
                condition=ast.Literal(value=True),
                true_branch=ast.Block(
                    statements=[
                        ast.Identifier(name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(name='b')
        ]
    )

    assert parse(input) == expected


def test_identifiers_after_block_without_semicolons_raises_exception() -> None:
    input = tokenize('test', '{ if true then { a } b c }')
    unexpected = input[8]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected ";" or "}}"'
    assert str(excep_info.value) == error


def test_identifiers_after_block_with_semicolons_allowed() -> None:
    input = tokenize('test', '{ if true then { a } b; c }')
    expected = ast.Block(
        statements=[
            ast.IfStatement(
                condition=ast.Literal(value=True),
                true_branch=ast.Block(
                    statements=[
                        ast.Identifier(name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(name='b'),
            ast.Identifier(name='c')
        ]
    )

    assert parse(input) == expected


def test_if_branches_with_blocks() -> None:
    input = tokenize('test', '{ if true then { a } else { b } 3 }')
    expected = ast.Block(
        statements=[
            ast.IfStatement(
                condition=ast.Literal(value=True),
                true_branch=ast.Block(
                    statements=[
                        ast.Identifier(name='a')
                    ]
                ),
                false_branch=ast.Block(
                    statements=[
                        ast.Identifier(name='b')
                    ]
                )
            ),
            ast.Literal(value=3)
        ]
    )

    assert parse(input) == expected


def test_assignment_with_block_allowed() -> None:
    input = tokenize('test', 'x = { { f(a) } { b } }')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='x'),
        op='=',
        right=ast.Block(
            statements=[
                ast.Block(
                    statements=[
                        ast.FunctionCall(
                            name=ast.Identifier(name='f'),
                            args=[
                                ast.Identifier(name='a')
                            ]
                        )
                    ]
                ),
                ast.Block(
                    statements=[
                        ast.Identifier(name='b')
                    ]
                )
            ]
        )
    )

    assert parse(input) == expected
