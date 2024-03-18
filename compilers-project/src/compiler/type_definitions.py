from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """Base class for types."""
    name: str


@dataclass(frozen=True)
class BasicType(Type):
    """Class for Int, Bool and Unit types."""


Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')


@dataclass(frozen=True)
class FunType(Type):
    """Function types."""
    args: list[Type]
    return_type: Type | None
