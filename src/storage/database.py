"""
Independent Node SQLite Storage Engine

Manages persistent local SQLite storage for each node.
Enforces ACID atomic transactions, WAL journaling, and strict UNIQUE constraints
to prevent duplicate voting, duplicate registrations, and token double-spending.
Never shares database files between different physical or simulated nodes.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple


class Database:
    """Manages independent local SQLite database for a node."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection with WAL journal mode and foreign keys enabled."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for atomic database transaction with automatic commit/rollback."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema with tables and uniqueness constraints."""
        with self.transaction() as cur:
            # 1. Blocks Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    block_index INTEGER PRIMARY KEY,
                    current_hash TEXT UNIQUE NOT NULL,
                    previous_hash TEXT NOT NULL,
                    merkle_root TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    node_id TEXT NOT NULL,
                    shard_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    raw_json TEXT NOT NULL
                );
            """)

            # 2. Synthetic Voter Registry Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS voter_registry (
                    voter_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    eligible INTEGER DEFAULT 1,
                    registered_at REAL NOT NULL,
                    email TEXT UNIQUE
                );
            """)
            try:
                cur.execute("ALTER TABLE voter_registry ADD COLUMN email TEXT;")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_voter_email ON voter_registry(email);")
            except sqlite3.OperationalError:
                pass  # column or index already exists

            # 3. Blinded / Decoupled Single-Use Voting Authorization Tokens Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS voting_authorizations (
                    token_hash TEXT PRIMARY KEY,
                    voter_id TEXT NOT NULL,
                    election_id TEXT NOT NULL,
                    issued_at REAL NOT NULL,
                    is_spent INTEGER DEFAULT 0,
                    spent_at REAL,
                    FOREIGN KEY(voter_id) REFERENCES voter_registry(voter_id),
                    UNIQUE(voter_id, election_id) -- Only one authorization token per voter per election!
                );
            """)

            # 4. Accepted Ballots Table (Stored anonymously - decoupled from voter_id!)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accepted_ballots (
                    transaction_id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL, -- Prevents token double-spending!
                    block_index INTEGER,
                    committed_at REAL NOT NULL,
                    raw_json TEXT NOT NULL
                );
            """)

            # 5. Shard Partition Records Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shard_records (
                    record_key TEXT PRIMARY KEY,
                    shard_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
            """)

            # 6. Local Node Audit Log Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp REAL NOT NULL
                );
            """)

    # --- Block Operations ---
    def save_block(self, block_dict: Dict[str, Any]) -> None:
        """Persist block to database."""
        with self.transaction() as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO blocks 
                (block_index, current_hash, previous_hash, merkle_root, timestamp, node_id, shard_id, version, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block_dict["index"],
                    block_dict["current_hash"],
                    block_dict["previous_hash"],
                    block_dict["merkle_root"],
                    block_dict["timestamp"],
                    block_dict.get("node_id", "node_a"),
                    block_dict.get("shard_id", "shard_default"),
                    block_dict.get("version", 1),
                    json.dumps(block_dict),
                ),
            )

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        """Fetch all blocks in index sequence."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT raw_json FROM blocks ORDER BY block_index ASC;")
            rows = cur.fetchall()
            return [json.loads(row["raw_json"]) for row in rows]
        finally:
            conn.close()

    def get_block_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT raw_json FROM blocks WHERE block_index = ?;", (index,))
            row = cur.fetchone()
            return json.loads(row["raw_json"]) if row else None
        finally:
            conn.close()

    # --- Voter Operations ---
    def register_voter(
        self,
        voter_id: str,
        name: str,
        password_hash: str,
        salt: str,
        eligible: bool = True,
        email: Optional[str] = None,
    ) -> bool:
        """Register voter. Returns True if successful, False if voter or email already exists."""
        import time
        try:
            with self.transaction() as cur:
                cur.execute(
                    """
                    INSERT INTO voter_registry (voter_id, name, password_hash, salt, eligible, registered_at, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (voter_id, name, password_hash, salt, 1 if eligible else 0, time.time(), email),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_voter(self, voter_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM voter_registry WHERE voter_id = ?;", (voter_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_voter_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM voter_registry WHERE LOWER(email) = ?;", (email.lower().strip(),))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_voters(self) -> List[Dict[str, Any]]:
        """Return all registered voters (excluding sensitive password/salt fields)."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT voter_id, name, email, eligible, registered_at FROM voter_registry ORDER BY registered_at DESC;"
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # --- Voting Authorization Token Operations ---
    def issue_authorization_token(self, token_hash: str, voter_id: str, election_id: str) -> bool:
        """
        Record newly issued single-use voting authorization token.
        Fails if voter already received a token for this election.
        """
        import time
        try:
            with self.transaction() as cur:
                cur.execute(
                    """
                    INSERT INTO voting_authorizations (token_hash, voter_id, election_id, issued_at, is_spent)
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (token_hash, voter_id, election_id, time.time()),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def consume_authorization_token(self, token_hash: str) -> bool:
        """
        Atomically mark token as spent.
        Returns True if token was valid and unspent, False if already spent or nonexistent.
        """
        import time
        with self.transaction() as cur:
            cur.execute(
                """
                UPDATE voting_authorizations
                SET is_spent = 1, spent_at = ?
                WHERE token_hash = ? AND is_spent = 0
                """,
                (time.time(), token_hash),
            )
            return cur.rowcount > 0

    def get_authorization_by_voter(self, voter_id: str, election_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM voting_authorizations WHERE voter_id = ? AND election_id = ?;",
                (voter_id, election_id),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # --- Ballot Operations ---
    def record_accepted_ballot(
        self, transaction_id: str, candidate_id: str, token_hash: str, raw_json: str, block_index: Optional[int] = None
    ) -> bool:
        """
        Atomically record accepted ballot.
        Fails if transaction_id or token_hash was already committed (duplicate detection).
        """
        import time
        try:
            with self.transaction() as cur:
                cur.execute(
                    """
                    INSERT INTO accepted_ballots (transaction_id, candidate_id, token_hash, block_index, committed_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (transaction_id, candidate_id, token_hash, block_index, time.time(), raw_json),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def save_accepted_ballot(self, tx_dict: Dict[str, Any]) -> bool:
        """Convenience method to save accepted ballot transaction."""
        import json
        tx_id = tx_dict.get("transaction_id", "")
        candidate_id = tx_dict.get("candidate_id", "")
        token_hash = tx_dict.get("token_hash", "")
        block_index = tx_dict.get("block_index")
        return self.record_accepted_ballot(
            tx_id, candidate_id, token_hash, json.dumps(tx_dict, sort_keys=True), block_index
        )

    def get_accepted_ballots(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT raw_json FROM accepted_ballots ORDER BY committed_at ASC;")
            rows = cur.fetchall()
            return [json.loads(row["raw_json"]) for row in rows]
        finally:
            conn.close()

    # --- Shard Operations ---
    def save_shard_record(self, key: str, shard_id: str, record_type: str, payload: str) -> None:
        import time
        with self.transaction() as cur:
            cur.execute(
                """
                INSERT OR REPLACE INTO shard_records (record_key, shard_id, record_type, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, shard_id, record_type, payload, time.time()),
            )

    def get_shard_records(self, shard_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if shard_id:
                cur.execute("SELECT * FROM shard_records WHERE shard_id = ?;", (shard_id,))
            else:
                cur.execute("SELECT * FROM shard_records;")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # --- Audit Operations ---
    def log_audit(self, event_type: str, details: str) -> None:
        import time
        with self.transaction() as cur:
            cur.execute(
                "INSERT INTO audit_logs (event_type, details, timestamp) VALUES (?, ?, ?);",
                (event_type, details, time.time()),
            )

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM audit_logs ORDER BY timestamp ASC;")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
