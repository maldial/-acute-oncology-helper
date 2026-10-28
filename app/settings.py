"""Settings loaded from environment (optionally via a local .env file).

Only simple string values. Secrets are never logged or committed.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def load_dotenv(path: Optional[str] = None) -> None:
    """Minimal .env loader (KEY=VALUE lines, # comments, no interpolation).

    Never overwrites variables already present in the environment.
    """
    dotenv_path = Path(path) if path else Path(".env")
    if not dotenv_path.is_file():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    meta_api_base_url: str = "https://api.meta.ai/v1"
    meta_api_key: str = ""
    meta_intent_model_id: str = "muse-spark-1.3"
    ao_helpline_number: str = ""
    ao_db_path: str = "app.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            meta_api_base_url=os.environ.get(
                "META_API_BASE_URL", "https://api.meta.ai/v1"
            ).rstrip("/"),
            meta_api_key=os.environ.get("META_API_KEY", ""),
            meta_intent_model_id=os.environ.get(
                "META_INTENT_MODEL_ID", "muse-spark-1.3"
            ),
            ao_helpline_number=os.environ.get("AO_HELPLINE_NUMBER", ""),
            ao_db_path=os.environ.get("AO_DB_PATH", "app.db"),
        )

    @property
    def helpline_display(self) -> str:
        if self.ao_helpline_number.strip():
            return "the 24-hour Acute Oncology helpline on {}".format(
                self.ao_helpline_number.strip()
            )
        return "your 24-hour Acute Oncology helpline"
