from dataclasses import dataclass
from compiler.tokenizer import tokenize, Location, Token


@dataclass
class AnyLocation(Location):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location)


location = AnyLocation(
    file='test',
    line=0,
    column=0
)


def test_tokenizer_basics() -> None:
    tokens = [
        Token(
            text='if',
            type='identifier',
            source=location
        ),
        Token(
            text='3',
            type='integer',
            source=location
        ),
        Token(
            text='while',
            type='identifier',
            source=location
        )
    ]
    assert tokenize('if  3\nwhile') == tokens


def test_keywords() -> None:
    tokens = [
        Token(
            text='if',
            type='identifier',
            source=location
        ),
        Token(
            text='elif',
            type='identifier',
            source=location
        ),
        Token(
            text='else',
            type='identifier',
            source=location
        ),
        Token(
            text='while',
            type='identifier',
            source=location
        ),
        Token(
            text='not',
            type='identifier',
            source=location
        )
    ]
    assert tokenize('if elif else while not') == tokens


def test_variable_names() -> None:
    tokens = [
        Token(
            text='thisIsValid',
            type='identifier',
            source=location
        ),
        Token(
            text='python_style',
            type='identifier',
            source=location
        ),
        Token(
            text='variable1',
            type='identifier',
            source=location
        )
    ]
    assert tokenize('thisIsValid python_style variable1') == tokens


def test_underscored_variables() -> None:
    tokens = [
        Token(
            text='_one',
            type='identifier',
            source=location
        ),
        Token(
            text='__two',
            type='identifier',
            source=location
        ),
        Token(
            text='__multiple_underscores',
            type='identifier',
            source=location
        )
    ]
    assert tokenize('_one __two __multiple_underscores') == tokens


def test_positive_integers() -> None:
    tokens = [
        Token(
            text='1',
            type='integer',
            source=location
        ),
        Token(
            text='23',
            type='integer',
            source=location
        ),
        Token(
            text='95',  # do not accept '-' as part of integer
            type='integer',
            source=location
        )
    ]
    assert tokenize('1 23 -95') == tokens


def test_empty_returns_nothing() -> None:
    assert tokenize('') == []
