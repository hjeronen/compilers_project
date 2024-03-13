from dataclasses import dataclass
from .tokenizer import Location


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: Location | None


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
class UnaryOp(Expression):
    """AST node for an unary operation like `- B` or `not B`"""
    op: str
    expr: Expression


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


@dataclass
class WhileLoop(Expression):
    """AST node for function calls"""
    condition: Expression
    body: Expression


@dataclass
class Block(Expression):
    """AST node for {} blocks"""
    statements: list[Expression]


@dataclass
class VarDeclaration(Expression):
    name: Identifier
    type: Identifier | None
    value: Expression


...  # You get to define more later
