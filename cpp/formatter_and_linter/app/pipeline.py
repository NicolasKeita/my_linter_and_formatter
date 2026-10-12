#!/usr/bin/env python3
"""The multi-pass formatting pipeline applied to each source file."""

from app.registry import (
    brace_formatter,
    comment_function_formatter,
    comment_utils,
    declaration_blank_line_formatter,
    designated_init_split_formatter,
    file_handler,
    function_formatter,
    include_formatter,
    initialization_block_formatter,
    join_lines,
    linter,
    local_variable_alignment_formatter,
    member_alignment_formatter,
    module_formatter,
    prototype_spacing,
    short_if_formatter,
)


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
