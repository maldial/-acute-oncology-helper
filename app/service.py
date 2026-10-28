"""Intake pipeline: message -> contact/episode -> safety -> intent -> route.

Flow:
1. Hash the sender identifier; raw identifiers never touch storage or AI.
2. Identify/create contact and episode.
3. Store the message (deduplicated on external_message_id).
4. Run the Safety Gate. A flag escalates the episode permanently and
   overrides everything else.
5. Messages in an already-escalated episode are stored for audit but
   never reach intent classification.
6. Otherwise classify intent and route deterministically.
7. Reply text is always fixed config text, never model-generated.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.agents.intent_agent import classify_intent
from app.llm.providers import LLMProvider
from app.routing.router import SAFETY_ESCALATION, route
from app.safety.gate import SafetyGate
from app.settings import Settings
from app.storage.repository import Repository, hash_sender

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "outbound_responses.json"


def load_outbound_responses(config_path: Optional[Path] = None) -> Dict[str, str]:
    path = config_path or CONFIG_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    return dict(data["responses"])


class IntakeService:
    def __init__(
        self,
        repository: Repository,
        provider: LLMProvider,
        settings: Settings,
        gate: Optional[SafetyGate] = None,
    ) -> None:
        self._repo = repository
        self._provider = provider
        self._settings = settings
        self._gate = gate or SafetyGate()
        self._responses = load_outbound_responses()

    def _reply(self, route_name: str) -> str:
        template = self._responses[route_name]
        return template.replace("{helpline}", self._settings.helpline_display)

    def process_message(
        self,
        sender_id: str,
        text: str,
        language: str = "en",
        force_new_episode: bool = False,
        external_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if external_message_id:
            existing = self._repo.find_by_external_id(external_message_id)
            if existing:
                return {"duplicate": True,
                        "message_id": existing["message_id"],
                        "episode_id": existing["episode_id"]}

        contact = self._repo.get_or_create_contact(hash_sender(sender_id))
        episode = self._repo.get_or_create_episode(
            contact["contact_id"], force_new=force_new_episode
        )
        message = self._repo.save_message(
            contact_id=contact["contact_id"],
            episode_id=episode["episode_id"],
            direction="inbound",
            text=text,
            language=language,
            external_message_id=external_message_id,
        )

        safety = self._gate.check(text)
        if safety.flagged:
            assert safety.rule_id and safety.evidence
            self._repo.mark_message_safety(
                message["message_id"], safety.evidence, safety.rule_id
            )
            self._repo.mark_safety_escalated(
                episode["episode_id"], message["message_id"],
                safety.evidence, safety.rule_id,
            )
            return {
                "duplicate": False,
                "contact_id": contact["contact_id"],
                "episode_id": episode["episode_id"],
                "message_id": message["message_id"],
                "safety_flagged": True,
                "safety_rule_id": safety.rule_id,
                "safety_evidence": safety.evidence,
                "intent": None,
                "route": SAFETY_ESCALATION,
                "reply": self._reply(SAFETY_ESCALATION),
            }

        if episode["status"] == "SAFETY_ESCALATED":
            # Stored for audit above; never reaches intent classification.
            return {
                "duplicate": False,
                "contact_id": contact["contact_id"],
                "episode_id": episode["episode_id"],
                "message_id": message["message_id"],
                "safety_flagged": False,
                "safety_rule_id": None,
                "safety_evidence": None,
                "intent": None,
                "route": SAFETY_ESCALATION,
                "reply": self._reply(SAFETY_ESCALATION),
            }

        result = classify_intent(text, self._provider, language=language)
        route_name = route(result.intent, safety_flagged=False)
        return {
            "duplicate": False,
            "contact_id": contact["contact_id"],
            "episode_id": episode["episode_id"],
            "message_id": message["message_id"],
            "safety_flagged": False,
            "safety_rule_id": None,
            "safety_evidence": None,
            "intent": result.intent,
            "intent_evidence": result.evidence,
            "intent_confidence": result.confidence,
            "route": route_name,
            "reply": self._reply(route_name),
        }
