"""Turkish mobile phone recognizer (pattern only)."""

import re

from siper.pii.types import Detection

# Optional prefix (+90 / 0090 / 90 / 0), then 5XX XXX XX XX with optional spaces or dashes.
_PHONE = re.compile(
    r"(?<!\d)(?:(?:\+90|0090|90|0)[ -]?)?5\d{2}[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}(?!\d)"
)


def find_phone(text: str) -> list[Detection]:
    return [
        Detection(kind="PHONE", start=m.start(), end=m.end(), value=m.group())
        for m in _PHONE.finditer(text)
    ]
