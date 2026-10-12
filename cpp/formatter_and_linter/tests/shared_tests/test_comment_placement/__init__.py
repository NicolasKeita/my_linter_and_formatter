"""
Comment Placement Check Tests

Unit tests for the comment placement rule: a comment block (single-line,
contiguous multi-line `//`, or `/* */`) is valid only when it sits directly
above a function definition or a top-level declaration.

Run with:
    python -m unittest discover -s formatter_and_linter/tests -v
"""
