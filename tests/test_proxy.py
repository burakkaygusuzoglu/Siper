import json

import httpx
import pytest
from fastapi.testclient import TestClient

from siper.app import app

REAL_ASYNC_CLIENT = httpx.AsyncClient


def fake_upstream(monkeypatch, handler):
    """Make the proxy talk to `handler` instead of a real LLM server."""

    def factory(*args, **kwargs):
        return REAL_ASYNC_CLIENT(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_forwards_request_and_returns_upstream_response(client, monkeypatch):
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "hi"}}]})

    fake_upstream(monkeypatch, handler)
    payload = {"model": "m", "messages": [{"role": "user", "content": "hello"}]}

    response = client.post("/v1/chat/completions", json=payload)

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hi"
    assert seen["body"] == payload
    assert seen["url"].endswith("/v1/chat/completions")


def test_upstream_error_status_is_passed_through(client, monkeypatch):
    fake_upstream(monkeypatch, lambda request: httpx.Response(400, json={"error": "bad"}))

    response = client.post("/v1/chat/completions", json={"model": "m", "messages": []})

    assert response.status_code == 400
    assert response.json() == {"error": "bad"}


def test_unreachable_upstream_returns_502(client, monkeypatch):
    def handler(request):
        raise httpx.ConnectError("connection refused")

    fake_upstream(monkeypatch, handler)

    response = client.post("/v1/chat/completions", json={"model": "m", "messages": []})

    assert response.status_code == 502
    assert response.json() == {"error": "upstream unreachable"}
