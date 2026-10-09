import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, order=True)
class Issue:
    path: Path
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{os.path.relpath(self.path)}:{self.line}: {self.code} {self.message}"
