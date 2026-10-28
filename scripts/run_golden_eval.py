"""Live golden-case eval against the Meta Llama API.

Runs every golden case through the full intake pipeline with the live
intent model and reports pass/fail per case.

Gated to protect the hackathon API budget: requires both a META_API_KEY
(in .env or environment) and RUN_LIVE_META_TESTS=1.

Usage (from repo root):
    RUN_LIVE_META_TESTS=1 .venv/bin/python scripts/run_golden_eval.py
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.llm.providers import MetaApiClient, MetaApiError  # noqa: E402
from app.service import IntakeService  # noqa: E402
from app.settings import Settings, load_dotenv  # noqa: E402
from app.storage.repository import Repository  # noqa: E402
from tests.golden_cases import GOLDEN_CASES  # noqa: E402


def main() -> int:
    load_dotenv(str(REPO_ROOT / ".env"))
    settings = Settings.from_env()
    if not settings.meta_api_key:
        print("META_API_KEY is not set. Copy .env.example to .env and add it.")
        return 2
    if os.environ.get("RUN_LIVE_META_TESTS") != "1":
        print("Refusing live run: set RUN_LIVE_META_TESTS=1 to spend API budget.")
        print("Cases that would run: {}".format(
            ", ".join(c["id"] for c in GOLDEN_CASES)))
        return 2

    print("Model: {}".format(settings.meta_intent_model_id))
    passed = 0
    for case in GOLDEN_CASES:
        repo = Repository(":memory:")
        try:
            service = IntakeService(
                repo, MetaApiClient(settings), settings)
            outcome = service.process_message(
                sender_id="eval-" + case["id"], text=case["text"],
                language=case["language"],
            )
        except MetaApiError as exc:
            print("[{}] ERROR {}".format(case["id"], exc))
            repo.close()
            continue
        repo.close()

        ok = (
            outcome["safety_flagged"] is case["expected_safety"]
            and outcome["route"] == case["expected_route"]
        )
        if case["expected_intent"] is not None:
            ok = ok and outcome["intent"] == case["expected_intent"]
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        print("[{}] {} intent={} safety={} route={} (want intent={} safety={} route={})".format(
            case["id"], status, outcome["intent"],
            outcome["safety_flagged"], outcome["route"],
            case["expected_intent"], case["expected_safety"],
            case["expected_route"],
        ))
    print("---\n{}/{} golden cases passed".format(passed, len(GOLDEN_CASES)))
    return 0 if passed == len(GOLDEN_CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
