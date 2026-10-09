#!/usr/bin/env python3
"""
Thread-safe terminal progress bar used by the batch formatter.

The bar runs its own daemon thread so long formatting passes can report
progress without blocking the worker thread that processes the files.
"""

import contextlib
import io
import sys
import threading

from shared.progress_render import (
    DEFAULT_WIDTH,
    SPINNER_FRAMES,
    ProgressRenderer,
)


class ProgressBar:
    def __init__(self, total: int, width: int = DEFAULT_WIDTH, interval_sec: float = 1.0) -> None:
        self.total = max(total, 1)
        self.width = width
        self.interval_sec = interval_sec
        self.done = 0
        self.tick = 0
        self.current_file = ""
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.active = False
        self.renderer = ProgressRenderer(sys.stdout)

    def _snapshot(self) -> tuple[int, int, str]:
        with self.lock:
            return self.done, self.tick, self.current_file

    def build_line(self) -> str:
        done, tick, current_file = self._snapshot()
        ratio = min(done / self.total, 1.0)
        filled = int(ratio * self.width)
        bar = "#" * filled + "-" * (self.width - filled)
        percent = ratio * 100.0
        spinner = SPINNER_FRAMES[tick % 4]
        return f"[{bar}] {done}/{self.total} ({percent:5.1f}%) {spinner} {current_file}"

    def start(self) -> None:
        with self.lock:
            self.active = True
        self.renderer = ProgressRenderer(sys.stdout)
        self.render()
        self.thread.start()

    def set_file(self, filename: str) -> None:
        with self.lock:
            self.tick = 0
            self.current_file = filename
        self.render()

    def advance(self) -> None:
        with self.lock:
            self.done += 1
            self.tick = 0
        self.render()

    def run(self) -> None:
        while not self.stop_event.wait(self.interval_sec):
            with self.lock:
                self.tick += 1
            self.render()

    def render(self) -> None:
        with self.lock:
            if not self.active:
                return
            done = self.done
        self.renderer.render(self.build_line(), done)

    def clear(self) -> None:
        with self.lock:
            if not self.active:
                return
        self.renderer.clear()

    def run_with_captured_output(self, func, *args, **kwargs):
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            result = func(*args, **kwargs)
        output = buffer.getvalue()
        with self.lock:
            inactive = not self.active
        if inactive:
            self.renderer.emit(output)
            return result
        self.renderer.clear()
        self.renderer.emit(output)
        self.render()
        return result

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=2.0)
        with self.lock:
            if not self.active:
                return
            self.active = False
            done = self.done
        self.renderer.finalize(self.build_line(), done)
