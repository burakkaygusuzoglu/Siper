import pytest

from siper.pii.secrets import find_api_key, find_jwt

JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaSJ9."
    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
)


@pytest.mark.parametrize(
    "key",
    [
        "sk-" + "a1B2c3D4e5" * 3,
        "AKIAIOSFODNN7EXAMPLE",
        "ghp_" + "a1B2c3D4e5" * 4,
        "AIza" + "a1B2c3D4e5" * 3 + "xyz12",
    ],
)
def test_finds_api_keys(key):
    text = f"key={key} done"
    found = find_api_key(text)

    assert len(found) == 1
    assert found[0].kind == "API_KEY"
    assert text[found[0].start : found[0].end] == key


def test_ignores_short_or_unprefixed_strings():
    assert find_api_key("sk-short, AKIA123, hello-world-token") == []


def test_finds_jwt():
    text = f"Authorization: Bearer {JWT}"
    found = find_jwt(text)

    assert len(found) == 1
    assert found[0].kind == "JWT"
    assert found[0].value == JWT
    assert text[found[0].start : found[0].end] == JWT


def test_ignores_two_part_token():
    assert find_jwt("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0") == []
