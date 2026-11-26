"""API key and JWT recognizers (pattern only; they have distinctive prefixes)."""

import re

from siper.pii.types import Detection

_API_KEY = re.compile(
    r"(?<![A-Za-z0-9_-])(?:"
    r"sk-[A-Za-z0-9_-]{20,}"  # OpenAI-style
    r"|AKIA[0-9A-Z]{16}"  # AWS access key id
    r"|gh[pousr]_[A-Za-z0-9]{36,}"  # GitHub token
    r"|AIza[0-9A-Za-z_-]{35}"  # Google API key
    r")(?![A-Za-z0-9_-])"
)

# header.payload.signature, each part base64url; header and payload start with "eyJ" ({"...).
_JWT = re.compile(r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def find_api_key(text: str) -> list[Detection]:
    return [
        Detection(kind="API_KEY", start=m.start(), end=m.end(), value=m.group())
        for m in _API_KEY.finditer(text)
    ]


def find_jwt(text: str) -> list[Detection]:
    return [
        Detection(kind="JWT", start=m.start(), end=m.end(), value=m.group())
        for m in _JWT.finditer(text)
    ]
