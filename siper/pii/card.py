"""Payment card recognizer: regex finds candidates, the Luhn checksum confirms them."""

import re

from siper.pii.types import Detection

# 13-19 digits, optionally separated by single spaces or dashes.
_CANDIDATE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def is_luhn_valid(number: str) -> bool:
    """True if `number` (digits, spaces and dashes allowed) passes the Luhn check."""
    cleaned = number.replace(" ", "").replace("-", "")
    if not cleaned.isdigit() or not 13 <= len(cleaned) <= 19:
        return False

    total = 0
    for i, ch in enumerate(reversed(cleaned)):
        digit = int(ch)
        if i % 2 == 1:  # every second digit, counting from the right
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def find_card(text: str) -> list[Detection]:
    """Find card numbers that pass the Luhn check, in order of appearance."""
    return [
        Detection(kind="CARD", start=m.start(), end=m.end(), value=m.group())
        for m in _CANDIDATE.finditer(text)
        if is_luhn_valid(m.group())
    ]
