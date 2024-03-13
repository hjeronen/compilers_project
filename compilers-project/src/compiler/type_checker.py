from compiler import ast
from compiler.types import Bool, Int, Type, Unit, FunType
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
            if node.type is None:
                type = typecheck(node.value, symtab)
                if node.name.name not in symtab.locals:
                    symtab.locals[node.name.name] = type
                    return type
                else:
                    raise Exception(
                        f'Variable {node.name.name} has already been declared')
            else:
                raise Exception(f'Typed variables not supported yet.')

        case ast.BinaryOp():
            t1 = typecheck(node.left, symtab)
            t2 = typecheck(node.right, symtab)

            if node.op in ['+', '-', '*', '/', '%']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(
                        f'Operator {node.op} expected two Ints, got {t1} and {t2}')
                return t1

            elif node.op in ['or', 'and']:
                if t1 is not Bool or t2 is not Bool:
                    raise Exception(
                        f'{node.location}: operator {node.op} expected two Bools, got {t1} and {t2}')
                return t1

            elif node.op in ['<', '<=', '>', '>=']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(
                        f'Operator {node.op} expected two Ints, got {t1} and {t2}')
                return Bool

            elif node.op in ['==', '!=']:
                if t1 not in [Int, Bool] or t2 not in [Int, Bool]:
                    raise Exception(
                        f'{node.location}: types must be either Int or Bool')
                if t1 != t2:
                    raise Exception(
                        f'{node.location}: types {t1} and {t2} do not match')
                else:
                    return Bool

            elif node.op == '=':
                if t1 != t2:
                    raise Exception(
                        f'{node.location}: types {t1} and {t2} do not match')
                else:
                    return t1

            else:
                raise Exception(f'Unknown operator {node.op}')

        case ast.UnaryOp():
            type = typecheck(node.expr, symtab)
            if type is not Bool:
                raise Exception(
                    f'{node.location}: expected type Bool, got {type}')
            return type

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

        case ast.Block():
            type = Unit
            context = symtab
            if symtab.parent is not None:
                context = SymTab(locals={}, parent=symtab)

            for statement in node.statements:
                type = typecheck(statement, context)

            return type

        case ast.FunctionCall():
            args = []
            return_type = Unit

            for arg in node.args:
                arg_type = typecheck(arg, symtab)
                args.append(arg_type)

            fun_type = FunType(args, return_type)
            if node.name is not None:
                symtab.locals[node.name.name] = fun_type
                return fun_type
            else:
                raise Exception(f'{node.location}: function call has no name')

        case ast.WhileLoop():
            condition = typecheck(node.condition, symtab)
            if condition is not Bool:
                raise Exception(
                    f'{node.location}: while loop condition must be type Bool, got {condition}')

            typecheck(node.body, symtab)

            return Unit

        case _:
            raise Exception(f'Unknown AST type: {node}')
