"""Phase 0 clinical content: question registry, drug list, teaching cards.

All content is data (JSON under config/), validated here in code.
Invalid content fails closed with RegistryError - it is never silently
repaired or partially loaded.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Question:
    id: str
    type: str  # A (fixed categorical), B (voice then tap), C (nurse only)
    en_text: str
    ur_text: Optional[str]
    ur_status: str
    maps_to_fact: str
    required: bool
    options: Tuple[str, ...] = ()
    confirmation_source: Optional[str] = None
    nurse_check: Optional[str] = None

    @property
    def patient_askable(self) -> bool:
        return self.type in ("A", "B")


@dataclass(frozen=True)
class DrugList:
    version: str
    drugs: Tuple[Tuple[str, Tuple[str, ...]], ...]  # (generic, aliases)

    def find(self, text: str) -> Optional[str]:
        """Return the generic name for an alias match, else None (no guessing)."""
        needle = text.strip().casefold()
        for generic, aliases in self.drugs:
            if needle in [a.casefold() for a in aliases]:
                return generic
        return None


@dataclass(frozen=True)
class TeachingCard:
    guideline_id: str
    title: str
    source: str
    page: int
    status: str
    grading_table: Tuple[Dict, ...] = ()
    management_by_grade: Tuple[Tuple[str, str], ...] = ()
    cross_references: Tuple[str, ...] = ()
    nurse_checks: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def excerpts_curated(self) -> bool:
        return "PENDING" not in self.status


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError("cannot load {}: {}".format(path, exc))


def load_question_registry(path: Optional[Path] = None) -> List[Question]:
    data = _read_json(path or CONFIG_DIR / "question_registry.json")
    raw_questions = data.get("questions")
    if not isinstance(raw_questions, list) or not raw_questions:
        raise RegistryError("question registry has no questions")
    questions = []
    seen_ids = set()
    seen_facts = set()
    for raw in raw_questions:
        try:
            question = Question(
                id=raw["id"],
                type=raw["type"],
                en_text=raw["en_text"],
                ur_text=raw.get("ur_text"),
                ur_status=raw["ur_status"],
                maps_to_fact=raw["maps_to_fact"],
                required=bool(raw["required"]),
                options=tuple(raw.get("options", ())),
                confirmation_source=raw.get("confirmation_source"),
                nurse_check=raw.get("nurse_check"),
            )
        except KeyError as exc:
            raise RegistryError("question missing field {}".format(exc))
        if question.id in seen_ids:
            raise RegistryError("duplicate question id: " + question.id)
        if question.maps_to_fact in seen_facts:
            raise RegistryError(
                "duplicate maps_to_fact: " + question.maps_to_fact)
        if question.type not in ("A", "B", "C"):
            raise RegistryError("bad type for {}: {}".format(
                question.id, question.type))
        if not question.en_text.strip():
            raise RegistryError("empty en_text for " + question.id)
        if question.type == "A":
            if len(question.options) < 2:
                raise RegistryError(
                    "Type A question needs >=2 options: " + question.id)
            if "don't know" not in [o.casefold() for o in question.options]:
                raise RegistryError(
                    "Type A question needs an explicit Don't know option: "
                    + question.id)
        if question.type == "B" and not question.confirmation_source:
            raise RegistryError(
                "Type B question needs confirmation_source: " + question.id)
        if question.type == "C" and not (question.nurse_check or "").strip():
            raise RegistryError(
                "Type C question needs nurse_check text: " + question.id)
        seen_ids.add(question.id)
        seen_facts.add(question.maps_to_fact)
        questions.append(question)
    return questions


def get_question(question_id: str,
                 path: Optional[Path] = None) -> Question:
    for question in load_question_registry(path):
        if question.id == question_id:
            return question
    raise RegistryError("unknown question id: " + question_id)


def load_drug_list(path: Optional[Path] = None) -> DrugList:
    data = _read_json(path or CONFIG_DIR / "drug_list.json")
    raw_drugs = data.get("drugs")
    if not isinstance(raw_drugs, list) or not raw_drugs:
        raise RegistryError("drug list is empty")
    drugs = []
    for raw in raw_drugs:
        generic = (raw.get("generic") or "").strip()
        aliases = tuple(raw.get("aliases", ()))
        if not generic or not aliases:
            raise RegistryError("drug entry needs generic + aliases")
        drugs.append((generic, aliases))
    return DrugList(version=data.get("version", ""), drugs=tuple(drugs))


def load_teaching_card(guideline_id: str,
                       cards_dir: Optional[Path] = None) -> TeachingCard:
    directory = cards_dir or CONFIG_DIR / "teaching_cards"
    for path in sorted(directory.glob("*.json")):
        data = _read_json(path)
        if data.get("guideline_id") == guideline_id:
            try:
                return TeachingCard(
                    guideline_id=data["guideline_id"],
                    title=data["title"],
                    source=data["source"],
                    page=int(data["page"]),
                    status=data["status"],
                    grading_table=tuple(data.get("grading_table", ())),
                    management_by_grade=tuple(
                        sorted(data.get("management_by_grade", {}).items())),
                    cross_references=tuple(data.get("cross_references", ())),
                    nurse_checks=tuple(data.get("nurse_checks", ())),
                )
            except KeyError as exc:
                raise RegistryError(
                    "teaching card missing field {}: {}".format(exc, path))
    raise RegistryError("unknown guideline id: " + guideline_id)
