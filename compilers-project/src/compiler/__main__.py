import sys
from .tokenizer import tokenize
from .parser import parse
from .interpreter import interpret
from .type_checker import typecheck
from .ir_generator import generate_ir
from .assembly_generator import generate_assembly
from .assembler import assemble
from .symtab import SymTab, interpreter_locals, root_types
from .run_test_programs import check_test_cases

# TODO(student): add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]

Command 'interpret':
    Runs the interpreter on source code.

Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"


def main() -> int:
    command: str | None = None
    input_file: str | None = None
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    if input_file is None:
        input_file = 'no_file'

    if command == 'test_prints':
        source_code = read_source_code()

        print('------- Tokens --------')
        tokens = tokenize(input_file, source_code)
        for token in tokens:
            print(token)

        print('------- AST --------')
        ast_node = parse(tokens)
        if ast_node is None:
            raise Exception('AST node was none')
        print(ast_node)

        print('------- Interpreter --------')
        interpreter_symtab = SymTab(locals=interpreter_locals, parent=None)
        result = interpret(ast_node, interpreter_symtab)
        print(result)

        print('------- Typechecker --------')
        typechecker_symtab = SymTab(locals={}, parent=None)
        check_type = typecheck(ast_node, typechecker_symtab)
        print(check_type)

        print('------- IR --------')
        ir = generate_ir(root_types, ast_node)
        print('\n'.join([str(ins) for ins in ir]))

        print('------- Assembly --------')
        asm_code = generate_assembly(ir)
        print(asm_code)

    elif command == 'interpret':
        source_code = read_source_code()
        tokens = tokenize(input_file, source_code)
        ast_node = parse(tokens)
        if ast_node is None:
            raise Exception('AST node was none')
        interpreter_symtab = SymTab(locals=interpreter_locals, parent=None)
        result = interpret(ast_node, interpreter_symtab)
        print(result)
        typechecker_symtab = SymTab(locals={}, parent=None)
        check_type = typecheck(ast_node, typechecker_symtab)
        print(check_type)

    elif command == 'ir':
        source_code = read_source_code()
        tokens = tokenize(input_file, source_code)
        ast_node = parse(tokens)
        if ast_node is None:
            raise Exception('AST node was none')
        typechecker_symtab = SymTab(locals={}, parent=None)
        typecheck(ast_node, typechecker_symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        print('\n'.join([str(ins) for ins in ir_instructions]))

    elif command == 'asm':
        source_code = read_source_code()
        tokens = tokenize(input_file, source_code)
        ast_node = parse(tokens)
        if ast_node is None:
            raise Exception('AST node was none')
        typechecker_symtab = SymTab(locals={}, parent=None)
        typecheck(ast_node, typechecker_symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        asm_code = generate_assembly(ir_instructions)
        print(asm_code)

    elif command == 'compile':
        source_code = read_source_code()
        tokens = tokenize(input_file, source_code)
        ast_node = parse(tokens)
        if ast_node is None:
            raise Exception('AST node was none')
        typechecker_symtab = SymTab(locals={}, parent=None)
        typecheck(ast_node, typechecker_symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        asm_code = generate_assembly(ir_instructions)
        assemble(asm_code, 'compiled_program')

    elif command == 'end':
        check_test_cases()

    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
