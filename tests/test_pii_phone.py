import pytest

from siper.pii.phone import find_phone


@pytest.mark.parametrize(
    "number",
    [
        "+90 532 123 45 67",
        "+905321234567",
        "0532 123 45 67",
        "05321234567",
        "532 123 45 67",
        "0532-123-45-67",
    ],
)
def test_finds_turkish_mobile_formats(number):
    text = f"Ara beni: {number} sonra"
    found = find_phone(text)

    assert len(found) == 1
    assert found[0].kind == "PHONE"
    assert text[found[0].start : found[0].end] == number


def test_does_not_match_inside_a_longer_number():
    assert find_phone("55544433340") == []  # an 11-digit TC kimlik number
    assert find_phone("1234567890123") == []


def test_does_not_match_landlines():
    assert find_phone("0212 123 45 67") == []
