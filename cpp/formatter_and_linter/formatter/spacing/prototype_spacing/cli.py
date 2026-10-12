#!/usr/bin/env python3
"""Standalone command-line entry point for the prototype spacing cleaner."""

import sys

from formatter.spacing.prototype_spacing.cleaner import clean_code


def main() -> None:
    arguments = sys.argv[1:]
    in_place = "-i" in arguments
    file_paths = [argument for argument in arguments if argument != "-i"]

    if not file_paths:
        print("Usage: python prototype_spacing.py [-i] <file.cpp|file.cppm> ...", file=sys.stderr)
        print("  -i, --in-place : Modify the files in place (otherwise print to stdout)", file=sys.stderr)
        sys.exit(1)

    for file_path in file_paths:
        with open(file_path, encoding="utf-8") as handle:
            content = handle.read()

        cleaned = clean_code(content)

        if in_place:
            with open(file_path, "w", encoding="utf-8", newline="") as handle:
                handle.write(cleaned)
                if not cleaned.endswith("\n"):
                    handle.write("\n")
        else:
            print(cleaned)


if __name__ == "__main__":
    main()
