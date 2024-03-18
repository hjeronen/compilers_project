from . import ast, ir
from .symtab import SymTab
from .type_definitions import Bool, Int, Type, Unit
from .ir import IRVar
from .tokenizer import Location


def generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type],
    root_expr: ast.Expression
) -> list[ir.Instruction]:
    var_types: dict[IRVar, Type] = root_types.copy()

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    next_var_number = 1
    next_label_number = 1

    def new_var(t: Type) -> IRVar:
        # Create a new unique IR variable and
        # add it to var_types
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        next_var_number += 1
        var_types[var] = t
        return var

    def new_label(loc: Location) -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(location=loc,
                         name=f'L{next_label_number}')
        next_label_number += 1
        return label

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(st: SymTab, expr: ast.Expression) -> IRVar:
        loc = expr.location

        match expr:
            case ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(ir.LoadBoolConst(
                            loc, expr.value, var))
                    case int():
                        var = new_var(Int)
                        ins.append(ir.LoadIntConst(
                            loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(
                            f"{loc}: unsupported literal: {type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return st.require(expr.name)

            case ast.BinaryOp():
                # Ask the symbol table to return the variable that refers
                # to the operator to call.
                var_op = st.require(expr.op)

                # Recursively emit instructions to calculate the operands.
                var_left = visit(st, expr.left)

                if expr.op == 'and':
                    l_right = new_label(loc)
                    l_skip = new_label(loc)
                    l_end = new_label(loc)

                    ins.append(ir.CondJump(loc, var_left, l_right, l_skip))

                    ins.append(l_right)
                    var_right = visit(st, expr.right)
                    result = new_var(Bool)
                    ins.append(ir.Copy(loc, var_right, result))
                    ins.append(ir.Jump(loc, l_end))

                    ins.append(l_skip)
                    ins.append(ir.LoadBoolConst(loc, False, result))
                    ins.append(ir.Jump(loc, l_end))

                    ins.append(l_end)

                    return result

                elif expr.op == 'or':
                    l_right = new_label(loc)
                    l_skip = new_label(loc)
                    l_end = new_label(loc)

                    ins.append(ir.CondJump(loc, var_left, l_skip, l_right))

                    ins.append(l_right)
                    var_right = visit(st, expr.right)
                    result = new_var(Bool)
                    ins.append(ir.Copy(loc, var_right, result))
                    ins.append(ir.Jump(loc, l_end))

                    ins.append(l_skip)
                    ins.append(ir.LoadBoolConst(loc, True, result))
                    ins.append(ir.Jump(loc, l_end))

                    ins.append(l_end)

                    return result

                var_right = visit(st, expr.right)
                if expr.op == '=':
                    if not isinstance(expr.left, ast.Identifier):
                        raise Exception(f'{loc}: expected an identifier')
                    ins.append(ir.Copy(loc, var_right, var_left))
                    return var_right
                else:
                    # Generate variable to hold the result.
                    var_result = new_var(expr.type)
                    # Emit a Call instruction that writes to that variable.
                    ins.append(ir.Call(
                        loc, var_op, [var_left, var_right], var_result))
                    return var_result

            case ast.UnaryOp():
                var_op = st.require('unary_' + expr.op)
                var_value = visit(st, expr.expr)
                if expr.op == 'not':
                    var_result = new_var(Bool)
                elif expr.op == '-':
                    var_result = new_var(Int)
                else:
                    raise Exception(f'{loc}: invalid unary operator {expr.op}')
                ins.append(ir.Call(loc, var_op, [var_value], var_result))
                return var_result

            case ast.IfStatement():
                if expr.false_branch is None:
                    # Create (but don't emit) some jump targets.
                    l_then = new_label(loc)
                    l_end = new_label(loc)

                    # Recursively emit instructions for
                    # evaluating the condition.
                    var_cond = visit(st, expr.condition)
                    # Emit a conditional jump instruction
                    # to jump to 'l_then' or 'l_end',
                    # depending on the content of 'var_cond'.
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    # Emit the label that marks the beginning of
                    # the "then" branch.
                    ins.append(l_then)
                    # Recursively emit instructions for the "then" branch.
                    visit(st, expr.true_branch)

                    # Emit the label that we jump to
                    # when we don't want to go to the "then" branch.
                    ins.append(l_end)

                    # An if-then expression doesn't return anything, so we
                    # return a special variable "unit".
                    return var_unit
                else:
                    ...  # "if-then-else" case
                    l_then = new_label(loc)
                    l_else = new_label(loc)
                    l_end = new_label(loc)

                    var_cond = visit(st, expr.condition)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_else))

                    ins.append(l_then)
                    var_result = visit(st, expr.true_branch)
                    ins.append(ir.Jump(loc, l_end))

                    ins.append(l_else)
                    var_else_result = visit(st, expr.false_branch)
                    ins.append(ir.Copy(loc, var_else_result, var_result))

                    ins.append(l_end)
                    return var_result

            case ast.VarDeclaration():
                value = visit(st, expr.value)
                var = new_var(expr.value.type)
                st.add_local(expr.name.name, var)
                ins.append(ir.Copy(loc, value, var))
                return var_unit

            case ast.Block():
                symtab = SymTab(locals={}, parent=st)
                for statement in expr.statements:
                    visit(symtab, statement)
                return var_unit

            case ast.FunctionCall():
                if expr.name is None:
                    raise Exception(f'{loc}: function has no name')
                f_var = st.require(expr.name.name)
                arg_vars = []
                for arg in expr.args:
                    arg_var = visit(st, arg)
                    arg_vars.append(arg_var)
                result_var = new_var(Unit)
                ins.append(ir.Call(loc, f_var, arg_vars, result_var))
                return result_var

            case ast.WhileLoop():
                l_start = new_label(loc)
                l_body = new_label(loc)
                l_end = new_label(loc)

                ins.append(l_start)
                condition = visit(st, expr.condition)
                ins.append(ir.CondJump(loc, condition, l_body, l_end))

                ins.append(l_body)
                visit(st, expr.body)
                ins.append(ir.Jump(loc, l_start))

                ins.append(l_end)

                return var_unit

            case _:
                raise Exception(f'Unsupported AST node: {expr}')

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymTab(locals={str: IRVar}, parent=None)
    for v in root_types.keys():
        if type(v) == str:
            root_symtab.add_local(v, v)
        else:
            root_symtab.add_local(v.name, v)

    ins.append(ir.Label(root_expr.location, 'start'))

    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)

    if var_types[var_final_result] == Int:
        ins.append(ir.Call(
            root_expr.location,
            IRVar('print_int'),
            [var_final_result],
            new_var(Int)
        ))
    elif var_types[var_final_result] == Bool:
        ins.append(ir.Call(
            root_expr.location,
            IRVar('print_bool'),
            [var_final_result],
            new_var(Bool)
        ))

    ins.append(ir.Return(root_expr.location))

    return ins
