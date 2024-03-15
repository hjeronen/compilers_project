import operator
from dataclasses import dataclass
from typing import Any
from compiler.types import Bool, Int, FunType, Type, Unit
from compiler.ir import IRVar


@dataclass
class SymTab:
    locals: dict
    parent: 'SymTab | None'

    def require(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        elif self.parent is not None:
            self.parent.require(name)
        else:
            return None

    def add_local(self, name: str, value: Any) -> None:
        if name in self.locals:
            raise Exception(f'{name} is already defined')
        else:
            self.locals[name] = value


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

root_types: dict[IRVar, Type] = {
    IRVar('print_int'): Unit,
    IRVar('print_bool'): Unit,
    IRVar('read_int'): Unit,
    IRVar('or'): Bool,
    IRVar('and'): Bool,
    IRVar('and'): Bool,
    IRVar('!='): Bool,
    IRVar('<'): Bool,
    IRVar('<='): Bool,
    IRVar('>'): Bool,
    IRVar('>='): Bool,
    IRVar('+'): Int,
    IRVar('-'): Int,
    IRVar('*'): Int,
    IRVar('/'): Int,
    IRVar('%'): Int,
    IRVar('unary_-'): Bool,
    IRVar('not'): Bool
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
