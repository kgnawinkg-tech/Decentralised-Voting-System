"""
Security, Signatures & Ballot Privacy Tests
"""

import os
import tempfile
import pytest
from src.security.authentication import hash_password, verify_password
from src.security.digital_signatures import KeyPair, verify_signature, create_signed_envelope, verify_signed_envelope
from src.security.hashing import sha256_hash, canonical_json_bytes
from src.storage.database import Database


def test_password_hashing_and_salting():
    pwd = "SecretPassword123"
    hash1, salt1 = hash_password(pwd)
    hash2, salt2 = hash_password(pwd)

    # Different salts yield different hashes (rainbow table resistance)
    assert salt1 != salt2
    assert hash1 != hash2

    # Verification works
    assert verify_password(pwd, hash1, salt1) is True
    assert verify_password("WrongPassword", hash1, salt1) is False


def test_ecdsa_signatures_and_envelope_integrity():
    kp = KeyPair.generate()
    payload = {"from": "node_a", "to": "node_b", "action": "PROPOSE_BLOCK", "block_index": 5}
    envelope = create_signed_envelope(kp, payload, sender_id="node_a")

    assert verify_signed_envelope(envelope) is True

    # Tamper with envelope payload
    tampered_envelope = dict(envelope)
    tampered_envelope["payload"] = dict(payload)
    tampered_envelope["payload"]["block_index"] = 6
    assert verify_signed_envelope(tampered_envelope) is False


def test_database_schema_ballot_privacy():
    """
    CRITICAL BALLOT PRIVACY TEST:
    Verify that accepted ballots stored in the database DO NOT contain voter_id!
    The ballot table must decouple voter identity from candidate choice.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "privacy_test.db"))

        # Inspect table columns for accepted_ballots
        conn = db._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(accepted_ballots);")
            columns = [col["name"] for col in cur.fetchall()]
            # Must NOT contain voter_id or voter_name
            assert "voter_id" not in columns
            assert "voter_name" not in columns
            assert "transaction_id" in columns
            assert "candidate_id" in columns
            assert "token_hash" in columns
        finally:
            conn.close()
