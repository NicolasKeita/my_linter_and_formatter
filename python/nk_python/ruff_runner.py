"""Run Ruff in batches, optionally collecting its output for a check summary."""

import os
import subprocess
import sys
from pathlib import Path

RUFF_CONFIG = Path(__file__).with_name("ruff.toml")


def run_ruff(command: str, files: list[Path], *options: str, output: list[str] | None = None) -> int:
    status = 0
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
            stdout=subprocess.PIPE if output is not None else None,
            stderr=subprocess.STDOUT if output is not None else None,
            text=True,
            check=False,
        )
        if output is not None:
            output.append(result.stdout)
        status = max(status, result.returncode)
    return status
