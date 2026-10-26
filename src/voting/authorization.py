"""
Anonymous Voting Authorization Module

Implements the educational decoupled authorization workflow:
1. Authenticates synthetic voter & verifies eligibility.
2. Issues a single-use cryptographically random voting authorization token.
3. Records token_hash = sha256(token) in SQLite with UNIQUE(voter_id, election_id) constraint.
4. When voting, the ballot includes token_hash and candidate_id, completely omitting voter_id.
5. Consumes the authorization token atomically, preventing duplicate votes or replay attacks.
"""

from typing import Optional, Tuple
from src.security.authentication import generate_auth_token
from src.security.hashing import sha256_hash
from src.storage.database import Database


class VotingAuthorizationManager:
    """Manages single-use voting authorization tokens."""

    def __init__(self, db: Database, election_id: str):
        self.db = db
        self.election_id = election_id

    def issue_token(self, voter_id: str) -> Tuple[bool, Optional[str], str]:
        """
        Issue a single-use authorization token for an eligible voter.
        Enforces one token per voter per election.
        Returns (success, raw_token, message).
        """
        voter = self.db.get_voter(voter_id)
        if not voter:
            return False, None, "Voter not found"
        if not voter["eligible"]:
            return False, None, "Voter is ineligible"

        raw_token = generate_auth_token(32)
        token_hash = sha256_hash(raw_token)

        success = self.db.issue_authorization_token(token_hash, voter_id, self.election_id)
        if not success:
            return False, None, "Authorization token already issued for this voter in this election"

        self.db.log_audit(
            "AUTH_TOKEN_ISSUED",
            f"Issued voting token for voter {voter_id} (token_hash={token_hash[:8]}...)",
        )
        return True, raw_token, "Authorization token issued successfully"

    def redeem_token(self, raw_token: str) -> Tuple[bool, Optional[str], str]:
        """
        Atomically validate and consume single-use authorization token.
        Returns (valid, token_hash, message).
        """
        token_hash = sha256_hash(raw_token)
        consumed = self.db.consume_authorization_token(token_hash)
        if not consumed:
            return (
                False,
                None,
                "Invalid, expired, or already-consumed authorization token (Double-voting prevented)",
            )

        self.db.log_audit("AUTH_TOKEN_CONSUMED", f"Consumed token_hash {token_hash[:8]}...")
        return True, token_hash, "Authorization token consumed successfully"
