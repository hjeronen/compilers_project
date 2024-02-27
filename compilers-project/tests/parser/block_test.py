import pytest
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_parse_block_with_result_expression() -> None:
    input = tokenize('test', '{f(a); x = y; f(x)}')
    expected = ast.Block(
        location,
        statements=[
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='a')
                ]
            ),
            ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='x'),
                op='=',
                right=ast.Identifier(location, name='y')
            ),
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='x')
                ]
            )
        ]
    )

    assert parse(input) == expected


def test_parse_block_without_result_expression() -> None:
    input = tokenize('test', '{f(a); x = y; f(x);}')
    expected = ast.Block(
        location,
        statements=[
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='a')
                ]
            ),
            ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='x'),
                op='=',
                right=ast.Identifier(location, name='y')
            ),
            ast.FunctionCall(
                location,
                name=ast.Identifier(location, name='f'),
                args=[
                    ast.Identifier(location, name='x')
                ]
            ),
            ast.Literal(location, value=None)
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
    unexpected = input[13]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_inner_blocks() -> None:
    input = tokenize('test', '{ while f() do { x = 10; y = if g(x)'
                     + 'then { x = x + 1; x } else { g(x) }; g(y); }; 123 }')
    expected = ast.Block(
        location,
        statements=[
            ast.WhileLoop(
                location,
                condition=ast.FunctionCall(
                    location,
                    name=ast.Identifier(location, name='f'),
                    args=[]
                ),
                body=ast.Block(
                    location,
                    statements=[
                        ast.BinaryOp(
                            location,
                            left=ast.Identifier(location, name='x'),
                            op='=',
                            right=ast.Literal(location, value=10)
                        ),
                        ast.BinaryOp(
                            location,
                            left=ast.Identifier(location, name='y'),
                            op='=',
                            right=ast.IfStatement(
                                location,
                                condition=ast.FunctionCall(
                                    location,
                                    name=ast.Identifier(location, name='g'),
                                    args=[
                                        ast.Identifier(location, name='x')
                                    ]
                                ),
                                true_branch=ast.Block(
                                    location,
                                    statements=[
                                        ast.BinaryOp(
                                            location,
                                            left=ast.Identifier(
                                                location, name='x'),
                                            op='=',
                                            right=ast.BinaryOp(
                                                location,
                                                left=ast.Identifier(
                                                    location, name='x'),
                                                op='+',
                                                right=ast.Literal(
                                                    location, value=1)
                                            )
                                        ),
                                        ast.Identifier(location, name='x')
                                    ]
                                ),
                                false_branch=ast.Block(
                                    location,
                                    statements=[
                                        ast.FunctionCall(
                                            location,
                                            name=ast.Identifier(
                                                location, name='g'),
                                            args=[
                                                ast.Identifier(
                                                    location, name='x')
                                            ]
                                        )
                                    ]
                                )
                            )
                        ),
                        ast.FunctionCall(
                            location,
                            name=ast.Identifier(location, name='g'),
                            args=[
                                ast.Identifier(location, name='y')
                            ]
                        ),
                        ast.Literal(location, value=None)
                    ]
                )
            ),
            ast.Literal(location, value=123)
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
        location,
        statements=[
            ast.Block(
                location,
                statements=[
                    ast.Identifier(location, name='a')
                ]
            ),
            ast.Block(
                location,
                statements=[
                    ast.Identifier(location, name='b')
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
        location,
        statements=[
            ast.IfStatement(
                location,
                condition=ast.Literal(location, value=True),
                true_branch=ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(location, name='b')
        ]
    )

    assert parse(input) == expected


def test_if_then_with_semicolons_allowed() -> None:
    input = tokenize('test', '{ if true then { a }; b }')
    expected = ast.Block(
        location,
        statements=[
            ast.IfStatement(
                location,
                condition=ast.Literal(location, value=True),
                true_branch=ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(location, name='b')
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
        location,
        statements=[
            ast.IfStatement(
                location,
                condition=ast.Literal(location, value=True),
                true_branch=ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='a')
                    ]
                ),
                false_branch=None
            ),
            ast.Identifier(location, name='b'),
            ast.Identifier(location, name='c')
        ]
    )

    assert parse(input) == expected


def test_if_branches_with_blocks() -> None:
    input = tokenize('test', '{ if true then { a } else { b } 3 }')
    expected = ast.Block(
        location,
        statements=[
            ast.IfStatement(
                location,
                condition=ast.Literal(location, value=True),
                true_branch=ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='a')
                    ]
                ),
                false_branch=ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='b')
                    ]
                )
            ),
            ast.Literal(location, value=3)
        ]
    )

    assert parse(input) == expected


def test_assignment_with_block_allowed() -> None:
    input = tokenize('test', 'x = { { f(a) } { b } }')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='x'),
        op='=',
        right=ast.Block(
            location,
            statements=[
                ast.Block(
                    location,
                    statements=[
                        ast.FunctionCall(
                            location,
                            name=ast.Identifier(location, name='f'),
                            args=[
                                ast.Identifier(location, name='a')
                            ]
                        )
                    ]
                ),
                ast.Block(
                    location,
                    statements=[
                        ast.Identifier(location, name='b')
                    ]
                )
            ]
        )
    )

    assert parse(input) == expected


def test_empty_block_allowed() -> None:
    input = tokenize('test', '{ }')
    expected = ast.Block(
        location,
        statements=[]
    )

    assert parse(input) == expected


def test_multiple_top_level_blocks_allowed() -> None:
    input = tokenize('test', '{ a } { b }')
    expected = ast.Block(
        location,
        statements=[
            ast.Block(
                location,
                statements=[
                    ast.Identifier(location, name='a')
                ]
            ),
            ast.Block(
                location,
                statements=[
                    ast.Identifier(location, name='b')
                ]
            )
        ]
    )

    assert parse(input) == expected
