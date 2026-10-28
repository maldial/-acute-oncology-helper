import pytest

from app.storage.repository import OwnershipError, Repository, hash_sender


@pytest.fixture()
def repo():
    repository = Repository(":memory:")
    yield repository
    repository.close()


def test_sender_hash_is_deterministic_and_not_raw():
    hashed = hash_sender("+447700900123")
    assert hashed == hash_sender("+447700900123")
    assert "+447700900123" not in hashed
    assert len(hashed) == 64


def test_contact_ids_are_sequential_and_unique(repo):
    first = repo.get_or_create_contact(hash_sender("sender-a"))
    second = repo.get_or_create_contact(hash_sender("sender-b"))
    assert first["contact_id"] == "C0001"
    assert second["contact_id"] == "C0002"


def test_same_sender_reuses_contact(repo):
    first = repo.get_or_create_contact(hash_sender("sender-a"))
    second = repo.get_or_create_contact(hash_sender("sender-a"))
    assert first["contact_id"] == second["contact_id"]


def test_episode_reused_within_inactivity_window(repo):
    contact = repo.get_or_create_contact(hash_sender("sender-a"))
    first = repo.get_or_create_episode(contact["contact_id"])
    second = repo.get_or_create_episode(contact["contact_id"])
    assert first["episode_id"] == second["episode_id"] == "E0001"


def test_force_new_episode(repo):
    contact = repo.get_or_create_contact(hash_sender("sender-a"))
    first = repo.get_or_create_episode(contact["contact_id"])
    second = repo.get_or_create_episode(contact["contact_id"], force_new=True)
    assert first["episode_id"] != second["episode_id"]


def test_cross_contact_episode_read_rejected(repo):
    alice = repo.get_or_create_contact(hash_sender("alice"))
    bob = repo.get_or_create_contact(hash_sender("bob"))
    bobs_episode = repo.get_or_create_episode(bob["contact_id"])
    with pytest.raises(OwnershipError):
        repo.get_episode(alice["contact_id"], bobs_episode["episode_id"])
    with pytest.raises(OwnershipError):
        repo.get_history(alice["contact_id"], bobs_episode["episode_id"])


def test_save_message_rejects_other_contacts_episode(repo):
    alice = repo.get_or_create_contact(hash_sender("alice"))
    bob = repo.get_or_create_contact(hash_sender("bob"))
    bobs_episode = repo.get_or_create_episode(bob["contact_id"])
    with pytest.raises(OwnershipError):
        repo.save_message(
            alice["contact_id"], bobs_episode["episode_id"],
            "inbound", "hello",
        )


def test_message_ids_sequential(repo):
    contact = repo.get_or_create_contact(hash_sender("alice"))
    episode = repo.get_or_create_episode(contact["contact_id"])
    first = repo.save_message(
        contact["contact_id"], episode["episode_id"], "inbound", "one")
    assert first["message_id"] == "M0001"
    second = repo.save_message(
        contact["contact_id"], episode["episode_id"], "inbound", "two")
    assert second["message_id"] == "M0002"


def test_history_returns_episode_messages_in_order(repo):
    contact = repo.get_or_create_contact(hash_sender("alice"))
    episode = repo.get_or_create_episode(contact["contact_id"])
    repo.save_message(
        contact["contact_id"], episode["episode_id"], "inbound", "one")
    repo.save_message(
        contact["contact_id"], episode["episode_id"], "inbound", "two")
    history = repo.get_history(contact["contact_id"], episode["episode_id"])
    assert [m["text"] for m in history] == ["one", "two"]


def test_safety_escalation_first_trigger_wins(repo):
    contact = repo.get_or_create_contact(hash_sender("alice"))
    episode = repo.get_or_create_episode(contact["contact_id"])
    assert repo.mark_safety_escalated(
        episode["episode_id"], "M0001", "fever", "DEMO_FEVER") is True
    assert repo.mark_safety_escalated(
        episode["episode_id"], "M0002", "chest pain", "DEMO_CHEST_PAIN"
    ) is False
    stored = repo.get_episode(contact["contact_id"], episode["episode_id"])
    assert stored["status"] == "SAFETY_ESCALATED"
    assert stored["safety_message_id"] == "M0001"
    assert stored["safety_evidence"] == "fever"
    assert stored["safety_rule_id"] == "DEMO_FEVER"


def test_escalated_episode_pins_contact_until_closed(repo):
    contact = repo.get_or_create_contact(hash_sender("alice"))
    episode = repo.get_or_create_episode(contact["contact_id"])
    repo.mark_safety_escalated(
        episode["episode_id"], "M0001", "fever", "DEMO_FEVER")
    pinned = repo.get_or_create_episode(contact["contact_id"], force_new=True)
    assert pinned["episode_id"] == episode["episode_id"]
    repo.close_episode(episode["episode_id"])
    fresh = repo.get_or_create_episode(contact["contact_id"])
    assert fresh["episode_id"] != episode["episode_id"]
    assert fresh["status"] == "OPEN"


def test_external_message_id_dedup_lookup(repo):
    contact = repo.get_or_create_contact(hash_sender("alice"))
    episode = repo.get_or_create_episode(contact["contact_id"])
    saved = repo.save_message(
        contact["contact_id"], episode["episode_id"], "inbound", "hi",
        external_message_id="wamid-123",
    )
    found = repo.find_by_external_id("wamid-123")
    assert found is not None
    assert found["message_id"] == saved["message_id"]
    assert repo.find_by_external_id("wamid-unknown") is None
