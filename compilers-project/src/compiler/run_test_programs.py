import os
import subprocess
from dataclasses import dataclass
from .tokenizer import tokenize
from .parser import parse
from .type_checker import typecheck
from .ir_generator import generate_ir
from .assembly_generator import generate_assembly
from .assembler import assemble
from .symtab import SymTab, root_types


@dataclass
class TestCase:
    name: str
    input: str
    output: str


def read_file(relative_path: str) -> str:
    with open(relative_path, 'r') as f:
        return f.read()


def find_test_cases(file: str) -> list[TestCase]:
    cases = file.split('---\n')
    test_cases = []
    test_number = 0

    for case in cases:
        parts = case.split('prints')
        name = f'{file}_{test_number}'
        test_number += 1
        input = parts[0].strip().replace('input ', '', 1)
        output = parts[1].strip()
        test_cases.append(TestCase(
            name,
            input,
            output
        ))

    return test_cases


def get_all_testcases(directory: str) -> list[TestCase]:
    test_cases = []
    for filename in os.listdir(directory):
        file = read_file(directory + filename)
        tests = find_test_cases(file)

        for test in tests:
            test_cases.append(test)
    return test_cases


def compile(testcase: TestCase) -> None:
    tokens = tokenize(testcase.name, testcase.input)
    ast_node = parse(tokens)
    if ast_node is None:
        raise Exception('AST node was none')
    typechecker_symtab = SymTab(locals={}, parent=None)
    typecheck(ast_node, typechecker_symtab)
    local_root_types = root_types.copy()
    ir_instructions = generate_ir(local_root_types, ast_node)
    asm_code = generate_assembly(ir_instructions)
    assemble(asm_code, 'test_program')


def run_program_and_get_output(program_path: str) -> str:
    try:
        result = subprocess.run(
            ['./test_program'],
            input=None,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error running {program_path}: {e}")
        return ''


def check_test_cases() -> None:
    directory = 'test_programs/'
    test_cases = get_all_testcases(directory)
    successful = 0

    def run_test_case(testcase: TestCase) -> None:
        nonlocal successful
        compile(testcase)
        output = run_program_and_get_output('./')
        output = output.strip()
        try:
            assert output == testcase.output
            successful += 1
        except AssertionError:
            print(
                f'Error in {testcase}: the output was "{output}", expected "{testcase.output}"')

    for test_case in test_cases:
        run_test_case(test_case)

    if successful == len(test_cases):
        print(f'All {len(test_cases)} test cases succesful!')
    else:
        print(f'{successful} out of {len(test_cases)} test cases passed')
