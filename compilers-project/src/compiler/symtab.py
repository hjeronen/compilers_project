import operator
from dataclasses import dataclass


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


interpreter_locals = {
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


def find_context(symtab: SymTab, name: str) -> SymTab | None:
    if name in symtab.locals:
        return symtab
    else:
        if symtab.parent is not None:
            return find_context(symtab.parent, name)
        else:
            return None
