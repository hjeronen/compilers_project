import re
from dataclasses import dataclass
from typing import Literal, Match
import math


TokenType = Literal['integer', 'operator', 'comp_operator', 'assignment', 'bool_literal', 'bool_operator',
                    'null_literal', 'unary_op', 'punctuation', 'identifier', 'keyword', 'end']


@dataclass
class Location:
    file: str
    line: int
    column: int


@dataclass
class AnyLocation(Location):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location)


@dataclass
class Token:
    text: str
    type: TokenType
    location: Location


def match_re(regex: str, input: str, position: int) -> Match | None:
    r = re.compile(regex)
    return r.match(input, position)


def get_location(file: str, line: int, pos: int) -> Location:
    return Location(
        file=file,
        line=line,
        column=math.floor(pos/line)
    )


def tokenize(input_file: str, source_code: str) -> list[Token]:
    pos = 0
    line = 1
    result: list[Token] = []

    def check_regex(regex: str, type: TokenType, source_code: str, input_file: str, line: int, result: list[Token]) -> bool:
        nonlocal pos
        match = match_re(regex, source_code, pos)
        if match is not None:
            result.append(Token(
                type=type,
                text=source_code[pos:match.end()],
                location=get_location(input_file, line, pos)
            ))
            pos = match.end()
            return True

        return False

    whitespace = r'\s+'
    newline = r'\n+'
    keyword = r'\b(if|then|elif|else|while|return|var)\b'
    bool_literal = r'\b(true|false)\b'
    bool_operator = r'\b(and|or)\b'
    null_literal = r'\bnull\b'
    unary_op = r'\bnot\b'
    identifier = r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    integer = r'[0-9]+'
    operator = r'\+|\-|\*|\/|\%'
    comp_operator = r'\=\=|\!\=|\<\=|\>\=|\<|\>'
    assignment = r'\='
    punctuation = r'\(|\)|\[|\]|\{|\}|\,|\:|\;'
    comment_oneline = r'(#+|//+).*\n+'
    comment_multiline = r'/\*[^*/]*\*/'

    while pos < len(source_code):

        match = match_re(whitespace, source_code, pos)
        if match is not None:
            pos = match.end()
            continue

        match = match_re(newline, source_code, pos)
        if match is not None:
            pos = match.end()
            line += 1
            continue

        match = match_re(comment_oneline, source_code, pos)
        if match is not None:
            pos = match.end()
            continue

        match = match_re(comment_multiline, source_code, pos)
        if match is not None:
            pos = match.end()
            continue

        if check_regex(keyword, 'keyword', source_code,
                       input_file, line, result):
            continue

        if check_regex(bool_literal, 'bool_literal', source_code,
                       input_file, line, result):
            continue

        if check_regex(bool_operator, 'bool_operator', source_code,
                       input_file, line, result):
            continue

        if check_regex(null_literal, 'null_literal', source_code,
                       input_file, line, result):
            continue

        if check_regex(unary_op, 'unary_op', source_code,
                       input_file, line, result):
            continue

        if check_regex(identifier, 'identifier', source_code,
                       input_file, line, result):
            continue

        if check_regex(integer, 'integer', source_code,
                       input_file, line, result):
            continue

        if check_regex(operator, 'operator', source_code,
                       input_file, line, result):
            continue

        if check_regex(comp_operator, 'comp_operator', source_code,
                       input_file, line, result):
            continue

        if check_regex(assignment, 'assignment', source_code,
                       input_file, line, result):
            continue

        if check_regex(punctuation, 'punctuation', source_code,
                       input_file, line, result):
            continue

        pos += 1

    return result
