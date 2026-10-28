"""Phase 0: question registry, drug list, teaching cards load and validate."""
import json

import pytest

from app.clinical.registry import (
    RegistryError,
    get_question,
    load_drug_list,
    load_question_registry,
    load_teaching_card,
)


def test_registry_loads_six_questions_covering_abc_types():
    questions = load_question_registry()
    assert len(questions) == 6
    assert sorted(q.type for q in questions) == ["A", "A", "B", "B", "C", "C"]


def test_type_a_questions_have_bands_and_unknown_option():
    stools = get_question("stools_above_normal")
    assert list(stools.options) == ["1-3", "4-6", "7-9", "10+", "Don't know"]
    blood = get_question("blood_in_stool")
    assert "Don't know" in list(blood.options)


def test_type_b_questions_declare_confirmation_source():
    assert get_question("current_treatment").confirmation_source == "closed_drug_list"
    assert get_question("symptom_description").confirmation_source == "patient_readback"


def test_type_c_questions_are_never_patient_askable():
    for qid in ("neutrophil_count", "news_score"):
        question = get_question(qid)
        assert question.patient_askable is False
        assert "never ask the patient" in question.nurse_check.casefold()
    for qid in ("stools_above_normal", "blood_in_stool",
                "current_treatment", "symptom_description"):
        assert get_question(qid).patient_askable is True


def test_fact_fields_are_unique_per_question():
    facts = [q.maps_to_fact for q in load_question_registry()]
    assert len(set(facts)) == len(facts)


def test_urdu_text_is_flagged_pending_clinical_review():
    for question in load_question_registry():
        if question.type == "C":
            continue
        assert question.ur_text is None
        assert question.ur_status == "PENDING_CLINICAL_REVIEW"


def test_unknown_question_id_fails_closed():
    with pytest.raises(RegistryError):
        get_question("no_such_question")


def test_invalid_registry_fails_closed(tmp_path):
    bad = {"questions": [
        {"id": "dup", "type": "A", "en_text": "x?", "ur_status": "s",
         "maps_to_fact": "f1", "required": True,
         "options": ["Yes", "No", "Don't know"]},
        {"id": "dup", "type": "Z", "en_text": "y?", "ur_status": "s",
         "maps_to_fact": "f2", "required": True},
    ]}
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(RegistryError):
        load_question_registry(path)


def test_type_a_without_unknown_option_rejected(tmp_path):
    bad = {"questions": [
        {"id": "q1", "type": "A", "en_text": "x?", "ur_status": "s",
         "maps_to_fact": "f1", "required": True,
         "options": ["Yes", "No"]},
    ]}
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(RegistryError, match="Don't know"):
        load_question_registry(path)


def test_drug_list_lookup_by_alias():
    drugs = load_drug_list()
    assert drugs.find("Keytruda") == "pembrolizumab"
    assert drugs.find("5-FU") == "fluorouracil"
    assert drugs.find("capecitabine") == "capecitabine"


def test_drug_list_never_guesses_unknown_drugs():
    assert load_drug_list().find("mystery-mycin") is None


def test_teaching_cards_carry_source_metadata():
    g06 = load_teaching_card("UKONS-V4-G06")
    assert g06.page == 13
    assert "G21" in "".join(g06.cross_references) or "UKONS-V4-G21" in g06.cross_references
    g21 = load_teaching_card("UKONS-V4-G21")
    assert g21.page == 28
    for card in (g06, g21):
        assert "4.0" in card.source
        assert card.nurse_checks == ("neutrophil_count", "news_score")


def test_teaching_card_excerpts_not_yet_curated():
    # Guard: no grading/management content may render until the clinical
    # lead transcribes it from the source document. Update this test
    # deliberately when curation lands.
    for gid in ("UKONS-V4-G06", "UKONS-V4-G21"):
        card = load_teaching_card(gid)
        assert card.excerpts_curated is False
        assert card.grading_table == ()
        assert card.management_by_grade == ()


def test_unknown_guideline_id_fails_closed():
    with pytest.raises(RegistryError):
        load_teaching_card("UKONS-V4-G99")
