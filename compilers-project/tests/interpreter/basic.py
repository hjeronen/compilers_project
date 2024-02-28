import pytest
import compiler.ast as ast
from compiler.tokenizer import tokenize, AnyLocation
from compiler.parser import parse
from compiler.interpreter import interpret

location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_interpret_basic_binary_op() -> None:
    input = parse(tokenize('test', '2 + 3'))
    expected = 5

    assert interpret(input) == expected
