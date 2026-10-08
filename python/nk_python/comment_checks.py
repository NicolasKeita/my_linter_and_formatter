"""Token-based comment placement and optional language checks."""

import io
import re
import tokenize
from pathlib import Path

from .model import Issue

try:
    from lingua import Language, LanguageDetectorBuilder
except ImportError:
    Language = None
    LanguageDetectorBuilder = None

LANGUAGE_AVAILABLE = LanguageDetectorBuilder is not None
_detector = None
_DIRECTIVE = re.compile(
    r"^(?:!|coding[:=]|noqa\b|type:\s*ignore\b|pyright:\s*ignore\b|"
    r"pylint:|fmt:|ruff:|isort:|pragma:\s*no cover\b)",
    re.IGNORECASE,
)
_WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+")
_META_WORD = re.compile(r"^(?:TODO|FIXME|XXX|HACK|NOTE|WIP)$", re.IGNORECASE)


def check_comments(path: Path, source: str, functions: list[tuple[int, int]]) -> list[Issue]:
    issues: list[Issue] = []
    source_lines = source.splitlines()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            line_number, column = token.start
            comment = token.string[1:].strip()
            if _DIRECTIVE.match(comment):
                continue
            inside = any(start <= line_number <= end for start, end in functions)
            if inside:
                issues.append(
                    Issue(path, line_number, "PY006", "Use a docstring or clear code instead of a function comment.")
                )
            elif source_lines[line_number - 1][:column].strip():
                issues.append(Issue(path, line_number, "PY005", "Place the comment on its own line."))
            language = _comment_language(comment)
            if language:
                issues.append(Issue(path, line_number, "PY007", f"Comment appears to be in {language}; use English."))
    except (tokenize.TokenError, IndentationError):
        pass
    return issues


def _comment_language(comment: str) -> str | None:
    if not LANGUAGE_AVAILABLE:
        return None
    words = [word for word in _WORD.findall(comment) if _natural_word(word)]
    if len(words) < 3 or len(" ".join(words)) < 20:
        return None
    confidences = _get_detector().compute_language_confidence_values(" ".join(words))
    if not confidences or confidences[0].language == Language.ENGLISH:
        return None
    english = next((item.value for item in confidences if item.language == Language.ENGLISH), 0.0)
    margin = 0.35 if len(words) <= 5 else 0.15
    if confidences[0].value - english < margin:
        return None
    return confidences[0].language.name.title()


def _natural_word(word: str) -> bool:
    if _META_WORD.fullmatch(word) or word.isupper():
        return False
    return not any(left.islower() and right.isupper() for left, right in zip(word, word[1:], strict=False))


def _get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.GERMAN
        ).build()
    return _detector
