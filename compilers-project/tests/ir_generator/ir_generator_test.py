import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.ir_generator import generate_ir
from compiler.symtab import SymTab, root_types


def test_generate_ir_works() -> None:
    input = parse(tokenize('test', '1 + 2 * 3'))
    if input is None:
        raise Exception('Failed to parse input')
    typecheck(input, SymTab(locals={}, parent=None))
    expected = [
        'LoadIntConst(1, x1)',
        'LoadIntConst(2, x2)',
        'LoadIntConst(3, x3)',
        'Call(*, [x2, x3], x4)',
        'Call(+, [x1, x4], x5)'
    ]

    ir_instructions = generate_ir(root_types, input)
    output = [str(ins) for ins in ir_instructions]

    assert output == expected
