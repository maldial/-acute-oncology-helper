"""Manually close an episode (developer-only safety reset).

Closing is the only way to release a SAFETY_ESCALATED episode; there is
no AI-reachable path. Audit history is preserved.

Usage (from repo root):
    .venv/bin/python scripts/close_episode.py --episode E0001 --confirm E0001
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.settings import Settings, load_dotenv  # noqa: E402
from app.storage.repository import Repository  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", required=True)
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    if args.episode != args.confirm:
        print("Confirmation does not match. Aborting.")
        return 2
    load_dotenv(str(REPO_ROOT / ".env"))
    settings = Settings.from_env()
    repo = Repository(settings.ao_db_path)
    try:
        repo.close_episode(args.episode)
    finally:
        repo.close()
    print("Closed episode {}. History preserved.".format(args.episode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
