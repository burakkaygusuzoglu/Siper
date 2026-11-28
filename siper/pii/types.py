"""Shared result type: every recognizer returns a list of Detection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    kind: str  # e.g. "TC_KIMLIK"
    start: int  # index of the first character in the text
    end: int  # index just after the last character (text[start:end] == value)
    value: str  # the matched text
