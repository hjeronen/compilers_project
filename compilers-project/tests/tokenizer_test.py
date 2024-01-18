from compiler.tokenizer import tokenize


def test_tokenizer_basics() -> None:
    assert tokenize('if  3\nwhile') == ['if', '3', 'while']


def test_keywords() -> None:
    assert tokenize('if elif else while not') == [
        'if', 'elif', 'else', 'while', 'not']


def test_variable_names() -> None:
    assert tokenize('thisIsValid python_style variable1') == [
        'thisIsValid', 'python_style', 'variable1']


def test_underscored_variables() -> None:
    assert tokenize('_one __two __multiple_underscores') == [
        '_one', '__two', '__multiple_underscores']


def test_positive_integers() -> None:
    assert tokenize('1 23 -95') == ['1', '23', '95']


def test_empty_returns_nothing() -> None:
    assert tokenize('') == []
