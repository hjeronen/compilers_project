from compiler import ast
from compiler.types import Bool, Int, Type, Unit


def typecheck(node: ast.Expression | None) -> Type:
    if node is None:
        return Unit

    match node:

        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            else:
                raise Exception(f'Unknown type for literal {node.value}')

        case ast.BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)

            if node.op in ['+', '-', '*', '/']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(
                        f'Operator {node.op} expected two Ints, got {t1} and {t2}')
                return Int
            elif node.op in ['<']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(
                        f'Operator {node.op} expected two Ints, got {t1} and {t2}')
                return Bool
            else:
                raise Exception(f'Unknown operator {node.op}')

        case ast.IfStatement():
            t1 = typecheck(node.condition)
            if t1 is not Bool:
                raise Exception(f'If condition was {t1}')

            t2 = typecheck(node.true_branch)
            if node.false_branch is None:
                return Unit

            t3 = typecheck(node.false_branch)
            if t2 != t3:
                raise Exception(f'Branches had different types: {t2} and {t3}')

            return t2

        case _:
            raise Exception(f'Unknown AST type: {node}')
