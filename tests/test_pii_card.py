import pytest

from siper.pii.card import find_card, is_luhn_valid


@pytest.mark.parametrize(
    "number",
    [
        "4111111111111111",
        "5500000000000004",
        "378282246310005",  # 15 digits
        "6011111111111117",
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
    ],
)
def test_valid_cards(number):
    assert is_luhn_valid(number) is True


@pytest.mark.parametrize(
    "number",
    [
        "4111111111111112",  # wrong last digit
        "411111111111",  # 12 digits, too short
        "41111111111111111111",  # 20 digits, too long
        "4111a11111111111",  # letter inside
        "",
    ],
)
def test_invalid_cards(number):
    assert is_luhn_valid(number) is False


def test_find_card_returns_detection_with_position():
    text = "Kart: 4111 1111 1111 1111 son kullanma 12/29"
    found = find_card(text)

    assert len(found) == 1
    assert found[0].kind == "CARD"
    assert text[found[0].start : found[0].end] == "4111 1111 1111 1111"


def test_find_card_ignores_failed_checksum():
    assert find_card("no: 4111111111111112") == []


def test_find_card_finds_several_in_order():
    text = "A 4111111111111111 B 5500000000000004"
    assert [d.value for d in find_card(text)] == ["4111111111111111", "5500000000000004"]
