#!/usr/bin/env python3
"""
C++ Code Formatter & Linter

Entry point for the formatter_and_linter package. This thin wrapper sets up
the import path so the ``formatter``, ``linter``, ``shared`` and ``app``
subpackages resolve as top-level packages, then delegates to the application
layer in ``app.cli``.
"""

import os
import sys

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatter_and_linter")
for _path in (os.path.dirname(os.path.abspath(__file__)), PACKAGE_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)


def main() -> None:
    from app.cli import main as run_cli

    run_cli()


if __name__ == "__main__":
    main()
