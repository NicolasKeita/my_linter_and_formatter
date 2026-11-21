"""Compare differing words without letting identical context inflate similarity."""

from .distance import edit_distance
from .identity import name_body


def split_words(stem: str) -> list[str]:
    value = name_body(stem)
    separated: list[str] = []
    for index, character in enumerate(value):
        previous = value[index - 1] if index else ""
        following = value[index + 1] if index + 1 < len(value) else ""
        boundary = character.isupper() and (
            previous.islower() or previous.isdecimal() or (previous.isupper() and following.islower())
        )
        if boundary:
            separated.append("_")
        separated.append(character)
    return [word.lower() for word in "".join(separated).split("_") if word]


def differing_words_match(left: str, right: str) -> bool:
    first, second = split_words(left), split_words(right)
    if len(first) != len(second):
        return False
    for word, other in zip(first, second):
        if word != other:
            length = max(len(word), len(other))
            if abs(len(word) - len(other)) * 100 > length * 15:
                return False
            if edit_distance(word, other) * 100 > length * 15:
                return False
    return bool(first)
