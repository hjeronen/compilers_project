from typing import Any, Callable, Union
from . import ast
from dataclasses import dataclass
from .symtab import SymTab, find_context, find_top_level_context


@dataclass
class Unit:
    def __repr__(self) -> str:
        return 'unit'


Value = Union[int, bool, None, Unit, Callable]


def interpret(node: ast.Expression | None, symtab: SymTab) -> Value:
    if node is None:
        return None

    top_context = find_top_level_context(symtab)

    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            context = find_context(symtab, node.name)
            if context is not None:
                return context.locals[node.name]
            else:
                raise Exception(f'Undefined variable name {node.name}')

        case ast.BinaryOp():
            if node.op == '=':
                value = interpret(node.right, symtab)
                if isinstance(node.left, ast.Identifier):
                    context = find_context(symtab, node.left.name)
                    if context is not None:
                        context.locals[node.left.name] = value
                        return value
                    else:
                        raise Exception(
                            f'Undefined variable name {node.left.name}')

                    # if node.left.name in symtab.locals:
                    #     symtab.locals[node.left.name] = value
                    # else:
                    #     parent_context = find_context(symtab, node.left.name)
                    #     parent_context.locals[node.left.name] = value

                else:
                    raise Exception(
                        f'Only identifiers allowed as variable names.')

            elif node.op in top_context.locals:
                a: Any = interpret(node.left, symtab)
                op = top_context.locals[node.op]

                if not callable(op):
                    raise Exception(f'{node.location}: {op} is not a function')

                elif node.op == 'and':
                    if a is False:
                        return False
                elif node.op == 'or':
                    if a is True:
                        return True

                b: Any = interpret(node.right, symtab)

                return op(a, b)

            else:
                raise Exception(f'{node.location}: unknown operator {node.op}')

        case ast.UnaryOp():
            expr = interpret(node.expr, symtab)
            if isinstance(expr, bool):
                if node.op in top_context.locals:
                    op = top_context.locals[node.op]
                    return op(expr)
                else:
                    raise Exception(
                        f'{node.location}: incompatible operator {node.op} for boolean')
            elif isinstance(expr, int):
                op = 'unary_' + node.op
                if op in top_context.locals:
                    op = top_context.locals[op]
                    return op(expr)
                else:
                    raise Exception(
                        f'{node.location}: incompatible operator {node.op} for integer')
            else:
                raise Exception(
                    f'{node.location}: expression must be an integer or boolean')

        case ast.IfStatement():
            cond = interpret(node.condition, symtab)
            if node.false_branch is None:
                if cond is True:
                    interpret(node.true_branch, symtab)
                    return Unit()
                elif cond is False:
                    return Unit()
                else:
                    raise Exception(
                        f'{node.location}: unable to evaluate condition')
            else:
                if cond is True:
                    return interpret(node.true_branch, symtab)
                elif cond is False:
                    return interpret(node.false_branch, symtab)
                else:
                    raise Exception(
                        f'{node.location}: unable to evaluate condition')

        case ast.VarDeclaration():
            if not isinstance(node.name, ast.Identifier):
                raise Exception('Only identifiers allowed as variable names')
            elif node.name.name in symtab.locals:
                raise Exception(f'Variable {node.name.name} already exists.')
            else:
                symtab.locals[node.name.name] = interpret(node.value, symtab)
                return Unit()

        case ast.Block():
            result = None
            context = SymTab(
                locals={},
                parent=symtab
            )

            for statement in node.statements:
                result = interpret(statement, context)

            if result is None:
                return Unit()

            return result

        case ast.WhileLoop():
            cond = interpret(node.condition, symtab)
            if cond is True:
                interpret(node.body, symtab)
                return interpret(node, symtab)
            elif cond is False:
                return Unit()
            else:
                raise Exception(
                    f'{node.location}: failed to evaluate condition')

        case ast.FunctionCall():
            if isinstance(node.name, ast.Identifier):
                name = node.name.name
                if name in top_context.locals:  # only built in functions supported for now
                    f = top_context.locals[name]
                    if not callable(f):
                        raise Exception(
                            f'{node.location}: {f} is not a function')
                    args = []
                    for arg in node.args:
                        args.append(interpret(arg, symtab))
                    result = f(*args)
                    return result
                else:
                    raise Exception(
                        f'{node.location}: unknown function call {name}')
            else:
                raise Exception(
                    f'{node.location}: function name has to be an Identifier')

        case _:
            raise Exception(f'{node.location}: unrecognized AST node')
