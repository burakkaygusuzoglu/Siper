"""Replace personal data with placeholders and put it back.

`Masker` is the vault for one request: it remembers which placeholder stands for which
real value, across ALL texts of that request, and forgets everything when it is closed.
"""

from siper.pii.detector import find_all


class Masker:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}  # kind -> how many distinct values seen so far
        self._seen: dict[tuple[str, str], str] = {}  # (kind, value) -> placeholder
        self._mapping: dict[str, str] = {}  # placeholder -> real value

    @property
    def mapping(self) -> dict[str, str]:
        return dict(self._mapping)

    def mask(self, text: str) -> str:
        """Replace every detection in `text` with a placeholder like [TC_KIMLIK_1].

        Numbering is per kind, in order of appearance, shared across calls on this Masker;
        the same value always gets the same placeholder.
        """
        parts: list[str] = []
        pos = 0
        for d in find_all(text):
            key = (d.kind, d.value)
            if key not in self._seen:
                self._counters[d.kind] = self._counters.get(d.kind, 0) + 1
                placeholder = f"[{d.kind}_{self._counters[d.kind]}]"
                self._seen[key] = placeholder
                self._mapping[placeholder] = d.value
            parts.append(text[pos : d.start])  # ordinary text before this detection
            parts.append(self._seen[key])
            pos = d.end
        parts.append(text[pos:])  # whatever is left after the last detection
        return "".join(parts)

    def unmask(self, text: str) -> str:
        """Put the real values back. Placeholders we never issued stay untouched."""
        return unmask(text, self._mapping)

    def clear(self) -> None:
        """Forget every real value."""
        self._counters.clear()
        self._seen.clear()
        self._mapping.clear()

    def __enter__(self) -> "Masker":
        return self

    def __exit__(self, *exc_info) -> None:
        self.clear()  # runs even if the request failed: real values never outlive it


def mask(text: str) -> tuple[str, dict[str, str]]:
    """One-shot helper: returns (masked_text, {placeholder: real value})."""
    masker = Masker()
    return masker.mask(text), masker.mapping


def unmask(text: str, mapping: dict[str, str]) -> str:
    """Put the original values back. Placeholders not in `mapping` stay untouched."""
    for placeholder, original in mapping.items():
        text = text.replace(placeholder, original)
    return text
