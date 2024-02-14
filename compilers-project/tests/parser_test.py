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


def test_single_literal() -> None:
    input = tokenize('test', '11')
    assert parse(input) == ast.Literal(11)


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


def test_missing_term_raises_exception() -> None:
    input = tokenize('test', '5 - 2 +')
    unexpected = input[3]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'{unexpected.location}: expected an integer or an identifier'
    assert str(exec_info.value) == error


def test_consecutive_operators_raises_exception() -> None:
    input = tokenize('test', '5 - + 2')
    unexpected = input[2]

    with pytest.raises(Exception) as exec_info:
        parse(input)

    error = f'{unexpected.location}: expected an integer or an identifier'
    assert str(exec_info.value) == error


def test_multiply_operator_precedence() -> None:
    input = tokenize('test', 'a - 7 * 2')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.BinaryOp(
            left=ast.Literal(value=7),
            op='*',
            right=ast.Literal(value=2)
        )
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


def test_if_statement() -> None:
    input = tokenize('test', 'if a then b + c else x * y')
    expected = ast.IfStatement(
        condition=ast.Identifier(name='a'),
        true_branch=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='+',
            right=ast.Identifier(name='c')
        ),
        false_branch=ast.BinaryOp(
            left=ast.Identifier(name='x'),
            op='*',
            right=ast.Identifier(name='y')
        )
    )

    assert parse(input) == expected


def test_if_statement_without_else() -> None:
    input = tokenize('test', 'if a then b + c')
    expected = ast.IfStatement(
        condition=ast.Identifier(name='a'),
        true_branch=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='+',
            right=ast.Identifier(name='c')
        ),
        false_branch=None
    )

    assert parse(input) == expected


def test_if_as_sub_statement() -> None:
    input = tokenize('test', '1 + if true then 2 else 3')
    expected = ast.BinaryOp(
        left=ast.Literal(value=1),
        op='+',
        right=ast.IfStatement(
            condition=ast.Literal(value=True),
            true_branch=ast.Literal(value=2),
            false_branch=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected


def test_parsing_function_call() -> None:
    input = tokenize('test', 'f(x, y + z)')
    expected = ast.FunctionCall(
        name=ast.Identifier(name='f'),
        args=[
            ast.Identifier(name='x'),
            ast.BinaryOp(
                left=ast.Identifier(name='y'),
                op='+',
                right=ast.Identifier(name='z')
            )
        ]
    )

    assert parse(input) == expected


def test_function_with_longer_name() -> None:
    input = tokenize('test', 'print_out(x)')
    expected = ast.FunctionCall(
        name=ast.Identifier(name='print_out'),
        args=[
            ast.Identifier(name='x')
        ]
    )

    assert parse(input) == expected


# Will be added in Task 4
# def test_comparison_operator() -> None:
#     input = tokenize('test', '1 < 2 + 3')
#     expected = ast.BinaryOp(
#         left=ast.Literal(value=1),
#         op='<',
#         right=ast.BinaryOp(
#             left=ast.Literal(value=2),
#             op='+',
#             right=ast.Literal(value=3)
#         )
#     )

#     assert parse(input) == expected
