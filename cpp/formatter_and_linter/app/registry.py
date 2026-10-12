#!/usr/bin/env python3
"""Lazy loading and binding of the formatter / linter submodules."""


def load_modules():
    import formatter.braces.brace_formatter
    import formatter.braces.short_if_formatter
    import formatter.declarations.declaration_blank_line_formatter
    import formatter.declarations.designated_init_split_formatter
    import formatter.declarations.initialization_block_formatter
    import formatter.declarations.local_variable_alignment_formatter
    import formatter.declarations.member_alignment_formatter
    import formatter.file_handler
    import formatter.module.module_formatter
    import formatter.params.function_formatter
    import formatter.spacing.comment_function_formatter
    import formatter.spacing.includes.include_formatter
    import formatter.spacing.prototype_spacing
    import linter.core.linter
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
        "include_formatter": formatter.spacing.includes.include_formatter,
        "initialization_block_formatter": formatter.declarations.initialization_block_formatter,
        "local_variable_alignment_formatter": formatter.declarations.local_variable_alignment_formatter,
        "member_alignment_formatter": formatter.declarations.member_alignment_formatter,
        "module_formatter": formatter.module.module_formatter,
        "prototype_spacing": formatter.spacing.prototype_spacing,
        "short_if_formatter": formatter.braces.short_if_formatter,
        "linter": linter.core.linter,
        "comment_utils": shared.comment_utils,
        "join_lines": join_lines_fn,
        "ProgressBar": ProgressBar,
    }


_MODULES = load_modules()
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
