from app.safety.gate import SafetyGate


def test_fever_triggers_with_verbatim_evidence():
    result = SafetyGate().check("I feel hot, my temperature is 38.5.")
    assert result.flagged is True
    assert result.rule_id == "DEMO_FEVER"
    assert result.evidence in "I feel hot, my temperature is 38.5."


def test_chest_pain_triggers():
    result = SafetyGate().check("I have chest pain since this morning.")
    assert result.flagged is True
    assert result.rule_id == "DEMO_CHEST_PAIN"


def test_breathlessness_triggers():
    result = SafetyGate().check("I feel breathless even when I am resting.")
    assert result.flagged is True
    assert result.rule_id == "DEMO_BREATHLESS"


def test_very_unwell_triggers():
    result = SafetyGate().check("I feel very unwell today.")
    assert result.flagged is True
    assert result.rule_id == "DEMO_VERY_UNWELL"


def test_collapse_triggers():
    result = SafetyGate().check("My husband collapsed in the kitchen.")
    assert result.flagged is True
    assert result.rule_id == "DEMO_COLLAPSE"


def test_matching_is_case_insensitive():
    result = SafetyGate().check("I have a FEVER.")
    assert result.flagged is True
    assert result.evidence == "FEVER"


def test_routine_messages_do_not_trigger():
    clean = [
        "My next chemo date I don't know.",
        "Today my blood test is done at GP.",
        "Can I take the flu injection?",
        "From morning loose motions, four five times.",
        "Hello? Is anyone there?",
    ]
    gate = SafetyGate()
    for text in clean:
        assert gate.check(text).flagged is False, text


def test_extra_flagger_can_add_but_never_clear():
    gate = SafetyGate()

    def silent(text):
        return None

    def alarming(text):
        return ("EXTRA_MODEL", "model-flagged span")

    flagged = gate.check("I have a fever.", extra_flagger=silent)
    assert flagged.flagged is True
    assert flagged.rule_id == "DEMO_FEVER"

    added = gate.check("My next chemo date?", extra_flagger=alarming)
    assert added.flagged is True
    assert added.rule_id == "EXTRA_MODEL"

    quiet = gate.check("My next chemo date?", extra_flagger=silent)
    assert quiet.flagged is False
