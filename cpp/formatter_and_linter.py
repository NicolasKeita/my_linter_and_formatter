#!/usr/bin/env python3
"""
C++ Code Formatter & Linter

Entry point for the formatter_and_linter package.
"""

import os
import sys
from typing import NoReturn

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatter_and_linter")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PACKAGE_DIR)


def _load_modules():
    import formatter.braces.brace_formatter
    import formatter.spacing.comment_function_formatter
    import formatter.declarations.declaration_blank_line_formatter
    import formatter.declarations.designated_init_split_formatter
    import formatter.file_handler
    import formatter.params.function_formatter
    import formatter.spacing.include_formatter
    import formatter.declarations.initialization_block_formatter
    import formatter.declarations.local_variable_alignment_formatter
    import formatter.declarations.member_alignment_formatter
    import formatter.module.module_formatter
    import formatter.spacing.prototype_spacing
    import formatter.braces.short_if_formatter
    import linter.linter
    import shared.comment_utils
    from formatter.join_lines import join_lines as join_lines_fn
    from shared.progress_bar import ProgressBar

    return {
        "brace_formatter": formatter.braces.brace_formatter,
        "comment_function_formatter": formatter.spacing.comment_function_formatter,
        "declaration_blank_line_formatter": formatter.declarations.declaration_blank_line_formatter,
        "designated_init_split_formatter": formatter.declarations.designated_init_split_formatter,
        "file_handler": formatter.file_handler,
        "function_formatter": formatter.params.function_formatter,
        "include_formatter": formatter.spacing.include_formatter,
        "initialization_block_formatter": formatter.declarations.initialization_block_formatter,
        "local_variable_alignment_formatter": formatter.declarations.local_variable_alignment_formatter,
        "member_alignment_formatter": formatter.declarations.member_alignment_formatter,
        "module_formatter": formatter.module.module_formatter,
        "prototype_spacing": formatter.spacing.prototype_spacing,
        "short_if_formatter": formatter.braces.short_if_formatter,
        "linter": linter.linter,
        "comment_utils": shared.comment_utils,
        "join_lines": join_lines_fn,
        "ProgressBar": ProgressBar,
    }


_MODULES = _load_modules()
brace_formatter = _MODULES["brace_formatter"]
comment_function_formatter = _MODULES["comment_function_formatter"]
declaration_blank_line_formatter = _MODULES["declaration_blank_line_formatter"]
designated_init_split_formatter = _MODULES["designated_init_split_formatter"]
file_handler = _MODULES["file_handler"]
function_formatter = _MODULES["function_formatter"]
include_formatter = _MODULES["include_formatter"]
initialization_block_formatter = _MODULES["initialization_block_formatter"]
local_variable_alignment_formatter = _MODULES["local_variable_alignment_formatter"]
member_alignment_formatter = _MODULES["member_alignment_formatter"]
module_formatter = _MODULES["module_formatter"]
prototype_spacing = _MODULES["prototype_spacing"]
short_if_formatter = _MODULES["short_if_formatter"]
linter = _MODULES["linter"]
comment_utils = _MODULES["comment_utils"]
join_lines = _MODULES["join_lines"]
ProgressBar = _MODULES["ProgressBar"]


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


def _format_module_interface(code: str, input_file: str) -> str:
    formatted_code = prototype_spacing.clean_code(code)
    return member_alignment_formatter.format_member_alignment_for_file(input_file, formatted_code)


def _format_regular_source(code: str) -> str:
    code_without_comments, comments = comment_utils.remove_comments(code)

    formatted_code = include_formatter.format_includes(code_without_comments)

    formatted_code = function_formatter.format_function_params(formatted_code)

    formatted_code = comment_utils.restore_comments(formatted_code, comments)

    formatted_code = comment_function_formatter.format_comment_function_spacing(formatted_code)

    formatted_code = short_if_formatter.format_if_statements(formatted_code)

    formatted_code = brace_formatter.format_control_structure_braces(formatted_code)

    formatted_code = brace_formatter.format_function_braces(formatted_code)

    formatted_code = declaration_blank_line_formatter.remove_blank_lines_between_declarations(formatted_code)

    formatted_code = initialization_block_formatter.format_initialization_blocks(formatted_code)

    formatted_code = module_formatter.reorder_using_after_prototypes(formatted_code)

    formatted_code = module_formatter.reorder_using_after_import(formatted_code)

    formatted_code = module_formatter.format_import_order(formatted_code)

    formatted_code = module_formatter.format_module_import_spacing(formatted_code)

    return prototype_spacing.clean_code(formatted_code)


def _apply_common_passes(formatted_code: str, is_module_interface: bool) -> str:
    formatted_code = join_lines(formatted_code)

    if not is_module_interface:
        formatted_code = local_variable_alignment_formatter.align_first_declaration_blocks(formatted_code)

    return designated_init_split_formatter.split_long_designated_initializations(formatted_code)


def format_file(input_file: str, in_place: bool, check_only: bool) -> bool:
    code = file_handler.read_input_file(input_file)

    is_module_interface = input_file.lower().endswith('.cppm')
    if is_module_interface:
        formatted_code = _format_module_interface(code, input_file)
    else:
        formatted_code = _format_regular_source(code)

    formatted_code = _apply_common_passes(formatted_code, is_module_interface)

    has_long_lines = linter.lint_code(formatted_code, file_path=input_file)

    if check_only:
        return has_long_lines

    output_file = input_file if in_place else "output.cpp"
    file_handler.write_output_file(output_file, formatted_code)

    return has_long_lines


def check_directory_structure() -> bool:
    directory_violations = linter.check_directory_file_counts(
        ["Src", "Tests", "apps"],
        max_files=linter.MAX_FILES_PER_DIRECTORY,
    )
    linter.print_directory_file_count_warnings(
        directory_violations,
        linter.MAX_FILES_PER_DIRECTORY,
    )

    module_filename_violations = linter.check_module_filename_convention(["Src", "Tests", "apps"])
    linter.print_module_filename_warnings(module_filename_violations)

    module_size_violations = linter.check_module_implementation_counts(["Src", "Tests", "apps"])
    linter.print_module_size_warnings(module_size_violations)

    cmake_length_violations = linter.check_cmake_file_lengths(["Src", "Tests", "apps"])
    linter.print_cmake_length_warnings(
        cmake_length_violations,
        linter.MAX_CMAKELISTS_LINES,
    )

    return (
        len(directory_violations) > 0
        or len(module_filename_violations) > 0
        or len(module_size_violations) > 0
        or len(cmake_length_violations) > 0
    )


_SEARCH_DIRECTORIES = ("Src", "Tests", "apps")


def _print_usage() -> None:
    print(
        "Usage: python formatter_and_linter.py [-i] [-r/--recursive] <input_file.cpp> ...",
        file=sys.stderr,
    )
    print("       python formatter_and_linter.py --check", file=sys.stderr)
    print("  -i, --in-place    : Modify the file in place (otherwise create output.cpp)", file=sys.stderr)
    print(
        "  -r, --recursive   : Process all .cpp/.cppm files "
        "in Src/, Tests/ and apps/ recursively",
        file=sys.stderr,
    )
    print(
        "  --check           : Check all files in Src/, Tests/ and apps/ "
        "and CMakeLists.txt without modifying",
        file=sys.stderr,
    )


def _collect_search_directories() -> list[str]:
    input_files: list[str] = []
    for directory in _SEARCH_DIRECTORIES:
        input_files += file_handler.find_source_files(directory, include_hpp=False, include_cppm=True)
    return input_files


def _resolve_input_files(
    check_only: bool,
    recursive: bool,
    input_files: list[str],
) -> list[str]:
    if check_only or recursive:
        input_files = _collect_search_directories()
        if not input_files:
            print("No source files found in Src/, Tests/ or apps/", file=sys.stderr)
            sys.exit(1)
        action = "Checking" if check_only else "Found"
        print(f"{action} {len(input_files)} files in Src/, Tests/ and apps/...")
    elif not input_files:
        _print_usage()
        sys.exit(1)
    return input_files


def _process_files(input_files: list[str], in_place: bool, check_only: bool) -> bool:
    has_any_long_lines = False
    progress = ProgressBar(total=len(input_files), interval_sec=1.0)
    progress.start()
    try:
        for input_file in input_files:
            progress.set_file(input_file)
            has_long_lines = progress.run_with_captured_output(
                format_file, input_file, in_place, check_only
            )
            progress.advance()
            if has_long_lines:
                has_any_long_lines = True
    finally:
        progress.stop()
    return has_any_long_lines


def main() -> NoReturn:
    in_place, check_only, recursive, input_files = file_handler.parse_arguments()
    input_files = _resolve_input_files(check_only, recursive, input_files)

    has_directory_violations = check_directory_structure() if (check_only or recursive) else False

    if not check_only and not recursive:
        print("Renaming files to PascalCase...")
        rename_files_to_pascal_case("Src")

    has_any_long_lines = _process_files(input_files, in_place, check_only)

    if has_any_long_lines or has_directory_violations:
        print("[FAIL] Style issues detected!")
    else:
        print("[PASS] All files pass style checks!")

    exit_code = 1 if (has_any_long_lines or has_directory_violations) else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()