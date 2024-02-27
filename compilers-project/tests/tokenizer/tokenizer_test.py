from compiler.tokenizer import tokenize, Location, AnyLocation, Token


filename = 'test'

location = AnyLocation(
    file=filename,
    line=0,
    column=0
)


def test_tokenizer_basics() -> None:
    tokens = [
        Token(
            text='if',
            type='keyword',
            location=location
        ),
        Token(
            text='3',
            type='integer',
            location=location
        ),
        Token(
            text='while',
            type='keyword',
            location=location
        )
    ]
    assert tokenize(filename, 'if  3\nwhile') == tokens


def test_keywords() -> None:
    tokens = [
        Token(
            text='if',
            type='keyword',
            location=location
        ),
        Token(
            text='then',
            type='keyword',
            location=location
        ),
        Token(
            text='elif',
            type='keyword',
            location=location
        ),
        Token(
            text='else',
            type='keyword',
            location=location
        ),
        Token(
            text='while',
            type='keyword',
            location=location
        ),
        Token(
            text='var',
            type='keyword',
            location=location
        )
    ]
    assert tokenize(filename, 'if then elif else while var') == tokens


def test_others() -> None:
    tokens = [
        Token(
            text='true',
            type='bool_literal',
            location=location
        ),
        Token(
            text='null',
            type='null_literal',
            location=location
        )
    ]
    assert tokenize(filename, 'true null') == tokens


def test_variable_names() -> None:
    tokens = [
        Token(
            text='thisIsValid',
            type='identifier',
            location=location
        ),
        Token(
            text='python_style',
            type='identifier',
            location=location
        ),
        Token(
            text='variable1',
            type='identifier',
            location=location
        )
    ]
    assert tokenize(filename, 'thisIsValid python_style variable1') == tokens


def test_underscored_variables() -> None:
    tokens = [
        Token(
            text='_one',
            type='identifier',
            location=location
        ),
        Token(
            text='__two',
            type='identifier',
            location=location
        ),
        Token(
            text='__multiple_underscores',
            type='identifier',
            location=location
        )
    ]
    assert tokenize(filename, '_one __two __multiple_underscores') == tokens


def test_positive_integers() -> None:
    tokens = [
        Token(
            text='1',
            type='integer',
            location=location
        ),
        Token(
            text='23',
            type='integer',
            location=location
        ),
        Token(
            text='-',
            type='operator',
            location=location
        ),
        Token(
            text='95',  # do not accept '-' as part of integer
            type='integer',
            location=location
        )
    ]
    assert tokenize(filename, '1 23 -95') == tokens


def test_operators() -> None:
    tokens = [
        Token(
            text='<',
            type='comp_operator',
            location=location
        ),
        Token(
            text='<=',
            type='comp_operator',
            location=location
        ),
        Token(
            text='>',
            type='comp_operator',
            location=location
        ),
        Token(
            text='!=',
            type='comp_operator',
            location=location
        ),
        Token(
            text='/',
            type='operator',
            location=location
        ),
        Token(
            text='+',
            type='operator',
            location=location
        ),
        Token(
            text='*',
            type='operator',
            location=location
        ),
        Token(
            text='=',
            type='assignment',
            location=location
        )
    ]
    assert tokenize(filename, '< <= > != / + * =') == tokens


def test_remainder() -> None:
    tokens = [
        Token(
            text='4',
            type='integer',
            location=location
        ),
        Token(
            text='%',
            type='operator',
            location=location
        ),
        Token(
            text='2',
            type='integer',
            location=location
        )
    ]
    assert tokenize(filename, '4 % 2') == tokens


def test_punctuation() -> None:
    tokens = [
        Token(
            text='(',
            type='punctuation',
            location=location
        ),
        Token(
            text=')',
            type='punctuation',
            location=location
        ),
        Token(
            text=',',
            type='punctuation',
            location=location
        ),
        Token(
            text=';',
            type='punctuation',
            location=location
        )
    ]
    assert tokenize(filename, '() , ;') == tokens


def test_comment_oneline_java() -> None:
    tokens = [
        Token(
            text='if',
            type='keyword',
            location=location
        ),
        Token(
            text='(',
            type='punctuation',
            location=location
        ),
        Token(
            text='true',
            type='bool_literal',
            location=location
        ),
        Token(
            text=')',
            type='punctuation',
            location=location
        ),
        Token(
            text='{',
            type='punctuation',
            location=location
        ),
        Token(
            text='return',
            type='keyword',
            location=location
        ),
        Token(
            text='a',
            type='identifier',
            location=location
        ),
        Token(
            text='}',
            type='punctuation',
            location=location
        )
    ]

    code = 'if (true) {\n// comment ignored!\nreturn a\n}'

    assert tokenize(filename, code) == tokens


def test_comment_oneline_python() -> None:
    tokens = [
        Token(
            text='if',
            type='keyword',
            location=location
        ),
        Token(
            text='true',
            type='bool_literal',
            location=location
        ),
        Token(
            text=':',
            type='punctuation',
            location=location
        ),
        Token(
            text='return',
            type='keyword',
            location=location
        ),
        Token(
            text='a',
            type='identifier',
            location=location
        )
    ]

    code = 'if true:\n# comment ignored!\nreturn a\n'

    assert tokenize(filename, code) == tokens


def test_comment_multiline() -> None:
    tokens = [
        Token(
            text='print_int',
            type='identifier',
            location=location
        ),
        Token(
            text='(',
            type='punctuation',
            location=location
        ),
        Token(
            text='123',
            type='integer',
            location=location
        ),
        Token(
            text=')',
            type='punctuation',
            location=location
        )
    ]

    code = '/*\nMany lines\nof comment\ntext.\n*/\nprint_int(123)\n/* Another\ncomment. */'

    assert tokenize(filename, code) == tokens


def test_locations_are_equal() -> None:
    one = Location(
        file=filename,
        line=2,
        column=3
    )
    two = AnyLocation(
        file=filename,
        line=0,
        column=0
    )
    assert one == two


def test_empty_returns_nothing() -> None:
    assert tokenize(filename, '') == []
