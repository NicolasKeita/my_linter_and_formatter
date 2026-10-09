#!/usr/bin/env python3
"""
Single-pass scanners for one C++ literal or comment.

Each helper takes the source and the index of the opening character and returns
the half-open ``(start, end)`` range it covers, or ``None`` when the candidate
does not actually open a literal (an unterminated string, an invalid raw-string
delimiter, ...).
"""


def _prefix_after_char_prefix(code: str, r_index: int) -> int:
    before_r = r_index - 1
    before_prefix = before_r - 1
    if before_prefix >= 0 and (code[before_prefix].isalnum() or code[before_prefix] == "_"):
        return -1
    return before_r


def _u8_prefix_start(code: str, r_index: int) -> int:
    before_r = r_index - 1
    if before_r - 1 < 0 or code[before_r - 1] != "u":
        return -1
    return _prefix_after_char_prefix(code, before_r)


def raw_string_prefix_start(code: str, quote_index: int) -> int:
    """Return the start of the raw-string prefix before ``quote_index``, or -1."""
    if quote_index <= 0 or code[quote_index - 1] != "R":
        return -1
    r_index = quote_index - 1
    before_r = r_index - 1
    if before_r < 0:
        return r_index
    previous = code[before_r]
    if previous in ("u", "U", "L"):
        return _prefix_after_char_prefix(code, r_index)
    if previous == "8":
        return _u8_prefix_start(code, r_index)
    if previous.isalnum() or previous == "_":
        return -1
    return r_index


def scan_line_comment(code: str, index: int, length: int) -> tuple[int, int]:
    end = code.find("\n", index)
    if end == -1:
        end = length
    return index, end


def scan_block_comment(code: str, index: int, length: int) -> tuple[int, int]:
    end = code.find("*/", index + 2)
    if end == -1:
        end = length
    else:
        end += 2
    return index, end


def scan_raw_string(code: str, index: int, prefix_start: int) -> tuple[int, int] | None:
    delimiter_end = code.find("(", index + 1, index + 17)
    if delimiter_end == -1:
        return None
    delimiter = code[index + 1 : delimiter_end]
    if any(item in " \\()" for item in delimiter):
        return None
    terminator = ")" + delimiter + '"'
    term_index = code.find(terminator, delimiter_end + 1)
    if term_index == -1:
        return None
    return prefix_start, term_index + len(terminator)


def scan_string_literal(code: str, index: int, length: int) -> tuple[int, int] | None:
    closing = index + 1
    while closing < length and code[closing] != "\n":
        if code[closing] == "\\":
            closing += 2
            continue
        if code[closing] == '"':
            return index, closing + 1
        closing += 1
    return None


def scan_char_literal(code: str, index: int, length: int) -> tuple[int, int] | None:
    closing = index + 1
    if closing < length and code[closing] == "\\":
        closing += 2
    else:
        closing += 1
    if closing < length and code[closing] == "'" and "\n" not in code[index : closing + 1]:
        return index, closing + 1
    return None
