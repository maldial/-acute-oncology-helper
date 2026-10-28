import json

from app.agents.intent_agent import classify_intent
from app.llm.providers import StubProvider

TEXT = "My next chemo date I don't know."


def classify(raw):
    return classify_intent(TEXT, StubProvider(response=raw))


def test_valid_classification_passes_through():
    raw = json.dumps(
        {"intent": "ADMIN", "evidence": "next chemo date", "confidence": 0.9}
    )
    result = classify(raw)
    assert result.intent == "ADMIN"
    assert result.evidence == "next chemo date"
    assert result.confidence == 0.9


def test_malformed_json_degrades_to_unclear():
    result = classify("definitely not json")
    assert result.intent == "UNCLEAR"


def test_unknown_intent_degrades_to_unclear():
    raw = json.dumps(
        {"intent": "DIAGNOSE", "evidence": "chemo", "confidence": 0.9}
    )
    assert classify(raw).intent == "UNCLEAR"


def test_non_verbatim_evidence_degrades_to_unclear():
    raw = json.dumps(
        {"intent": "ADMIN", "evidence": "paraphrased words", "confidence": 0.9}
    )
    assert classify(raw).intent == "UNCLEAR"


def test_low_confidence_degrades_to_unclear():
    raw = json.dumps(
        {"intent": "ADMIN", "evidence": "chemo", "confidence": 0.59}
    )
    assert classify(raw).intent == "UNCLEAR"


def test_missing_fields_degrade_to_unclear():
    assert classify(json.dumps({"intent": "ADMIN"})).intent == "UNCLEAR"
    assert classify(json.dumps(["ADMIN"])).intent == "UNCLEAR"


def test_markdown_fences_are_tolerated():
    raw = '```json\n{"intent": "ADMIN", "evidence": "chemo", "confidence": 0.8}\n```'
    assert classify(raw).intent == "ADMIN"


def test_unclear_with_confidence_is_accepted():
    raw = json.dumps(
        {"intent": "UNCLEAR", "evidence": "don't know", "confidence": 0.7}
    )
    result = classify(raw)
    assert result.intent == "UNCLEAR"
    assert result.confidence == 0.7


def test_none_content_degrades_to_unclear_without_raising():
    class NoneProvider(StubProvider):
        def chat(self, messages, temperature=0.0, max_tokens=300):
            return None

    result = classify_intent(TEXT, NoneProvider())
    assert result.intent == "UNCLEAR"


def test_language_tagged_input_validates_against_original_text():
    provider = StubProvider(
        response=json.dumps(
            {"intent": "ADMIN", "evidence": "chemo", "confidence": 0.9}
        )
    )
    result = classify_intent(TEXT, provider, language="ur")
    assert result.intent == "ADMIN"
    assert provider.calls[0][-1].content.startswith("[language: ur]")
