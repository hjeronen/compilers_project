from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    """Base class for types."""


@dataclass(frozen=True)
class BasicType(Type):
    name: str


Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')


@dataclass(frozen=True)
class FunType(Type):
    """Function types."""
