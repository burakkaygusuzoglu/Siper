import pytest

from siper.pii.masker import Masker


def test_numbering_is_shared_across_texts():
    masker = Masker()

    first = masker.mask("TC 12345678950")
    second = masker.mask("baska TC 98765432150 ve yine 12345678950")

    assert first == "TC [TC_KIMLIK_1]"
    assert second == "baska TC [TC_KIMLIK_2] ve yine [TC_KIMLIK_1]"


def test_unmask_restores_values_from_all_texts():
    masker = Masker()
    masker.mask("TC 12345678950")
    masker.mask("mail ali@firma.com")

    assert masker.unmask("[TC_KIMLIK_1] / [EMAIL_1]") == "12345678950 / ali@firma.com"


def test_clear_forgets_every_real_value():
    masker = Masker()
    masker.mask("TC 12345678950")

    masker.clear()

    assert masker.mapping == {}
    assert masker.unmask("[TC_KIMLIK_1]") == "[TC_KIMLIK_1]"


def test_leaving_the_with_block_clears_the_vault():
    with Masker() as masker:
        masker.mask("TC 12345678950")
        assert masker.mapping != {}

    assert masker.mapping == {}


def test_vault_is_cleared_even_when_the_block_raises():
    masker = Masker()
    with pytest.raises(RuntimeError):
        with masker:
            masker.mask("TC 12345678950")
            raise RuntimeError("boom")

    assert masker.mapping == {}
