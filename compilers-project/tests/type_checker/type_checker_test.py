import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.types import BasicType, Bool, Int, Unit, FunType
from compiler.symtab import SymTab


def test_typecheck_returns_int() -> None:
    input = parse(tokenize('test', '1 + 2'))
    expected = Int

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_comparison_returns_bool() -> None:
    input = parse(tokenize('test', '1 + 2 < 2'))
    expected = Bool

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_comparing_bool_and_int_raises_exception() -> None:
    input = parse(tokenize('test', '(1 < 2) + 3'))
    t1 = BasicType('Bool')
    t2 = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'Operator + expected two Ints, got {t1} and {t2}'
    assert str(excep_info.value) == error


def test_if_then_returns_unit() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3'))
    expected = Unit

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_if_then_else_returns_int() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3 else 4'))
    expected = Int

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_if_then_else_returns_bool() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3 < 4 else 4 < 5'))
    expected = Bool

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_if_with_int_condition_raises_exception() -> None:
    input = parse(tokenize('test', 'if 1 then 2 else 3'))
    int_type = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'If condition was {int_type}'
    assert str(excep_info.value) == error


def test_if_with_differing_branch_types_raises_exception() -> None:
    input = parse(tokenize('test', 'if true then 2 else false'))
    t1 = BasicType('Int')
    t2 = BasicType('Bool')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'Branches had different types: {t1} and {t2}'
    assert str(excep_info.value) == error


def test_typechecking_untyped_var_declaration() -> None:
    input = parse(tokenize('test', 'var x = 123'))
    expected = Int

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_typechecking_assignment_types_match() -> None:
    input = parse(tokenize('test', '{ var x = 123; x = 2 }'))
    expected = Int

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_assignment_with_different_type_raises_exception() -> None:
    tokens = tokenize('test', '{ var x = 123; x = true }')
    input = parse(tokens)
    unexpected = tokens[7]
    t1 = BasicType('Int')
    t2 = BasicType('Bool')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'{unexpected.location}: types {t1} and {t2} do not match'
    assert str(excep_info.value) == error


def test_equality_requires_int_or_bool() -> None:
    tokens = tokenize('test', '{ { if true then false } == true }')
    input = parse(tokens)
    unexpected = tokens[7]

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'{unexpected.location}: types must be either Int or Bool'
    assert str(excep_info.value) == error


def test_equality_with_different_types_raises_exception() -> None:
    tokens = tokenize('test', '{ 1 == true }')
    input = parse(tokens)
    unexpected = tokens[2]
    t1 = BasicType('Int')
    t2 = BasicType('Bool')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'{unexpected.location}: types {t1} and {t2} do not match'
    assert str(excep_info.value) == error


def test_comparison_requires_ints() -> None:
    tokens = tokenize('test', 'true >= 2')
    input = parse(tokens)
    t1 = BasicType('Bool')
    t2 = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'Operator >= expected two Ints, got {t1} and {t2}'
    assert str(excep_info.value) == error


def test_unary_operator_requires_bool() -> None:
    tokens = tokenize('test', 'not 2')
    input = parse(tokens)
    unexpected = tokens[0]
    t1 = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'{unexpected.location}: expected type Bool, got {t1}'
    assert str(excep_info.value) == error


def test_or_operator_requires_bool() -> None:
    tokens = tokenize('test', '( 2 != 1 ) and 2')
    input = parse(tokens)
    unexpected = tokens[5]
    t1 = BasicType('Bool')
    t2 = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input, SymTab(locals={}, parent=None))

    error = f'{unexpected.location}: operator and expected two Bools, got {t1} and {t2}'
    assert str(excep_info.value) == error


def test_typechecking_function_call() -> None:
    input = parse(tokenize('test', 'print_int(1)'))
    expected = FunType(args=[Int], return_type=Unit)

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected


def test_typechecking_while_loop_returns_unit() -> None:
    input = parse(tokenize('test', 'var x = 0; while x < 2 do { x = x + 1 }'))
    expected = Unit

    assert typecheck(input, SymTab(locals={}, parent=None)) == expected
