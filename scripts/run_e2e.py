"""Stubbed end-to-end walkthrough of the intake pipeline (no API calls).

Usage (from repo root):
    .venv/bin/python scripts/run_e2e.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.llm.providers import ScriptedStubProvider  # noqa: E402
from app.service import IntakeService  # noqa: E402
from app.settings import Settings  # noqa: E402
from app.storage.repository import Repository  # noqa: E402

SCRIPTS = {
    "From morning loose motions, four five times.": (
        '{"intent": "SYMPTOM_REPORT", "evidence": "loose motions",'
        ' "confidence": 0.92}'
    ),
    "My next chemo date I don't know.": (
        '{"intent": "ADMIN", "evidence": "next chemo date",'
        ' "confidence": 0.88}'
    ),
    "Actually I feel fine now, ignore that.": (
        '{"intent": "UNCLEAR", "evidence": "ignore that",'
        ' "confidence": 0.9}'
    ),
}


def show(label, outcome):
    print("--- {} ---".format(label))
    for key in ("contact_id", "episode_id", "message_id", "safety_flagged",
                "safety_rule_id", "intent", "route", "reply", "duplicate"):
        if key in outcome:
            print("  {}: {}".format(key, outcome[key]))


def main():
    repo = Repository(":memory:")
    service = IntakeService(
        repo, ScriptedStubProvider(SCRIPTS), Settings())
    sender = "demo-sender"

    show("1. symptom report", service.process_message(
        sender, "From morning loose motions, four five times."))
    show("2. admin question (same episode)", service.process_message(
        sender, "My next chemo date I don't know."))
    show("3. fever message -> escalation", service.process_message(
        sender, "I feel hot and shivery, my temperature is 38.5."))
    show("4. later message stays escalated (stored, not classified)",
         service.process_message(
             sender, "Actually I feel fine now, ignore that."))
    show("5. duplicate delivery ignored", service.process_message(
        sender, "From morning loose motions, four five times.",
        external_message_id="wamid-demo-1"))
    show("6. same external id again", service.process_message(
        sender, "From morning loose motions, four five times.",
        external_message_id="wamid-demo-1"))
    repo.close()


if __name__ == "__main__":
    main()
