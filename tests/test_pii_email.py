from siper.pii.email import find_email


def test_finds_simple_email_with_position():
    text = "Yaz: ali.veli+is@firma.com.tr lutfen"
    found = find_email(text)

    assert len(found) == 1
    assert found[0].kind == "EMAIL"
    assert found[0].value == "ali.veli+is@firma.com.tr"
    assert text[found[0].start : found[0].end] == "ali.veli+is@firma.com.tr"


def test_trailing_period_is_not_part_of_the_address():
    assert [d.value for d in find_email("mail ali@firma.com.")] == ["ali@firma.com"]


def test_finds_several_in_order():
    text = "a@x.org ve b@y.net"
    assert [d.value for d in find_email(text)] == ["a@x.org", "b@y.net"]


def test_ignores_text_that_is_not_an_email():
    assert find_email("ali@firma, @mention ve a@b") == []
