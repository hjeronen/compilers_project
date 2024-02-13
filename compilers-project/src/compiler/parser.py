from compiler.tokenizer import Token
import compiler.ast as ast

# Keep track of our position in the token list in a variable pos.
# Define a set of parsing functions to parse different kinds of AST subtrees.


def parse(tokens: list[Token]) -> ast.Expression | None:
    if len(tokens) == 0:
        return None

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

    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'bool_literal':
            raise Exception(f'{peek().location}: expected a boolean value')

        token = consume()
        if token.text == 'true' or token.text == 'True':
            return ast.Literal(value=True)

        if token.text == 'false' or token.text == 'False':
            return ast.Literal(value=False)

        raise Exception(
            f'{token.location}: expected boolean true/True or false/False')

    def parse_if_statement() -> ast.Expression:
        condition = parse_expression()
        true_branch = parse_expression()
        false_branch = None

        if peek().type == 'keyword':
            false_branch = parse_expression()

        return ast.IfStatement(
            condition,
            true_branch,
            false_branch
        )

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()

        if peek().type == 'integer':
            return parse_int_literal()

        if peek().type == 'identifier':
            return parse_identifier()

        if peek().type == 'bool_literal':
            return parse_bool_literal()

        if peek().type == 'keyword':
            text = peek().text
            if text == 'then' or text == 'else':
                consume(['then', 'else'])
                return parse_expression()

            if text == 'if':
                consume('if')
                return parse_if_statement()

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
            operator = operator_token.text
            right = parse_term()

            left = ast.BinaryOp(
                left,
                operator,
                right
            )

        return left

    def parse_expression_right() -> ast.Expression:
        left = parse_term()

        if peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_expression_right()
            return ast.BinaryOp(
                left,
                operator,
                right
            )

        return left

    result = parse_expression()

    if pos < len(tokens):
        raise Exception(f'Unexpected token: {tokens[pos]}')

    return result
