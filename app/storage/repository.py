"""SQLite repository: contacts, episodes, messages.

Invariants:
- Sender identifiers are stored only as SHA-256 hashes, never raw.
- Internal pseudonymous IDs: C0001 (contact), E0001 (episode), M0001 (message),
  issued from atomic counters.
- Every read/write checks contact/episode ownership; mismatches raise.
- A SAFETY_ESCALATED episode pins the contact: no new episode is opened
  until a developer manually closes it (scripts/close_episode.py).
"""
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

EPISODE_INACTIVITY_SECONDS = 30 * 60

SCHEMA = """
CREATE TABLE IF NOT EXISTS id_counters (
    name TEXT PRIMARY KEY,
    next_value INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
    contact_id TEXT PRIMARY KEY,
    sender_hash TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS episodes (
    episode_id TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL REFERENCES contacts(contact_id),
    status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TEXT NOT NULL,
    last_message_at TEXT NOT NULL,
    closed_at TEXT,
    safety_message_id TEXT,
    safety_evidence TEXT,
    safety_rule_id TEXT,
    safety_triggered_at TEXT
);
CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL REFERENCES contacts(contact_id),
    episode_id TEXT NOT NULL REFERENCES episodes(episode_id),
    direction TEXT NOT NULL,
    text TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    created_at TEXT NOT NULL,
    safety_flag INTEGER NOT NULL DEFAULT 0,
    safety_evidence TEXT,
    matched_rule_id TEXT,
    external_message_id TEXT UNIQUE
);
"""


def hash_sender(sender_id: str) -> str:
    return hashlib.sha256(sender_id.encode("utf-8")).hexdigest()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class OwnershipError(ValueError):
    """Raised when a contact/episode pair does not match stored ownership."""


class Repository:
    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    # -- IDs -----------------------------------------------------------------
    def next_id(self, prefix: str) -> str:
        with self._conn:  # atomic counter increment
            row = self._conn.execute(
                "SELECT next_value FROM id_counters WHERE name = ?", (prefix,)
            ).fetchone()
            value = row["next_value"] if row else 1
            if row:
                self._conn.execute(
                    "UPDATE id_counters SET next_value = ? WHERE name = ?",
                    (value + 1, prefix),
                )
            else:
                self._conn.execute(
                    "INSERT INTO id_counters (name, next_value) VALUES (?, ?)",
                    (prefix, value + 1),
                )
        return "{}{:04d}".format(prefix, value)

    # -- contacts -------------------------------------------------------------
    def get_or_create_contact(self, sender_hash: str) -> Dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM contacts WHERE sender_hash = ?", (sender_hash,)
        ).fetchone()
        if row:
            return dict(row)
        contact_id = self.next_id("C")
        now = utcnow_iso()
        with self._conn:
            self._conn.execute(
                "INSERT INTO contacts (contact_id, sender_hash, created_at)"
                " VALUES (?, ?, ?)",
                (contact_id, sender_hash, now),
            )
        return {"contact_id": contact_id, "sender_hash": sender_hash,
                "created_at": now}

    # -- episodes --------------------------------------------------------------
    def _latest_episode(self, contact_id: str) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM episodes WHERE contact_id = ?"
            " ORDER BY last_message_at DESC, episode_id DESC LIMIT 1",
            (contact_id,),
        ).fetchone()

    def get_or_create_episode(
        self, contact_id: str, force_new: bool = False
    ) -> Dict[str, Any]:
        latest = self._latest_episode(contact_id)
        if latest is not None and latest["status"] == "SAFETY_ESCALATED":
            # Escalation pins the episode: it stays put until manually closed.
            return dict(latest)
        if latest is not None and not force_new:
            last = datetime.fromisoformat(latest["last_message_at"])
            age = (datetime.now(timezone.utc) - last).total_seconds()
            if age < EPISODE_INACTIVITY_SECONDS and latest["status"] == "OPEN":
                return dict(latest)
        episode_id = self.next_id("E")
        now = utcnow_iso()
        with self._conn:
            self._conn.execute(
                "INSERT INTO episodes (episode_id, contact_id, status,"
                " created_at, last_message_at)"
                " VALUES (?, ?, 'OPEN', ?, ?)",
                (episode_id, contact_id, now, now),
            )
        return {"episode_id": episode_id, "contact_id": contact_id,
                "status": "OPEN", "created_at": now, "last_message_at": now}

    def get_episode(self, contact_id: str, episode_id: str) -> Dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM episodes WHERE episode_id = ?", (episode_id,)
        ).fetchone()
        if row is None or row["contact_id"] != contact_id:
            raise OwnershipError("episode does not belong to contact")
        return dict(row)

    def touch_episode(self, episode_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE episodes SET last_message_at = ? WHERE episode_id = ?",
                (utcnow_iso(), episode_id),
            )

    def mark_safety_escalated(
        self, episode_id: str, message_id: str, evidence: str, rule_id: str
    ) -> bool:
        """Enter SAFETY_ESCALATED permanently. First trigger wins.

        Returns True if this call performed the transition, False if the
        episode was already escalated (existing trigger data preserved).
        """
        now = utcnow_iso()
        with self._conn:
            cursor = self._conn.execute(
                "UPDATE episodes SET status = 'SAFETY_ESCALATED',"
                " safety_message_id = ?, safety_evidence = ?,"
                " safety_rule_id = ?, safety_triggered_at = ?"
                " WHERE episode_id = ? AND status != 'SAFETY_ESCALATED'",
                (message_id, evidence, rule_id, now, episode_id),
            )
        return cursor.rowcount == 1

    def close_episode(self, episode_id: str) -> None:
        """Manual developer-only close (used after safety review)."""
        with self._conn:
            self._conn.execute(
                "UPDATE episodes SET status = 'CLOSED', closed_at = ?"
                " WHERE episode_id = ?",
                (utcnow_iso(), episode_id),
            )

    # -- messages ---------------------------------------------------------------
    def find_by_external_id(
        self, external_message_id: str
    ) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT * FROM messages WHERE external_message_id = ?",
            (external_message_id,),
        ).fetchone()
        return dict(row) if row else None

    def save_message(
        self,
        contact_id: str,
        episode_id: str,
        direction: str,
        text: str,
        language: str = "en",
        external_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.get_episode(contact_id, episode_id)  # ownership check
        message_id = self.next_id("M")
        now = utcnow_iso()
        with self._conn:
            self._conn.execute(
                "INSERT INTO messages (message_id, contact_id, episode_id,"
                " direction, text, language, created_at, external_message_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (message_id, contact_id, episode_id, direction, text,
                 language, now, external_message_id),
            )
            self._conn.execute(
                "UPDATE episodes SET last_message_at = ? WHERE episode_id = ?",
                (now, episode_id),
            )
        return {"message_id": message_id, "contact_id": contact_id,
                "episode_id": episode_id, "direction": direction,
                "text": text, "language": language, "created_at": now}

    def mark_message_safety(
        self, message_id: str, evidence: str, rule_id: str
    ) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE messages SET safety_flag = 1, safety_evidence = ?,"
                " matched_rule_id = ? WHERE message_id = ?",
                (evidence, rule_id, message_id),
            )

    def get_history(
        self, contact_id: str, episode_id: str
    ) -> List[Dict[str, Any]]:
        self.get_episode(contact_id, episode_id)  # ownership check
        rows = self._conn.execute(
            "SELECT * FROM messages WHERE contact_id = ? AND episode_id = ?"
            " ORDER BY created_at, message_id",
            (contact_id, episode_id),
        ).fetchall()
        return [dict(row) for row in rows]
