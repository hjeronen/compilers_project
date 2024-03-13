from compiler import ast
from compiler.types import Bool, Int, Type, Unit
from .symtab import SymTab, find_context, find_top_level_context


def typecheck(node: ast.Expression | None, symtab: SymTab) -> Type:
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

        case ast.Identifier():
            context = find_context(symtab, node.name)
            if context is not None:
                return context.locals[node.name]
            else:
                raise Exception(f'Unknown identifier {node.name}')

        case ast.VarDeclaration():
            raise Exception(f'Not supported yet.')

        case ast.BinaryOp():
            t1 = typecheck(node.left, symtab)
            t2 = typecheck(node.right, symtab)

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
            t1 = typecheck(node.condition, symtab)
            if t1 is not Bool:
                raise Exception(f'If condition was {t1}')

            t2 = typecheck(node.true_branch, symtab)
            if node.false_branch is None:
                return Unit

            t3 = typecheck(node.false_branch, symtab)
            if t2 != t3:
                raise Exception(f'Branches had different types: {t2} and {t3}')

            return t2

        case _:
            raise Exception(f'Unknown AST type: {node}')
