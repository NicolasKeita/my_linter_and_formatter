"""
C++20 Designated Initializer Tests

Unit tests (pytest style) for the empty-brace declaration check: a variable
declared with an empty-brace value initialization whose first following
executable statement (blank lines and comments ignored) assigns one of its
members is reported with a C++20 designated initializer suggestion. Consecutive
assignments on the same variable are grouped into a single suggestion.
"""
