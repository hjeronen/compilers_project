import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.interpreter import interpret, SymTab, Unit

symtab = SymTab(locals={}, parent=None)


def test_interpret_basic_binary_op() -> None:
    input = parse(tokenize('test', '2 + 3'))
    expected = 5

    assert interpret(input, symtab) == expected


def test_interpret_var_declaration() -> None:
    input = parse(tokenize('test', 'var x = 0 + 1'))
    expected = Unit()

    assert interpret(input, symtab) == expected


def test_interpret_block() -> None:
    input = parse(tokenize('test', '{ var x = 0 + 1; x + 1 }'))
    expected = 2

    assert interpret(input, symtab) == expected


def test_assignment() -> None:
    input = parse(tokenize('test', '{ var x = 0 + 1; x = x + 1; x }'))
    expected = 2

    assert interpret(input, symtab) == expected


def test_interpret_inner_blocks() -> None:
    input = parse(tokenize('test', '{ var x = 0 + 1; { var x = 0 } x + 1 }'))
    expected = 2

    assert interpret(input, symtab) == expected


def test_empty_blocks() -> None:
    input = parse(tokenize('test', '{ }'))
    expected = Unit()

    assert interpret(input, symtab) == expected
