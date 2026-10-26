"""
Synthetic Voter Registry Module

Manages voter registration, credential authentication, and eligibility verification.
Uses Trie for instant prefix search and Trie autocomplete of voters and candidates.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.dsa.trie import Trie
from src.security.authentication import hash_password, verify_password
from src.storage.database import Database


class VoterRegistry:
    """Manages synthetic voter accounts and eligibility checks."""

    def __init__(self, db: Database):
        self.db = db
        self.search_trie = Trie()
        self._load_existing_voters()

    def _load_existing_voters(self) -> None:
        """Populate in-memory Trie from persistent SQLite."""
        conn = self.db._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT voter_id, name FROM voter_registry;")
            for row in cur.fetchall():
                self.search_trie.insert(row["voter_id"], {"name": row["name"]})
                self.search_trie.insert(row["name"], {"voter_id": row["voter_id"]})
        finally:
            conn.close()

    def register_voter(
        self, voter_id: str, name: str, password: str, eligible: bool = True, email: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Register a new synthetic voter with hashed password, salt, and unique email check."""
        if email:
            email = email.lower().strip()
            existing_email = self.db.get_voter_by_email(email)
            if existing_email:
                return False, f"Email address '{email}' is already registered"

        pwd_hash, salt = hash_password(password)
        success = self.db.register_voter(voter_id, name, pwd_hash, salt, eligible=eligible, email=email)
        if success:
            self.search_trie.insert(voter_id, {"name": name, "email": email})
            self.search_trie.insert(name, {"voter_id": voter_id})
            if email:
                self.search_trie.insert(email, {"voter_id": voter_id})
            self.db.log_audit("VOTER_REGISTERED", f"Registered voter {voter_id} ({name}, email={email})")
            return True, f"Voter '{voter_id}' registered successfully"
        return False, f"Voter ID '{voter_id}' is already registered"

    def authenticate_voter(self, identifier: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Authenticate a synthetic voter by voter_id or registered email."""
        voter = self.db.get_voter(identifier)
        if not voter and "@" in identifier:
            voter = self.db.get_voter_by_email(identifier)
        if not voter:
            return False, None, "Voter account not found in registry"

        if not verify_password(password, voter["password_hash"], voter["salt"]):
            return False, None, "Invalid password"

        if not voter["eligible"]:
            return False, None, "Voter is marked as ineligible for this election"

        return True, voter, "Authentication successful"

    def search_voters_by_prefix(self, prefix: str) -> List[Tuple[str, Any]]:
        """Instant prefix lookup using Trie."""
        return self.search_trie.get_words_with_prefix(prefix)
