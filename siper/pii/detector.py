"""Run every recognizer and merge the results into one clean list."""

from siper.pii.card import find_card
from siper.pii.email import find_email
from siper.pii.iban import find_iban
from siper.pii.phone import find_phone
from siper.pii.secrets import find_api_key, find_jwt
from siper.pii.tc_kimlik import find_tc
from siper.pii.types import Detection

RECOGNIZERS = [find_tc, find_iban, find_card, find_email, find_phone, find_api_key, find_jwt]


def find_all(text: str) -> list[Detection]:
    """All detections in order of position, with overlaps resolved.

    When two detections overlap, the one that starts first wins; if they start at the
    same place, the longer one wins. So an IBAN's inner digit groups never also count
    as a card number.
    """
    found = [d for recognizer in RECOGNIZERS for d in recognizer(text)]
    found.sort(key=lambda d: (d.start, -(d.end - d.start)))

    result: list[Detection] = []
    last_end = 0
    for d in found:
        if d.start >= last_end:
            result.append(d)
            last_end = d.end
    return result
