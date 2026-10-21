"""Run Ruff in batches, optionally collecting its output for a check summary."""

import os
import re
import subprocess
import sys
from pathlib import Path

RUFF_CONFIG = Path(__file__).with_name("ruff.toml")
_FORMAT_COUNT = re.compile(r"(\d+) files? (would be reformatted|already formatted|reformatted|left unchanged)")


def _summarize_format_output(output: str) -> str:
    counts = dict.fromkeys(("would be reformatted", "reformatted", "already formatted", "left unchanged"), 0)
    details: list[str] = []
    for line in output.splitlines(keepends=True):
        matches = [_FORMAT_COUNT.fullmatch(part) for part in line.rstrip("\r\n").split(", ")]
        if not all(matches):
            details.append(line)
            continue
        for match in matches:
            if match is not None:
                counts[match[2]] += int(match[1])
    summary = ", ".join(
        f"{count} {'file' if count == 1 else 'files'} {state}" for state, count in counts.items() if count
    )
    if summary:
        details.append(summary + "\n")
    return "".join(details)


def run_ruff(command: str, files: list[Path], *options: str, output: list[str] | None = None) -> int:
    status = 0
    capture = output is not None or command == "format"
    chunks: list[str] = []
    for offset in range(0, len(files), 50):
        batch = files[offset : offset + 50]
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                command,
                "--config",
                str(RUFF_CONFIG),
                *options,
                *(os.path.relpath(path) for path in batch),
            ],
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if output is not None else None,
            text=True,
            check=False,
        )
        if capture:
            chunks.append(result.stdout)
        status = max(status, result.returncode)
    if command == "format":
        chunks = [_summarize_format_output("".join(chunks))]
    if output is not None:
        output.extend(chunks)
    elif capture:
        print("".join(chunks), end="")
    return status
