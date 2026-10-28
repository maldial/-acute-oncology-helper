"""MetaApiClient unit tests with mocked HTTP (no network, no key)."""
import io
import json
import urllib.error

import pytest

from app.llm.providers import ChatMessage, MetaApiClient, MetaApiError
from app.settings import Settings


def settings():
    return Settings(
        meta_api_base_url="https://example.invalid/v1",
        meta_api_key="test-key",
        meta_intent_model_id="test-model",
    )


class FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def completion(content, finish_reason="stop"):
    return {
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": content},
            }
        ]
    }


def test_client_returns_content(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda request, timeout: FakeResponse(completion('{"a": 1}')),
    )
    client = MetaApiClient(settings())
    assert client.chat([ChatMessage("user", "hi")]) == '{"a": 1}'


def test_client_sends_bearer_auth_and_model(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["auth"] = request.get_header("Authorization")
        seen["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(completion("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    MetaApiClient(settings()).chat([ChatMessage("user", "hi")])
    assert seen["url"] == "https://example.invalid/v1/chat/completions"
    assert seen["auth"] == "Bearer test-key"
    assert seen["payload"]["model"] == "test-model"
    assert seen["payload"]["temperature"] == 0.0


def test_null_content_raises_clear_error(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda request, timeout: FakeResponse(
            completion(None, finish_reason="length")),
    )
    with pytest.raises(MetaApiError, match="no content"):
        MetaApiClient(settings()).chat([ChatMessage("user", "hi")])


def test_http_error_raises_meta_api_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {}, io.BytesIO(b"bad key"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(MetaApiError, match="401"):
        MetaApiClient(settings()).chat([ChatMessage("user", "hi")])


def test_missing_key_refuses_to_construct():
    with pytest.raises(MetaApiError, match="META_API_KEY"):
        MetaApiClient(Settings(meta_api_key=""))
