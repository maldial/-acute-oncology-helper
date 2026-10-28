"""LLM provider interface: live Meta client plus deterministic stubs.

The live client speaks to Meta's OpenAI-compatible Llama API endpoint
using only the standard library (urllib), so the runtime has no
third-party dependencies.
"""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.settings import Settings


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class LLMProvider:
    """Provider interface. Subclasses implement chat()."""

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 300,
    ) -> str:
        raise NotImplementedError


class MetaApiError(RuntimeError):
    pass


class MetaApiClient(LLMProvider):
    def __init__(self, settings: Settings, timeout_seconds: int = 90) -> None:
        if not settings.meta_api_key:
            raise MetaApiError("META_API_KEY is not set")
        self._settings = settings
        self._timeout = timeout_seconds

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 300,
    ) -> str:
        payload = {
            "model": self._settings.meta_intent_model_id,
            "messages": [
                {"role": m.role, "content": m.content} for m in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self._settings.meta_api_base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._settings.meta_api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise MetaApiError(
                "Meta API HTTP {}: {}".format(exc.code, detail)
            )
        except urllib.error.URLError as exc:
            raise MetaApiError("Meta API request failed: {}".format(exc))
        try:
            choice = body["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise MetaApiError(
                "Unexpected Meta API response: {}".format(str(body)[:500])
            )
        if content is None:
            raise MetaApiError(
                "Meta API returned no content (finish_reason={}). "
                "Reasoning models consume max_tokens on thinking tokens; "
                "raise max_tokens.".format(choice.get("finish_reason"))
            )
        return content


class StubProvider(LLMProvider):
    """Scripted provider for tests and offline demos."""

    def __init__(self, response: str = "{}") -> None:
        self.response = response
        self.calls: List[List[ChatMessage]] = []

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 300,
    ) -> str:
        self.calls.append(list(messages))
        return self.response


class ScriptedStubProvider(LLMProvider):
    """Maps exact input text to a scripted response (golden cases)."""

    def __init__(self, scripts: Dict[str, str], default: str = "{}") -> None:
        self._scripts = scripts
        self._default = default
        self.calls: List[List[ChatMessage]] = []

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 300,
    ) -> str:
        self.calls.append(list(messages))
        user_text = messages[-1].content if messages else ""
        return self._scripts.get(user_text, self._default)
