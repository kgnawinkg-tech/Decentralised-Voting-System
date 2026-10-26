"""
Duplicate Voting Prevention & Concurrency Tests
"""

import os
import tempfile
import threading
import pytest
from src.networking.node import Node


@pytest.fixture
def temp_node():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_node.db")
        node = Node(
            node_id="test_node",
            name="Test Node",
            host="127.0.0.1",
            port=5999,
            db_path=db_path,
        )
        yield node


def test_voter_registration_and_duplicate_prevention(temp_node):
    node = temp_node
    ok, msg = node.voter_registry.register_voter("voter_1", "Alice", "pass123")
    assert ok is True

    # Duplicate registration attempt
    ok2, msg2 = node.voter_registry.register_voter("voter_1", "Alice", "pass123")
    assert ok2 is False
    assert "already registered" in msg2.lower()


def test_single_use_token_and_double_voting_prevention(temp_node):
    node = temp_node
    node.voter_registry.register_voter("voter_2", "Bob", "pass123")

    # Issue token 1
    ok, token, _ = node.auth_manager.issue_token("voter_2")
    assert ok is True
    assert token is not None

    # Cannot issue another token for same voter in same election
    ok_dup, token_dup, _ = node.auth_manager.issue_token("voter_2")
    assert ok_dup is False
    assert token_dup is None

    # Cast ballot with valid token
    cast_ok, receipt, _ = node.submit_ballot_transaction("cand_1", token)
    assert cast_ok is True
    assert receipt["transaction_id"] is not None

    # Attempt to reuse the same token (Double voting attempt)
    cast_dup, _, dup_msg = node.submit_ballot_transaction("cand_2", token)
    assert cast_dup is False
    assert "double-voting prevented" in dup_msg.lower() or "rejected" in dup_msg.lower()


def test_concurrent_duplicate_voting_submissions(temp_node):
    node = temp_node
    node.voter_registry.register_voter("voter_concurrent", "Carol", "pass123")
    ok, token, _ = node.auth_manager.issue_token("voter_concurrent")
    assert ok is True

    results = []

    def attempt_vote(candidate_id):
        res = node.submit_ballot_transaction(candidate_id, token)
        results.append(res[0])

    # Spin up 5 concurrent threads attempting to spend the exact same token simultaneously
    threads = [threading.Thread(target=attempt_vote, args=(f"cand_{(i % 3) + 1}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Exactly ONE thread must succeed; all other 4 threads must fail!
    assert results.count(True) == 1
    assert results.count(False) == 4


def test_rejection_after_election_closed(temp_node):
    node = temp_node
    node.voter_registry.register_voter("voter_late", "Dave", "pass123")
    ok, token, _ = node.auth_manager.issue_token("voter_late")
    assert ok is True

    # Close election
    node.election.close_election()

    # Attempt to vote
    cast_ok, _, msg = node.submit_ballot_transaction("cand_1", token)
    assert cast_ok is False
    assert "closed" in msg.lower()


def test_invalid_candidate_rejection(temp_node):
    node = temp_node
    node.voter_registry.register_voter("voter_inv", "Eve", "pass123")
    ok, token, _ = node.auth_manager.issue_token("voter_inv")
    assert ok is True

    cast_ok, _, msg = node.submit_ballot_transaction("cand_nonexistent_999", token)
    assert cast_ok is False
    assert "invalid candidate" in msg.lower()
