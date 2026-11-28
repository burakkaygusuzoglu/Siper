from siper.pii.masker import mask, unmask


def test_masks_a_tc_number():
    masked, mapping = mask("TC'm 12345678950, kaydet")

    assert masked == "TC'm [TC_KIMLIK_1], kaydet"
    assert mapping == {"[TC_KIMLIK_1]": "12345678950"}


def test_numbering_is_per_kind_and_in_order_of_appearance():
    masked, mapping = mask("A 12345678950 B 98765432150 C ali@firma.com")

    assert masked == "A [TC_KIMLIK_1] B [TC_KIMLIK_2] C [EMAIL_1]"
    assert mapping == {
        "[TC_KIMLIK_1]": "12345678950",
        "[TC_KIMLIK_2]": "98765432150",
        "[EMAIL_1]": "ali@firma.com",
    }


def test_same_value_gets_the_same_placeholder():
    masked, mapping = mask("12345678950 ve yine 12345678950")

    assert masked == "[TC_KIMLIK_1] ve yine [TC_KIMLIK_1]"
    assert mapping == {"[TC_KIMLIK_1]": "12345678950"}


def test_text_without_personal_data_is_unchanged():
    assert mask("Bugun hava guzel.") == ("Bugun hava guzel.", {})


def test_original_values_never_appear_in_masked_text():
    text = "TC 12345678950 IBAN TR330006100519786457841326 mail ali@firma.com"
    masked, _ = mask(text)

    for secret in ("12345678950", "TR330006100519786457841326", "ali@firma.com"):
        assert secret not in masked


def test_unmask_restores_the_original_text():
    text = "TC 12345678950, mail ali@firma.com, tekrar 12345678950"
    masked, mapping = mask(text)

    assert unmask(masked, mapping) == text


def test_unmask_works_on_a_model_reply_that_reuses_placeholders():
    _, mapping = mask("TC 12345678950")
    reply = "Tamam, [TC_KIMLIK_1] numarali kaydi buldum."

    assert unmask(reply, mapping) == "Tamam, 12345678950 numarali kaydi buldum."


def test_unmask_leaves_unknown_placeholders_alone():
    assert unmask("[IBAN_9] bilinmiyor", {}) == "[IBAN_9] bilinmiyor"
