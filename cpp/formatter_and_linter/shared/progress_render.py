#!/usr/bin/env python3
"""
Terminal rendering helpers for the batch progress bar.

Rendering is isolated from the progress bookkeeping so both halves stay small
and independently testable.
"""

import shutil
import sys

DEFAULT_WIDTH = 30
SPINNER_FRAMES = "|/-\\"
_FALLBACK_COLUMNS = 120


def terminal_columns() -> int:
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return _FALLBACK_COLUMNS


def is_tty_stream(stream) -> bool:
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def emit_output(output: str, stream) -> None:
    if not output:
        return
    sys.stderr.write(output)
    if not output.endswith("\n"):
        sys.stderr.write("\n")
    sys.stderr.flush()


def render_tty(stream, line: str, previous_length: int) -> int:
    """Draw ``line`` in place and return the new rendered length."""
    columns = terminal_columns()
    if columns > 1:
        line = line[: columns - 1]
    padding = " " * max(0, previous_length - len(line))
    stream.write("\r" + line + padding + "\x1b[K")
    stream.flush()
    return len(line)


def render_tty_final(stream, line: str, previous_length: int) -> None:
    """Draw the last ``line`` and move the cursor to the next row."""
    columns = terminal_columns()
    if columns > 1:
        line = line[: columns - 1]
    padding = " " * max(0, previous_length - len(line))
    stream.write("\r" + line + padding + "\n")
    stream.flush()


def clear_tty(stream, previous_length: int) -> None:
    stream.write("\r" + " " * previous_length + "\r")
    stream.flush()


class ProgressRenderer:
    """Owns every side effect on the terminal stream.

    The renderer keeps the in-place redraw state (previous line length and the
    last progress value echoed on non-interactive streams) so the progress bar
    itself only tracks counters.
    """

    def __init__(self, stream) -> None:
        self._stream = stream
        self._prev_len = 0
        self._last_logged_done = -1

    def is_tty(self) -> bool:
        return is_tty_stream(self._stream)

    def render(self, line: str, done: int) -> None:
        if not self.is_tty():
            self._render_plain(line, done)
            return
        self._prev_len = render_tty(self._stream, line, self._prev_len)

    def _render_plain(self, line: str, done: int) -> None:
        if done == self._last_logged_done:
            return
        self._stream.write(line + "\n")
        self._stream.flush()
        self._last_logged_done = done

    def clear(self) -> None:
        if not self.is_tty():
            return
        clear_tty(self._stream, self._prev_len)
        self._prev_len = 0

    def finalize(self, line: str, done: int) -> None:
        if self.is_tty():
            render_tty_final(self._stream, line, self._prev_len)
            self._prev_len = 0
            return
        self._render_plain(line, done)

    def emit(self, output: str) -> None:
        emit_output(output, self._stream)
