import re
from typing import Match


def match_re(regex: str, input: str, position: int) -> Match | None:
    r = re.compile(regex)
    return r.match(input, position)


def tokenize(source_code: str) -> list[str]:
    pos = 0
    result: list[str] = []

    whitespace_or_newline = r'\s+|\n'
    keyword = r'if|elif|else|while|not'
    variable = r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    integer = r'[0-9]+'

    while pos < len(source_code):

        match = match_re(whitespace_or_newline, source_code, pos)
        if match is not None:
            pos = match.end()
            continue

        match = match_re(keyword, source_code, pos)
        if match is not None:
            result.append(source_code[pos:match.end()])
            pos = match.end()
            continue

        match = match_re(variable, source_code, pos)
        if match is not None:
            result.append(source_code[pos:match.end()])
            pos = match.end()
            continue

        match = match_re(integer, source_code, pos)
        if match is not None:
            result.append(source_code[pos:match.end()])
            pos = match.end()
            continue

        pos += 1

    return result
