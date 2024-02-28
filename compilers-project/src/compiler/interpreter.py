from typing import Any
from compiler import ast
from typing import Union

Value = Union[int, bool, None]


def interpret(node: ast.Expression | None) -> Value:
    if node is None:
        return None

    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+':
                return a + b
            elif node.op == '<':
                return a < b
            else:
                raise Exception(f'{node.location}: unknown operator {node.op}')

        case ast.IfStatement():
            if interpret(node.condition):
                return interpret(node.true_branch)
            else:
                return interpret(node.false_branch)

        case _:
            raise Exception(f'{node.location}: unrecognized AST node')
