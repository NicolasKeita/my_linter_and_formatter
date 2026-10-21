"""Classify explicit variants before applying the inclusive 85 percent threshold."""

from .distance import edit_distance
from .identity import base_name, name_parts, normalized


def reason(left: str, right: str, module: str = "") -> str | None:
    left_stem, left_role = name_parts(left)
    right_stem, right_role = name_parts(right)
    if left_role != right_role:
        return None
    first, second = base_name(left_stem), base_name(right_stem)
    if not first or not second:
        return None
    if first == second:
        return "same normalized base (numbering, separators or case)"
    if module:
        prefix = normalized(module) + "-"
        if normalized(left_stem).startswith(prefix) and normalized(right_stem).startswith(prefix):
            first, second = base_name(left_stem[len(module) + 1 :]), base_name(right_stem[len(module) + 1 :])
    if min(len(first), len(second)) < 6:
        return None
    length = max(len(first), len(second))
    if abs(len(first) - len(second)) * 100 > length * 15:
        return None
    distance = edit_distance(first, second)
    if distance * 100 <= length * 15:
        return f"similarity {100 * (length - distance) / length:.1f}% (threshold 85%)"
    return None
