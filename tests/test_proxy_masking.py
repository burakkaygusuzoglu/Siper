import json

import httpx
import pytest
from fastapi.testclient import TestClient

from siper.app import app

REAL_ASYNC_CLIENT = httpx.AsyncClient
TC = "12345678950"
IBAN = "TR330006100519786457841326"


def fake_upstream(monkeypatch, handler):
    def factory(*args, **kwargs):
        return REAL_ASYNC_CLIENT(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)


@pytest.fixture
def client():
    return TestClient(app)


def test_upstream_never_sees_real_values(client, monkeypatch):
    seen = {}

    def handler(request):
        seen["raw"] = request.content.decode()
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    fake_upstream(monkeypatch, handler)
    payload = {
        "model": "m",
        "messages": [
            {"role": "system", "content": "Sen bir asistansin."},
            {"role": "user", "content": f"TC'm {TC}, IBAN'im {IBAN}"},
        ],
    }

    response = client.post("/v1/chat/completions", json=payload)

    assert response.status_code == 200
    assert TC not in seen["raw"] and IBAN not in seen["raw"]
    assert seen["body"]["messages"][1]["content"] == "TC'm [TC_KIMLIK_1], IBAN'im [IBAN_1]"
    assert seen["body"]["messages"][0]["content"] == "Sen bir asistansin."


def test_reply_is_unmasked_for_the_client(client, monkeypatch):
    def handler(request):
        reply = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "[TC_KIMLIK_1] kaydi bulundu.",
                        "reasoning_content": "Kullanici [TC_KIMLIK_1] verdi.",
                    }
                }
            ]
        }
        return httpx.Response(200, json=reply)

    fake_upstream(monkeypatch, handler)

    response = client.post(
        "/v1/chat/completions",
        json={"model": "m", "messages": [{"role": "user", "content": f"TC {TC}"}]},
    )

    message = response.json()["choices"][0]["message"]
    assert message["content"] == f"{TC} kaydi bulundu."
    assert message["reasoning_content"] == f"Kullanici {TC} verdi."


def test_placeholders_are_shared_across_messages(client, monkeypatch):
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": []})

    fake_upstream(monkeypatch, handler)
    messages = [
        {"role": "user", "content": f"TC {TC}"},
        {"role": "assistant", "content": "[TC_KIMLIK_1] alindi"},
        {"role": "user", "content": f"yine {TC}"},
    ]

    client.post("/v1/chat/completions", json={"model": "m", "messages": messages})

    contents = [m["content"] for m in seen["body"]["messages"]]
    assert contents[0] == "TC [TC_KIMLIK_1]"
    assert contents[2] == "yine [TC_KIMLIK_1]"


def test_multi_part_content_is_masked_too(client, monkeypatch):
    seen = {}

    def handler(request):
        seen["raw"] = request.content.decode()
        return httpx.Response(200, json={"choices": []})

    fake_upstream(monkeypatch, handler)
    message = {"role": "user", "content": [{"type": "text", "text": f"TC {TC}"}]}

    client.post("/v1/chat/completions", json={"model": "m", "messages": [message]})

    assert TC not in seen["raw"]
    assert "[TC_KIMLIK_1]" in seen["raw"]


def test_unreachable_upstream_still_returns_502_with_masking(client, monkeypatch):
    def handler(request):
        raise httpx.ConnectError("refused")

    fake_upstream(monkeypatch, handler)

    response = client.post(
        "/v1/chat/completions",
        json={"model": "m", "messages": [{"role": "user", "content": f"TC {TC}"}]},
    )

    assert response.status_code == 502
    assert TC not in response.text
