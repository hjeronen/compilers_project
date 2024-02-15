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

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_empty_string() -> None:
    input = tokenize('test', '')

    assert parse(input) == None


def test_missing_operator_raises_exception() -> None:
    input = tokenize('test', 'a b + c')
    unexpected = input[1]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


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


def test_missing_term_raises_exception() -> None:
    input = tokenize('test', '5 - 2 +')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected an integer, an identifier, a boolean literal or if'
    assert str(excep_info.value) == error


def test_consecutive_operators_raises_exception() -> None:
    input = tokenize('test', '5 - + 2')
    unexpected = input[2]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'{unexpected.location}: expected an integer, an identifier, a boolean literal or if'
    assert str(excep_info.value) == error


def test_multiply_operator_precedence() -> None:
    input = tokenize('test', 'a * 7 - 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='*',
            right=ast.Literal(value=7)
        ),
        op='-',
        right=ast.Literal(value=2)
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


def test_right_associativity() -> None:
    input = tokenize('test', 'a - 7 = 2')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='=',
        right=ast.Literal(value=2)
    )

    assert parse(input) == expected


def test_left_associativity_continues_after_right() -> None:
    input = tokenize('test', 'a - 7 = 2 + 2 - 3')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='-',
            right=ast.Literal(value=7)
        ),
        op='=',
        right=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(value=2),
                op='+',
                right=ast.Literal(value=2)
            ),
            op='-',
            right=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected


def test_continuous_right_associativity() -> None:
    input = tokenize('test', 'a = b = c')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='=',
        right=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='=',
            right=ast.Identifier(name='c')
        )
    )

    assert parse(input) == expected


def test_logical_or() -> None:
    input = tokenize('test', 'if a or b or c then d')
    expected = ast.IfStatement(
        condition=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name='a'),
                op='or',
                right=ast.Identifier(name='b')
            ),
            op='or',
            right=ast.Identifier(name='c')
        ),
        true_branch=ast.Identifier(name='d'),
        false_branch=None
    )

    assert parse(input) == expected


def test_logical_and() -> None:
    input = tokenize('test', 'a and b and c or d')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name='a'),
                op='and',
                right=ast.Identifier(name='b')
            ),
            op='and',
            right=ast.Identifier(name='c')
        ),
        op='or',
        right=ast.Identifier(name='d')
    )

    assert parse(input) == expected


def test_comparison_operator() -> None:
    input = tokenize('test', '1 < 2 + 3')
    expected = ast.BinaryOp(
        left=ast.Literal(value=1),
        op='<',
        right=ast.BinaryOp(
            left=ast.Literal(value=2),
            op='+',
            right=ast.Literal(value=3)
        )
    )

    assert parse(input) == expected


def test_consecutive_comparisons_raises_exception() -> None:
    input = tokenize('test', '1 < 2 < 3')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_consecutive_comparisons_with_parentheses_allowed() -> None:
    input = tokenize('test', '(1 < 2) < 3')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(value=1),
            op='<',
            right=ast.Literal(value=2)
        ),
        op='<',
        right=ast.Literal(value=3)
    )

    assert parse(input) == expected


def test_equality_operator() -> None:
    input = tokenize('test', 'a != b and c + 5')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='!=',
            right=ast.Identifier(name='b')
        ),
        op='and',
        right=ast.BinaryOp(
            left=ast.Identifier(name='c'),
            op='+',
            right=ast.Literal(value=5)
        )
    )

    assert parse(input) == expected


def test_consecutive_equalities_raises_exception() -> None:
    input = tokenize('test', 'a != b == c')
    unexpected = input[3]

    with pytest.raises(Exception) as excep_info:
        parse(input)

    error = f'Unexpected token: {unexpected}'
    assert str(excep_info.value) == error


def test_equality_with_comparison() -> None:
    input = tokenize('test', 'a != b < c')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='!=',
        right=ast.BinaryOp(
            left=ast.Identifier(name='b'),
            op='<',
            right=ast.Identifier(name='c')
        )
    )

    assert parse(input) == expected


def test_parse_reminder() -> None:
    input = tokenize('test', 'a % b == b')
    expected = ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name='a'),
            op='%',
            right=ast.Identifier(name='b')
        ),
        op='==',
        right=ast.Identifier(name='b')
    )

    assert parse(input) == expected


def test_parse_unary_op() -> None:
    input = tokenize('test', 'not a')
    expected = ast.UnaryOp(
        op='not',
        expr=ast.Identifier(name='a')
    )

    assert parse(input) == expected


def test_also_parse_second_unary_op() -> None:
    input = tokenize('test', '- a')
    expected = ast.UnaryOp(
        op='-',
        expr=ast.Identifier(name='a')
    )

    assert parse(input) == expected


def test_recognize_unary_op_after_operator() -> None:
    input = tokenize('test', 'a - - b')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='-',
        right=ast.UnaryOp(
            op='-',
            expr=ast.Identifier(name='b')
        )
    )

    assert parse(input) == expected


def test_expression_in_unary_op() -> None:
    input = tokenize('test', 'a + - (b or c)')
    expected = ast.BinaryOp(
        left=ast.Identifier(name='a'),
        op='+',
        right=ast.UnaryOp(
            op='-',
            expr=ast.BinaryOp(
                left=ast.Identifier(name='b'),
                op='or',
                right=ast.Identifier(name='c')
            )
        )
    )

    assert parse(input) == expected
