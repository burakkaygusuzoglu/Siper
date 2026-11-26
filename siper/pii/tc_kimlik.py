"""TC kimlik no recognizer: regex finds candidates, the checksum confirms them."""

import re

from siper.pii.types import Detection

# 11 digits that are not part of a longer run of digits.
_CANDIDATE = re.compile(r"(?<!\d)\d{11}(?!\d)")


def is_valid_tc(number: str) -> bool:
    """True only if `number` is a mathematically valid TC kimlik no."""
    if len(number) != 11 or not number.isdigit():
        return False
    if number[0] == "0":
        return False

    d = [int(c) for c in number]
    odd_sum = d[0] + d[2] + d[4] + d[6] + d[8]
    even_sum = d[1] + d[3] + d[5] + d[7]

    if (odd_sum * 7 - even_sum) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def find_tc(text: str) -> list[Detection]:
    """Find valid TC kimlik numbers in `text`, in order of appearance."""
    return [
        Detection(kind="TC_KIMLIK", start=m.start(), end=m.end(), value=m.group())
        for m in _CANDIDATE.finditer(text)
        if is_valid_tc(m.group())
    ]
