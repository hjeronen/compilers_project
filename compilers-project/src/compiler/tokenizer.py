import re
from dataclasses import dataclass
from typing import Literal, Match
import math


TokenType = Literal['integer', 'operator', 'punctuation', 'identifier', 'end']


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

    whitespace = r'\s+'
    newline = r'\n+'
    # keyword = r'if|elif|else|while|not'
    identifier = r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    integer = r'[0-9]+'
    operator = r'\+|\-|\*|/|\=\=|\!\=|\<\=|\>\=|\=|\<|\>'
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

        # match = match_re(keyword, source_code, pos)
        # if match is not None:
        #     result.append(source_code[pos:match.end()])
        #     pos = match.end()
        #     continue

        match = match_re(identifier, source_code, pos)
        if match is not None:
            result.append(Token(
                type='identifier',
                text=source_code[pos:match.end()],
                location=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        match = match_re(integer, source_code, pos)
        if match is not None:
            result.append(Token(
                type='integer',
                text=source_code[pos:match.end()],
                location=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        match = match_re(operator, source_code, pos)
        if match is not None:
            result.append(Token(
                type='operator',
                text=source_code[pos:match.end()],
                location=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        match = match_re(punctuation, source_code, pos)
        if match is not None:
            result.append(Token(
                type='punctuation',
                text=source_code[pos:match.end()],
                location=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        pos += 1

    return result
