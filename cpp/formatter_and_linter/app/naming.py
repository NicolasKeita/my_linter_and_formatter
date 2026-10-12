#!/usr/bin/env python3
"""PascalCase conversion and recursive file renaming helpers."""

import os


def to_pascal_case(name: str) -> str:
    if name == "main":
        return name

    if any(c.isupper() for c in name[1:]):
        result = ""
        capitalize_next = False
        for char in name:
            if char == '_':
                capitalize_next = True
            else:
                if capitalize_next:
                    result += char.upper()
                    capitalize_next = False
                else:
                    result += char
        return result

    parts = name.split('_')
    pascal_parts = [part.capitalize() for part in parts]
    return ''.join(pascal_parts)


def rename_files_to_pascal_case(directory: str) -> None:
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.cpp', '.hpp', '.h')):
                name, ext = os.path.splitext(file)
                if name != "main":
                    pascal_name = to_pascal_case(name)
                    if name != pascal_name:
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(root, pascal_name + ext)
                        os.rename(old_path, new_path)
                        print(f"Renamed: {file} -> {pascal_name + ext}")
