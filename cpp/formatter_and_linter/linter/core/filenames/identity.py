"""Normalize names without discarding their extension or technical role."""

import re
import unicodedata
from pathlib import Path

SEPARATORS = re.compile(r"[_\s\-\u2010-\u2015\u2212]+")
INVISIBLE = re.compile(r"[\u200b-\u200d\u2060\ufeff]")
NUMBERED_END = re.compile(r"(?:(?:part|chunk|split)[_\s-]*)?\d+$", re.IGNORECASE)
ROLES = (".test", ".spec", ".stories", ".d")


def name_parts(name: str) -> tuple[str, str]:
    path = Path(name)
    stem, role = path.stem, path.suffix.lower()
    if role in {".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs"}:
        for suffix in ROLES:
            if stem.lower().endswith(suffix):
                return stem[: -len(suffix)], suffix + role
    return stem, role


def spelling(stem: str) -> str:
    return INVISIBLE.sub("", unicodedata.normalize("NFKC", stem))


def normalized(stem: str) -> str:
    return spelling(stem).lower()


def name_body(stem: str) -> str:
    value = SEPARATORS.sub("_", spelling(stem))
    while True:
        previous = value
        value = NUMBERED_END.sub("", value.strip("_")).strip("_")
        if value == previous:
            return value


def base_name(stem: str) -> str:
    return name_body(stem).replace("_", "").lower()
