"""Intent Agent: ONE job — classify why the person is contacting the service.

Strict validation in code: the model must return JSON with an allowed
intent, a verbatim evidence span from the input, and confidence >= 0.60.
Any failure degrades to UNCLEAR. Temperature is always 0.
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.llm.providers import ChatMessage, LLMProvider

SYMPTOM_REPORT = "SYMPTOM_REPORT"
CONFIRMATION = "CONFIRMATION"
ADMIN = "ADMIN"
INFORMATION = "INFORMATION"
TEAM_MESSAGE = "TEAM_MESSAGE"
UNCLEAR = "UNCLEAR"

ALLOWED_INTENTS = (
    SYMPTOM_REPORT,
    CONFIRMATION,
    ADMIN,
    INFORMATION,
    TEAM_MESSAGE,
    UNCLEAR,
)

CONFIDENCE_FLOOR = 0.60

SYSTEM_PROMPT = """You classify why a cancer patient (or someone helping them) is contacting the Acute Oncology service. Reply with JSON only, exactly this shape:
{"intent": "<ONE_OF_BELOW>", "evidence": "<exact words copied from the message>", "confidence": <0.0-1.0>}

Allowed intents:
- SYMPTOM_REPORT: reporting a symptom, side effect, how they feel, or a scheduled follow-up report (e.g. weekly check).
- CONFIRMATION: confirming something is done (e.g. blood test done) with nothing else asked.
- ADMIN: appointments, scheduling, test dates, referrals, prescription logistics, difficulty reaching another team.
- INFORMATION: a general question (vaccines, food, activity) with no symptom reported.
- TEAM_MESSAGE: a message explicitly for a different team or person to receive.
- UNCLEAR: cannot tell, greeting only, or too vague.

Rules:
- "evidence" must be words copied exactly from the message, not paraphrased.
- If the message reports any symptom or feeling unwell AND asks something else, choose SYMPTOM_REPORT.
- A scheduled check-in that mentions symptoms or progress is SYMPTOM_REPORT, not CONFIRMATION.
- If unsure, choose UNCLEAR with confidence below 0.60."""


@dataclass(frozen=True)
class IntentResult:
    intent: str
    evidence: str
    confidence: float
    raw: str


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.startswith("json"):
            text = text[4:]
        end = text.rfind("```")
        if end >= 0:
            text = text[:end]
    return text.strip()


def _validate(text: str, raw: str) -> Optional[IntentResult]:
    try:
        data = json.loads(_strip_fences(raw))  # type: Dict[str, Any]
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    intent = data.get("intent")
    evidence = data.get("evidence")
    confidence = data.get("confidence")
    if intent not in ALLOWED_INTENTS:
        return None
    if not isinstance(evidence, str) or not evidence.strip():
        return None
    if evidence.strip().casefold() not in text.casefold():
        return None  # evidence must be verbatim from the input
    if not isinstance(confidence, (int, float)):
        return None
    if not 0.0 <= float(confidence) <= 1.0:
        return None
    if float(confidence) < CONFIDENCE_FLOOR:
        return None
    return IntentResult(
        intent=intent,
        evidence=evidence.strip(),
        confidence=float(confidence),
        raw=raw,
    )


def classify_intent(
    text: str, provider: LLMProvider, language: str = "en"
) -> IntentResult:
    """Classify the contact reason. Never raises on model output: failures
    degrade to UNCLEAR."""
    user_content = text
    if language and language.lower() != "en":
        user_content = "[language: {}] {}".format(language, text)
    # Generous token budget: reasoning models spend tokens thinking before
    # answering, and the actual JSON reply is short.
    raw = provider.chat(
        messages=[
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_content),
        ],
        temperature=0.0,
        max_tokens=2000,
    ) or ""
    result = _validate(text, raw)
    if result is None:
        return IntentResult(intent=UNCLEAR, evidence="", confidence=0.0,
                            raw=raw)
    return result
