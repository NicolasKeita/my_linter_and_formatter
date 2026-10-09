#!/usr/bin/env python3
"""
Comment detection and handling utilities for the C++ code formatter.

Provides functions for detecting, removing, and restoring comments in C++ code.
"""

from shared.comment_utils.detection import detect_comments_and_functions
from shared.comment_utils.placement import check_comment_placement
from shared.comment_utils.scanning import (
    COMMENT_PLACEHOLDER,
    remove_comments,
    restore_comments,
    scan_string_and_comment_ranges,
)

__all__ = [
    "COMMENT_PLACEHOLDER",
    "check_comment_placement",
    "detect_comments_and_functions",
    "remove_comments",
    "restore_comments",
    "scan_string_and_comment_ranges",
]
