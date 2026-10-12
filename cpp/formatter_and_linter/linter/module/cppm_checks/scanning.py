#!/usr/bin/env python3
"""Line-depth and body-line helpers for .cppm interface checks."""


def build_line_depths(lines: list[str]) -> list[int]:
    depths = []
    current_depth = 0
    for line in lines:
        depths.append(current_depth)
        current_depth += line.count('{')
        current_depth -= line.count('}')
        if current_depth < 0:
            current_depth = 0
    return depths


def count_significant_body_lines(lines: list[str], open_line: int, end_line: int) -> int:
    significant_lines = 0
    for line_idx in range(open_line, end_line + 1):
        body_line = _trim_body_line(lines[line_idx], line_idx, open_line, end_line)

        stripped = body_line.strip()
        if not stripped:
            continue
        if stripped in {'{', '}'}:
            continue
        significant_lines += 1

    return significant_lines


def _trim_body_line(body_line: str, line_idx: int, open_line: int, end_line: int) -> str:
    if line_idx == open_line:
        opening_pos = body_line.find('{')
        if opening_pos >= 0:
            body_line = body_line[opening_pos + 1:]
    if line_idx == end_line:
        closing_pos = body_line.rfind('}')
        if closing_pos >= 0:
            body_line = body_line[:closing_pos]
    return body_line
