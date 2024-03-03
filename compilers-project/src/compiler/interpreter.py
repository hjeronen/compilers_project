import inspect
import operator
import types
from typing import Any, Callable
from compiler import ast
from typing import Union
from dataclasses import dataclass


@dataclass
class Unit:
    def __repr__(self) -> str:
        return 'unit'


Value = Union[int, bool, None, Unit, Callable]


@dataclass
class SymTab:
    locals: dict
    parent: 'SymTab | None'


def print_int(i: int) -> None:
    print(i)


def print_bool(value: bool) -> None:
    if value:
        print('true')
    else:
        print('false')


def read_int() -> int:
    value = input()
    return int(value)


locals = {
    'print_int': print_int,
    'print_bool': print_bool,
    'read_int': read_int,
    'or': operator.or_,
    'and': operator.and_,
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.floordiv,
    '%': operator.mod,
    'unary_-': operator.neg,
    'not': operator.not_
}


def find_top_level_context(symtab: SymTab) -> SymTab:
    if symtab.parent is not None:
        return find_top_level_context(symtab.parent)
    return symtab


def find_context(symtab: SymTab, name: str) -> SymTab:
    if name not in symtab.locals:
        if symtab.parent is not None:
            return find_context(symtab.parent, name)
        else:
            raise Exception(f'Undefined variable name {name}')
    else:
        return symtab


def interpret(node: ast.Expression | None, symtab: SymTab) -> Value:
    if node is None:
        return None

    context = find_top_level_context(symtab)

    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            context = find_context(symtab, node.name)
            return context.locals[node.name]

        case ast.BinaryOp():
            a: Any = interpret(node.left, symtab)
            b: Any = interpret(node.right, symtab)

            if node.op == '=':
                if isinstance(node.left, ast.Identifier):
                    if node.left.name in symtab.locals:
                        symtab.locals[node.left.name] = b
                    else:
                        parent_context = find_context(symtab, node.left.name)
                        parent_context.locals[node.left.name] = b
                    return b
                else:
                    raise Exception(
                        f'Only identifiers allowed as variable names.')

            if node.op in context.locals:
                op = context.locals[node.op]
                if not callable(op):
                    raise Exception(f'{node.location}: {op} is not a function')
                return op(a, b)
            else:
                raise Exception(f'{node.location}: unknown operator {node.op}')

        case ast.UnaryOp():
            expr = interpret(node.expr, symtab)
            if isinstance(expr, bool):
                if node.op in context.locals:
                    op = context.locals[node.op]
                    return op(expr)
                else:
                    raise Exception(
                        f'{node.location}: incompatible operator {node.op} for boolean')
            elif isinstance(expr, int):
                op = 'unary_' + node.op
                if op in context.locals:
                    op = context.locals[op]
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

        case ast.FunctionCall():
            if isinstance(node.name, ast.Identifier):
                name = node.name.name
                if name in context.locals:
                    f = context.locals[name]
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
