from app.routing.router import route


def test_intent_routes():
    assert route("SYMPTOM_REPORT", False) == "CLINICAL_PIPELINE"
    assert route("CONFIRMATION", False) == "CONFIRMATIONS_QUEUE"
    assert route("ADMIN", False) == "ADMIN_QUEUE"
    assert route("INFORMATION", False) == "INFO_QUEUE"
    assert route("TEAM_MESSAGE", False) == "FORWARD_QUEUE"
    assert route("UNCLEAR", False) == "CLARIFICATION"


def test_unknown_intent_falls_back_to_clarification():
    assert route("SOMETHING_ELSE", False) == "CLARIFICATION"


def test_safety_overrides_every_intent():
    for intent in ("SYMPTOM_REPORT", "CONFIRMATION", "ADMIN",
                   "INFORMATION", "TEAM_MESSAGE", "UNCLEAR"):
        assert route(intent, True) == "SAFETY_ESCALATION"
