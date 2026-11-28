import pytest

from siper.pii.tc_kimlik import find_tc, is_valid_tc

VALID = ["12345678950", "98765432150", "10000000146", "55544433340"]


@pytest.mark.parametrize("number", VALID)
def test_valid_tc_numbers(number):
    assert is_valid_tc(number) is True


@pytest.mark.parametrize(
    "number",
    [
        "12345678951",  # wrong 11th digit
        "12345678960",  # wrong 10th digit
        "01234567890",  # starts with 0
        "1234567895",  # 10 digits
        "123456789500",  # 12 digits
        "1234567895a",  # not all digits
        "",  # empty
    ],
)
def test_invalid_tc_numbers(number):
    assert is_valid_tc(number) is False


def test_find_tc_returns_detection_with_position():
    text = "TC'm 12345678950, lutfen kaydet."
    found = find_tc(text)

    assert len(found) == 1
    detection = found[0]
    assert detection.kind == "TC_KIMLIK"
    assert detection.value == "12345678950"
    assert text[detection.start : detection.end] == "12345678950"


def test_find_tc_ignores_11_digit_numbers_that_fail_checksum():
    assert find_tc("Siparis no: 12345678951") == []


def test_find_tc_ignores_digits_inside_a_longer_number():
    assert find_tc("kod 123456789501 ve 912345678950") == []


def test_find_tc_finds_several_in_order():
    text = "A: 12345678950 B: 98765432150"
    values = [d.value for d in find_tc(text)]
    assert values == ["12345678950", "98765432150"]
