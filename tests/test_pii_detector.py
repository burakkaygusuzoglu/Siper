from siper.pii.detector import find_all


def test_finds_every_kind_in_order_of_position():
    text = "TC 12345678950, mail ali@firma.com, tel 0532 123 45 67, kart 4111 1111 1111 1111"
    assert [d.kind for d in find_all(text)] == ["TC_KIMLIK", "EMAIL", "PHONE", "CARD"]


def test_spaced_iban_is_not_also_reported_as_a_card():
    found = find_all("IBAN TR33 0006 1005 1978 6457 8413 26 gonder")
    assert [d.kind for d in found] == ["IBAN"]


def test_returns_empty_list_when_nothing_found():
    assert find_all("Bugun hava cok guzel.") == []


def test_detections_never_overlap():
    text = "a 12345678950 b TR330006100519786457841326 c 4111111111111111 d x@y.com"
    found = find_all(text)
    for left, right in zip(found, found[1:]):
        assert left.end <= right.start
