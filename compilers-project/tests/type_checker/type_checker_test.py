import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.types import BasicType, Bool, Int, Unit


def test_typecheck_returns_int() -> None:
    input = parse(tokenize('test', '1 + 2'))
    expected = Int

    assert typecheck(input) == expected


def test_typecheck_returns_bool() -> None:
    input = parse(tokenize('test', '1 + 2 < 2'))
    expected = Bool

    assert typecheck(input) == expected


def test_comparing_bool_and_int_raises_exception() -> None:
    input = parse(tokenize('test', '(1 < 2) + 3'))
    t1 = BasicType('Bool')
    t2 = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input)

    error = f'Operator + expected two Ints, got {t1} and {t2}'
    assert str(excep_info.value) == error


def test_if_then_returns_unit() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3'))
    expected = Unit

    assert typecheck(input) == expected


def test_if_then_else_returns_int() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3 else 4'))
    expected = Int

    assert typecheck(input) == expected


def test_if_then_else_returns_bool() -> None:
    input = parse(tokenize('test', 'if 1 < 2 then 3 < 4 else 4 < 5'))
    expected = Bool

    assert typecheck(input) == expected


def test_if_with_int_condition_raises_exception() -> None:
    input = parse(tokenize('test', 'if 1 then 2 else 3'))
    int_type = BasicType('Int')

    with pytest.raises(Exception) as excep_info:
        typecheck(input)

    error = f'If condition was {int_type}'
    assert str(excep_info.value) == error


def test_if_with_differing_branch_types_raises_exception() -> None:
    input = parse(tokenize('test', 'if true then 2 else false'))
    t1 = BasicType('Int')
    t2 = BasicType('Bool')

    with pytest.raises(Exception) as excep_info:
        typecheck(input)

    error = f'Branches had different types: {t1} and {t2}'
    assert str(excep_info.value) == error
