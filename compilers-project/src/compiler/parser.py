from compiler.tokenizer import Token
import compiler.ast as ast

# Keep track of our position in the token list in a variable pos.
# Define a set of parsing functions to parse different kinds of AST subtrees.


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]

        return Token(
            location=tokens[-1].location,
            type='end',
            text=''
        )

    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')

        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}' for e in expected])
            raise Exception(
                f'{token.location}: expected one of: {comma_separated}')

        pos += 1
        return token

    def parse_int_literal() -> ast.Literal:
        if peek().type != 'integer':
            raise Exception(f'{peek().location}: expected an integer')

        token = consume()
        return ast.Literal(int(token.text))

    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().location}: expected an identifier')

        token = consume()
        return ast.Identifier(name=token.text)

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()

        if peek().type == 'integer':
            return parse_int_literal()

        if peek().type == 'identifier':
            return parse_identifier()

        raise Exception(
            f'{peek().location}: expected an integer or an identifier')

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_term() -> ast.Expression:
        left = parse_factor()

        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )

        return left

    def parse_expression() -> ast.Expression:
        left = parse_term()

        while peek().text in ['+', '-']:
            operator_token = consume()
            right = parse_term()

            left = ast.BinaryOp(
                left,
                operator_token.text,
                right
            )

        return left

    def parse_expression_right() -> ast.Expression:
        left = parse_term()

        if peek().text in ['+', '-']:
            operator_token = consume()
            right = parse_expression_right()
            return ast.BinaryOp(
                left,
                operator_token.text,
                right
            )

        return left

    return parse_expression()
