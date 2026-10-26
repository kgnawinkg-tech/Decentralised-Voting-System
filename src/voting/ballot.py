"""
Ballot & Transaction Representation Module

Encapsulates cast ballots, transaction envelope creation, and voter inclusion receipts.
Never includes voter identity or credentials inside the ballot transaction.
"""

import time
from typing import Any, Dict, List, Optional
from src.security.hashing import sha256_hash


class Ballot:
    """Represents a committed ballot transaction."""

    def __init__(
        self,
        candidate_id: str,
        token_hash: str,
        timestamp: Optional[float] = None,
        transaction_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.candidate_id: str = candidate_id
        self.token_hash: str = token_hash
        self.timestamp: float = timestamp if timestamp is not None else time.time()
        self.metadata: Dict[str, Any] = metadata if metadata else {}

        # Transaction ID is deterministic SHA-256 hash of core ballot fields
        self.transaction_id: str = (
            transaction_id if transaction_id else self.calculate_transaction_id()
        )

    def calculate_transaction_id(self) -> str:
        """Calculate deterministic transaction ID."""
        data = {
            "candidate_id": self.candidate_id,
            "token_hash": self.token_hash,
            "timestamp": round(self.timestamp, 4),
        }
        return sha256_hash(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ballot to transaction dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "candidate_id": self.candidate_id,
            "token_hash": self.token_hash,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ballot":
        return cls(
            candidate_id=data["candidate_id"],
            token_hash=data["token_hash"],
            timestamp=data.get("timestamp"),
            transaction_id=data.get("transaction_id"),
            metadata=data.get("metadata"),
        )


class BallotReceipt:
    """Verifiable cryptographic receipt issued to a voter after block inclusion."""

    def __init__(
        self,
        transaction_id: str,
        block_index: int,
        block_hash: str,
        merkle_root: str,
        merkle_proof: List[Dict[str, Any]],
        timestamp: float,
    ):
        self.transaction_id = transaction_id
        self.block_index = block_index
        self.block_hash = block_hash
        self.merkle_root = merkle_root
        self.merkle_proof = merkle_proof
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "block_index": self.block_index,
            "block_hash": self.block_hash,
            "merkle_root": self.merkle_root,
            "merkle_proof": self.merkle_proof,
            "timestamp": self.timestamp,
            "verified": True,
        }
