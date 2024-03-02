from typing import Any
from compiler import ast
from typing import Union
from dataclasses import dataclass


@dataclass
class Unit:
    def __repr__(self) -> str:
        return 'unit'


Value = Union[int, Unit, bool, None]


@dataclass
class SymTab:
    locals: dict
    parent: 'SymTab | None'


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
                        context = find_context(symtab, node.left.name)
                        context.locals[node.left.name] = b
                    return b
                else:
                    raise Exception(
                        f'Only identifiers allowed as variable names.')

            if node.op == 'or':
                return a or b
            if node.op == 'and':
                return a and b
            elif node.op == '==':
                return a == b
            elif node.op == '!=':
                return a != b
            elif node.op == '<':
                return a < b
            elif node.op == '<=':
                return a <= b
            elif node.op == '>':
                return a > b
            elif node.op == '>=':
                return a >= b
            if node.op == '+':
                return a + b
            elif node.op == '-':
                return a - b
            elif node.op == '*':
                return a * b
            elif node.op == '/':
                return a // b
            elif node.op == '%':
                return a % b
            else:
                raise Exception(f'{node.location}: unknown operator {node.op}')

        case ast.IfStatement():
            if interpret(node.condition, symtab):
                return interpret(node.true_branch, symtab)
            else:
                return interpret(node.false_branch, symtab)

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

        case _:
            raise Exception(f'{node.location}: unrecognized AST node')
