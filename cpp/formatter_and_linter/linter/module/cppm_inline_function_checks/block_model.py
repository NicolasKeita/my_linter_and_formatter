#!/usr/bin/env python3
"""Block model and state enums for the cppm inline function scanner."""

from enum import Enum, auto
from typing import NamedTuple


class _SanitizeState(Enum):
    CODE = auto()
    LINE_COMMENT = auto()
    BLOCK_COMMENT = auto()
    STRING = auto()
    CHAR = auto()
    RAW_STRING = auto()


class _BlockKind(Enum):
    NAMESPACE = auto()
    TYPE = auto()
    FUNCTION = auto()
    OTHER = auto()


class _Block(NamedTuple):
    kind: _BlockKind
    name: str
    open_pos: int
    start_pos: int
    transparent: bool
