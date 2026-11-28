"""E-mail recognizer (pattern only: an address has no checksum)."""

import re

from siper.pii.types import Detection

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")


def find_email(text: str) -> list[Detection]:
    return [
        Detection(kind="EMAIL", start=m.start(), end=m.end(), value=m.group())
        for m in _EMAIL.finditer(text)
    ]
