import re
from dataclasses import dataclass
from typing import Literal, Match
import math


TokenType = Literal['integer', 'operator', 'punctuation', 'identifier']


@dataclass
class Location:
    file: str
    line: int
    column: int


@dataclass
class Token:
    text: str
    type: TokenType
    source: Location


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
                source=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        match = match_re(integer, source_code, pos)
        if match is not None:
            result.append(Token(
                type='integer',
                text=source_code[pos:match.end()],
                source=get_location(input_file, line, pos)
            ))
            pos = match.end()
            continue

        pos += 1

    return result
