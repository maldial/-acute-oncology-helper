"""Safety Gate: independent deterministic check on every message.

Rules come from config/safety_rules.json (substring, case-insensitive).
An optional extra flagger (e.g. a future Llama Guard call) may only ADD a
flag — it can never clear a deterministic match.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "safety_rules.json"


@dataclass(frozen=True)
class SafetyResult:
    flagged: bool
    rule_id: Optional[str] = None
    evidence: Optional[str] = None  # verbatim span from the patient text


@dataclass(frozen=True)
class SafetyRule:
    rule_id: str
    label: str
    phrases: Tuple[str, ...]


def load_rules(config_path: Optional[Path] = None) -> List[SafetyRule]:
    path = config_path or CONFIG_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        SafetyRule(
            rule_id=rule["rule_id"],
            label=rule.get("label", rule["rule_id"]),
            phrases=tuple(rule["phrases"]),
        )
        for rule in data["rules"]
    ]


def _verbatim_span(text: str, phrase_fold: str) -> Optional[str]:
    index = text.casefold().find(phrase_fold)
    if index < 0:
        return None
    return text[index:index + len(phrase_fold)]


class SafetyGate:
    def __init__(self, rules: Optional[List[SafetyRule]] = None) -> None:
        self._rules = rules if rules is not None else load_rules()

    @property
    def rules(self) -> List[SafetyRule]:
        return list(self._rules)

    def check(
        self,
        text: str,
        extra_flagger: Optional[Callable[[str], Optional[Tuple[str, str]]]] = None,
    ) -> SafetyResult:
        for rule in self._rules:
            for phrase in rule.phrases:
                span = _verbatim_span(text, phrase.casefold())
                if span is not None:
                    return SafetyResult(
                        flagged=True, rule_id=rule.rule_id, evidence=span
                    )
        if extra_flagger is not None:
            extra = extra_flagger(text)
            if extra is not None:
                rule_id, evidence = extra
                return SafetyResult(
                    flagged=True, rule_id=rule_id, evidence=evidence
                )
        return SafetyResult(flagged=False)
