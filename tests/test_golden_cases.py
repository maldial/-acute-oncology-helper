"""Golden cases through the full intake pipeline (scripted intent)."""
import json

import pytest

from app.llm.providers import ScriptedStubProvider
from app.service import IntakeService
from app.settings import Settings
from app.storage.repository import Repository
from tests.golden_cases import GOLDEN_CASES, stub_response


def script_key(case):
    if case["language"] != "en":
        return "[language: {}] {}".format(case["language"], case["text"])
    return case["text"]


@pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c["id"] for c in GOLDEN_CASES])
def test_golden_case(case):
    repo = Repository(":memory:")
    try:
        scripts = {script_key(case): stub_response(case)}
        provider = ScriptedStubProvider(scripts)
        service = IntakeService(repo, provider, Settings())
        outcome = service.process_message(
            sender_id="golden-" + case["id"], text=case["text"],
            language=case["language"],
        )
        assert outcome["duplicate"] is False
        assert outcome["safety_flagged"] is case["expected_safety"]
        assert outcome["route"] == case["expected_route"]
        if case["expected_intent"] is not None:
            assert outcome["intent"] == case["expected_intent"]
        else:
            # Safety cases never reach intent classification.
            assert outcome["intent"] is None
            assert provider.calls == []
        assert outcome["reply"]
    finally:
        repo.close()


def test_stub_evidence_is_verbatim_in_case_text():
    for case in GOLDEN_CASES:
        data = json.loads(stub_response(case))
        assert data["evidence"].casefold() in case["text"].casefold(), case["id"]
