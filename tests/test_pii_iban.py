import pytest

from siper.pii.iban import find_iban, is_valid_iban

VALID = [
    "TR330006100519786457841326",
    "TR420001000000000000000001",
    "TR320010300000000000000042",
    "TR33 0006 1005 1978 6457 8413 26",  # grouped with spaces
    "tr330006100519786457841326",  # lowercase
]


@pytest.mark.parametrize("iban", VALID)
def test_valid_ibans(iban):
    assert is_valid_iban(iban) is True


@pytest.mark.parametrize(
    "iban",
    [
        "TR340006100519786457841326",  # wrong check digits
        "TR33000610051978645784132",  # too short (25)
        "TR3300061005197864578413260",  # too long (27)
        "DE89370400440532013000",  # not Turkish
        "TR33000610051978645784132X",  # letter inside
        "",
    ],
)
def test_invalid_ibans(iban):
    assert is_valid_iban(iban) is False


def test_find_iban_returns_detection_with_position():
    text = "Hesap: TR330006100519786457841326 tesekkurler"
    found = find_iban(text)

    assert len(found) == 1
    assert found[0].kind == "IBAN"
    assert found[0].value == "TR330006100519786457841326"
    assert text[found[0].start : found[0].end] == "TR330006100519786457841326"


def test_find_iban_handles_spaced_format():
    text = "IBAN: TR33 0006 1005 1978 6457 8413 26."
    found = find_iban(text)

    assert [d.value for d in found] == ["TR33 0006 1005 1978 6457 8413 26"]


def test_find_iban_ignores_wrong_checksum():
    assert find_iban("TR340006100519786457841326") == []


def test_find_iban_finds_several_in_order():
    text = "A TR330006100519786457841326 B TR420001000000000000000001"
    assert [d.value for d in find_iban(text)] == [
        "TR330006100519786457841326",
        "TR420001000000000000000001",
    ]
