import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.interpreter import interpret, SymTab, Unit, locals
from typing import Any

symtab = SymTab(locals=locals, parent=None)


def test_interpret_basic_binary_op() -> None:
    input = parse(tokenize('test', '2 + 3'))
    expected = 5

    assert interpret(input, symtab) == expected


def test_interpret_var_declaration() -> None:
    input = parse(tokenize('test', 'var x = 0 + 1'))
    expected = Unit()

    assert interpret(input, symtab) == expected


def test_multiple_operators() -> None:
    input = parse(
        tokenize('test', '{ var x = 1; x = x * 10; x = x - 2; x = x / 2; x }'))
    expected = 4

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


def test_unary_op_one() -> None:
    input = parse(tokenize('test', '{ var a = 1; -a }'))
    expected = -1

    assert interpret(input, symtab) == expected


def test_unary_op_two() -> None:
    input = parse(tokenize('test', '{ var b = false; not b }'))
    expected = True

    assert interpret(input, symtab) == expected


def test_incompatible_unary_op_raises_exception() -> None:
    tokens = tokenize('test', '{ var b = 1; not b }')
    input = parse(tokens)
    with pytest.raises(Exception) as excep_info:
        interpret(input, symtab)

    error = f'{tokens[6].location}: incompatible operator not for integer'
    assert str(excep_info.value) == error


def test_print_int(capfd: Any) -> None:
    input = parse(tokenize('test', 'print_int(5)'))
    interpret(input, symtab)
    out, err = capfd.readouterr()

    assert out == '5\n'


def test_print_bool(capfd: Any) -> None:
    input = parse(tokenize('test', 'print_bool(true)'))
    interpret(input, symtab)
    out, err = capfd.readouterr()

    assert out == 'true\n'


def test_unknown_function_call_raises_exception() -> None:
    tokens = tokenize('test', 'print_something_else(5)')
    input = parse(tokens)
    with pytest.raises(Exception) as excep_info:
        interpret(input, symtab)

    error = f'{tokens[0].location}: unknown function call print_something_else'
    assert str(excep_info.value) == error


def test_if_then_statement() -> None:
    input = parse(tokenize('test', 'if 1 == 1 then x = 3'))
    expected = Unit()

    assert interpret(input, symtab) == expected


def test_if_then_else_statement() -> None:
    input = parse(tokenize('test', 'if 1 != 1 then x = 3 else x = 4'))
    expected = 4

    assert interpret(input, symtab) == expected


def test_shorcircuiting_or() -> None:
    program = ('var evaluated_right_hand_side = false;'
               + ' true or { evaluated_right_hand_side = true; true };'
               + ' evaluated_right_hand_side')

    input = parse(tokenize('test', program))
    expected = False

    assert interpret(input, symtab) == expected


def test_shorcircuiting_and() -> None:
    program = ('var evaluated_right_hand_side = false;'
               + ' false and { evaluated_right_hand_side = true; true };'
               + ' evaluated_right_hand_side')

    input = parse(tokenize('test', program))
    expected = False

    assert interpret(input, symtab) == expected
