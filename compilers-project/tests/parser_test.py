from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation, Token


filename = 'test'

location = AnyLocation(
    file=filename,
    line=0,
    column=0
)


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
