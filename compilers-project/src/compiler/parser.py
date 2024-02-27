from compiler.tokenizer import Token
import compiler.ast as ast

# Keep track of the position in the token list in a variable pos.
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

    def peek_backwards() -> Token:
        if pos - 1 >= 0:
            return tokens[pos - 1]

        return tokens[0]

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
        return ast.Literal(
            location=token.location,
            value=int(token.text)
        )

    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().location}: expected an identifier')

        token = consume()
        return ast.Identifier(
            location=token.location,
            name=token.text
        )

    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'bool_literal':
            raise Exception(f'{peek().location}: expected a boolean value')

        token = consume()
        if token.text == 'true' or token.text == 'True':
            return ast.Literal(
                location=token.location,
                value=True
            )

        if token.text == 'false' or token.text == 'False':
            return ast.Literal(
                location=token.location,
                value=False
            )

        raise Exception(
            f'{token.location}: expected boolean true/True or false/False')

    def parse_if_statement() -> ast.IfStatement:
        location = peek().location
        consume('if')
        condition = parse_expression()
        consume('then')
        true_branch = parse_expression()

        if peek().text == 'else':
            consume('else')
            false_branch = parse_expression()
        else:
            false_branch = None

        return ast.IfStatement(
            location,
            condition,
            true_branch,
            false_branch
        )

    def parse_while_loop() -> ast.WhileLoop:
        location = peek().location
        consume('while')
        condition = parse_expression()

        consume('do')
        body = parse_expression()

        return ast.WhileLoop(
            location,
            condition,
            body
        )

    def parse_function_call() -> ast.FunctionCall:
        consume('(')
        f = ast.FunctionCall(
            location=None,
            name=None,
            args=[]
        )

        while peek().text != ')':
            if peek().text == ',':
                consume(',')

            f.args.append(parse_expression())

        consume(')')
        return f

    def parse_var_declaration() -> ast.VarDeclaration:
        location = peek().location
        consume('var')
        initialize = parse_expression()

        return ast.VarDeclaration(
            location,
            initialize
        )

    def parse_block() -> ast.Block:
        location = peek().location
        consume('{')
        block = ast.Block(
            location,
            statements=[]
        )

        while peek().text != '}':
            if peek().type == 'end':
                raise Exception(f'{peek().location}: expected a "}}"')

            if peek().type == 'keyword' and peek().text == 'var':
                block.statements.append(parse_var_declaration())
                continue

            block.statements.append(parse_expression())
            if peek().text == ';':
                consume(';')
                if peek().text == '}':
                    location = peek().location
                    block.statements.append(ast.Literal(location, value=None))
            elif peek_backwards().text == '}':
                continue
            elif peek().text not in ['{', '}']:
                raise Exception(f'{peek().location}: expected ";" or "}}"')

        consume('}')

        return block

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()

        if peek().text == '{':
            return parse_block()

        if peek().type == 'integer':
            return parse_int_literal()

        if peek().type == 'identifier':
            identifier = parse_identifier()
            if peek().text == '(':
                f = parse_function_call()
                f.name = identifier
                f.location = identifier.location
                return f

            return identifier

        if peek().type == 'keyword':
            if peek().text == 'if':
                return parse_if_statement()

            if peek().text == 'while':
                return parse_while_loop()

            raise Exception(
                f'{peek().location}: unexpected keyword "{peek().text}"')

        if peek().type == 'bool_literal':
            return parse_bool_literal()

        if peek().text in ['-', 'not']:
            return parse_unary_op()

        raise Exception(
            f'{peek().location}: expected integer, identifier, keyword, boolean literal or unary operator')

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_unary_op() -> ast.Expression:
        location = peek().location
        if peek().text in ['-', 'not']:
            operator_token = consume()
            operator = operator_token.text
            expr = parse_factor()
            return ast.UnaryOp(
                location,
                operator,
                expr
            )

        raise Exception(
            f'{peek().location}: expected unary operator - or not')

    def parse_term() -> ast.Expression:
        left = parse_factor()

        while peek().text in ['*', '/', '%']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_polynomial() -> ast.Expression:
        left = parse_term()

        while peek().text in ['+', '-']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_comparison() -> ast.Expression:
        left = parse_polynomial()

        if peek().text in ['<=', '>=', '<', '>']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_polynomial()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_equality() -> ast.Expression:
        left = parse_comparison()

        if peek().text in ['==', '!=']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_comparison()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_logical_and() -> ast.Expression:
        left = parse_equality()

        while peek().text in ['and']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_equality()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_logical_or() -> ast.Expression:
        left = parse_logical_and()

        while peek().text in ['or']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_logical_and()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_expression() -> ast.Expression:
        left = parse_logical_or()

        if peek().text in ['=']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_expression_right()

            left = ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    def parse_expression_right() -> ast.Expression:
        left = parse_equality()

        if peek().text in ['=']:
            location = peek().location
            operator_token = consume()
            operator = operator_token.text
            right = parse_expression_right()
            return ast.BinaryOp(
                location,
                left,
                operator,
                right
            )

        return left

    result = parse_expression()

    if pos < len(tokens):
        raise Exception(f'Unexpected token: {tokens[pos]}')

    return result
