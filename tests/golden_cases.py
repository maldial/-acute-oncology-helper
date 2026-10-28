"""Golden cases: 10 synthetic cases (+1 Urdu bonus) shared by the deterministic
test suite and the live-model eval script (scripts/run_golden_eval.py).

expected_intent is None for safety cases: the Safety Gate overrides intent,
so only safety + route are gated there.
"""
from typing import Any, Dict, List

GOLDEN_CASES: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "text": "My next chemo date I don't know, nobody is picking up the phone in the lung team.",
        "language": "en",
        "expected_intent": "ADMIN",
        "expected_safety": False,
        "expected_route": "ADMIN_QUEUE",
        "stub_intent": "ADMIN",
        "stub_evidence": "next chemo date",
        "note": "Admin: appointment query + cannot reach another team.",
    },
    {
        "id": "G02",
        "text": "Today my blood test is done at GP, just wanted to tell the team, every week I do.",
        "language": "en",
        "expected_intent": "CONFIRMATION",
        "expected_safety": False,
        "expected_route": "CONFIRMATIONS_QUEUE",
        "stub_intent": "CONFIRMATION",
        "stub_evidence": "blood test is done",
        "note": "Confirmation: weekly bloods done, nothing asked.",
    },
    {
        "id": "G03",
        "text": "Can I take the flu injection? My GP is asking, I am on treatment.",
        "language": "en",
        "expected_intent": "INFORMATION",
        "expected_safety": False,
        "expected_route": "INFO_QUEUE",
        "stub_intent": "INFORMATION",
        "stub_evidence": "flu injection",
        "note": "Info request: vaccine question, no symptom.",
    },
    {
        "id": "G04",
        "text": "Please tell the lung team I need to change my appointment to next week.",
        "language": "en",
        "expected_intent": "TEAM_MESSAGE",
        "expected_safety": False,
        "expected_route": "FORWARD_QUEUE",
        "stub_intent": "TEAM_MESSAGE",
        "stub_evidence": "tell the lung team",
        "note": "Message for another team.",
    },
    {
        "id": "G05",
        "text": "From morning loose motions, four five times, I had Keytruda three weeks ago.",
        "language": "en",
        "expected_intent": "SYMPTOM_REPORT",
        "expected_safety": False,
        "expected_route": "CLINICAL_PIPELINE",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "loose motions",
        "note": "Symptom: diarrhoea + immunotherapy history (Keytruda).",
    },
    {
        "id": "G06",
        "text": "This is my Monday weekly check, stools are better than last week.",
        "language": "en",
        "expected_intent": "SYMPTOM_REPORT",
        "expected_safety": False,
        "expected_route": "CLINICAL_PIPELINE",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "Monday weekly check",
        "note": "Scheduled follow-up report mentioning progress.",
    },
    {
        "id": "G07",
        "text": "I feel hot and shivery, my temperature is 38.5.",
        "language": "en",
        "expected_intent": None,
        "expected_safety": True,
        "expected_route": "SAFETY_ESCALATION",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "temperature is 38.5",
        "note": "Fever hard-stop overrides everything.",
    },
    {
        "id": "G08",
        "text": "I have chest pain since this morning.",
        "language": "en",
        "expected_intent": None,
        "expected_safety": True,
        "expected_route": "SAFETY_ESCALATION",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "chest pain",
        "note": "Chest pain hard-stop.",
    },
    {
        "id": "G09",
        "text": "I feel breathless even when I am resting.",
        "language": "en",
        "expected_intent": None,
        "expected_safety": True,
        "expected_route": "SAFETY_ESCALATION",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "breathless",
        "note": "Breathlessness at rest hard-stop.",
    },
    {
        "id": "G10",
        "text": "Hello? Is anyone there?",
        "language": "en",
        "expected_intent": "UNCLEAR",
        "expected_safety": False,
        "expected_route": "CLARIFICATION",
        "stub_intent": "UNCLEAR",
        "stub_evidence": "Hello?",
        "note": "Greeting only: too vague to route.",
    },
    {
        "id": "G11",
        "text": "Assalamualaikum, subah se loose motions hain, 4-5 dafa.",
        "language": "ur",
        "expected_intent": "SYMPTOM_REPORT",
        "expected_safety": False,
        "expected_route": "CLINICAL_PIPELINE",
        "stub_intent": "SYMPTOM_REPORT",
        "stub_evidence": "loose motions",
        "note": "Bonus: mixed Urdu/English symptom report.",
    },
]


def stub_response(case: Dict[str, Any]) -> str:
    import json

    return json.dumps(
        {
            "intent": case["stub_intent"],
            "evidence": case["stub_evidence"],
            "confidence": 0.95,
        }
    )
