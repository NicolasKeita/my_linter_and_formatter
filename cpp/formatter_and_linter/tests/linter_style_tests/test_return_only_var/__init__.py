"""
Return-Only Variable Tests

Unit tests (pytest style) for the declaration-then-immediate-return check:
a local variable declared/initialized and then returned via 'return var;' as
its first following executable statement (blank lines and comments ignored)
is reported. Any interleaved executable instruction, a return of a modified
expression, or a return of a different identifier cancels the detection.
"""
