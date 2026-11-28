"""Turkish IBAN recognizer: regex finds candidates, MOD-97 confirms them."""

import re

from siper.pii.types import Detection

# "TR" + 2 check digits + 5 groups of 4 digits + 2 digits, optional spaces between groups.
_CANDIDATE = re.compile(
    r"(?<![A-Za-z0-9])TR\d{2}(?:\s?\d{4}){5}\s?\d{2}(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def is_valid_iban(iban: str) -> bool:
    """True only if `iban` is a valid Turkish IBAN (spaces allowed, any case)."""
    cleaned = iban.replace(" ", "").upper()
    if len(cleaned) != 26 or not cleaned.startswith("TR") or not cleaned[2:].isdigit():
        return False

    # Move the first 4 characters to the end, then turn letters into numbers (T=29, R=27).
    rearranged = cleaned[4:] + cleaned[:4]
    digits = "".join(str(int(c, 36)) for c in rearranged)
    return int(digits) % 97 == 1


def find_iban(text: str) -> list[Detection]:
    """Find valid Turkish IBANs in `text`, in order of appearance."""
    return [
        Detection(kind="IBAN", start=m.start(), end=m.end(), value=m.group())
        for m in _CANDIDATE.finditer(text)
        if is_valid_iban(m.group())
    ]
