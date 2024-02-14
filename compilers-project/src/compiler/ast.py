from dataclasses import dataclass


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression


@dataclass
class IfStatement(Expression):
    """AST node for conditional statements"""
    condition: Expression
    true_branch: Expression
    false_branch: Expression | None


@dataclass
class FunctionCall(Expression):
    """AST node for function calls"""
    name: Expression | None
    args: list[Expression]


...  # You get to define more later
