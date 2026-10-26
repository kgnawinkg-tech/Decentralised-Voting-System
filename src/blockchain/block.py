"""
Blockchain Block Data Structure

Represents an immutable block on the blockchain containing verified voting transactions.
Implements Doubly Linked List pointers for in-memory navigation, along with
cryptographic SHA-256 previous-hash and Merkle-root linkage.
"""

import time
from typing import Any, Dict, List, Optional
from src.blockchain.merkle_tree import MerkleTree
from src.security.hashing import sha256_hash, canonical_json_bytes


class Block:
    """
    A single block in the educational blockchain.
    
    Fields hashed into current_hash:
    - index: integer sequence number
    - timestamp: float Unix epoch
    - previous_hash: 64-char hex SHA-256 of preceding block
    - merkle_root: 64-char hex SHA-256 Merkle root of committed transactions
    - node_id: ID of node that mined/proposed this block
    - shard_id: ID of shard partition
    - version: block schema version (e.g., 1)
    """

    def __init__(
        self,
        index: int,
        transactions: List[Dict[str, Any]],
        previous_hash: str,
        timestamp: Optional[float] = None,
        node_id: str = "node_a",
        shard_id: str = "shard_default",
        version: int = 1,
        merkle_root: Optional[str] = None,
        current_hash: Optional[str] = None,
    ):
        self.index: int = index
        self.timestamp: float = timestamp if timestamp is not None else time.time()
        self.transactions: List[Dict[str, Any]] = list(transactions)
        self.previous_hash: str = previous_hash
        self.node_id: str = node_id
        self.shard_id: str = shard_id
        self.version: int = version

        # Build Merkle tree from transaction hashes
        if merkle_root is not None:
            self.merkle_root = merkle_root
            self._merkle_tree = MerkleTree()
            self._merkle_tree.root = merkle_root
        else:
            tx_hashes = [sha256_hash(tx) for tx in self.transactions]
            self._merkle_tree = MerkleTree(tx_hashes)
            self.merkle_root = self._merkle_tree.root

        # Doubly linked list pointers for in-memory traversal
        self.prev_node: Optional["Block"] = None
        self.next_node: Optional["Block"] = None

        # Calculate block hash
        self.current_hash: str = (
            current_hash if current_hash is not None else self.calculate_hash()
        )

    def header_dict(self) -> Dict[str, Any]:
        """Return canonical dictionary of block header fields included in block hash."""
        return {
            "index": self.index,
            "timestamp": round(self.timestamp, 4),
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "node_id": self.node_id,
            "shard_id": self.shard_id,
            "version": self.version,
        }

    def calculate_hash(self) -> str:
        """Compute deterministic SHA-256 hash of block header."""
        return sha256_hash(self.header_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete block to dictionary for API transmission and database storage."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "merkle_root": self.merkle_root,
            "node_id": self.node_id,
            "shard_id": self.shard_id,
            "version": self.version,
            "transactions": self.transactions,
            "transaction_count": len(self.transactions),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Reconstruct Block from dictionary representation."""
        return cls(
            index=data["index"],
            transactions=data.get("transactions", []),
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            node_id=data.get("node_id", "node_a"),
            shard_id=data.get("shard_id", "shard_default"),
            version=data.get("version", 1),
            merkle_root=data.get("merkle_root"),
            current_hash=data.get("current_hash"),
        )

    def get_merkle_tree(self) -> MerkleTree:
        """Get or rebuild the block's Merkle tree."""
        if not hasattr(self, "_merkle_tree") or not self._merkle_tree.leaves:
            tx_hashes = [sha256_hash(tx) for tx in self.transactions]
            self._merkle_tree = MerkleTree(tx_hashes)
        return self._merkle_tree

    def __repr__(self) -> str:
        return (
            f"Block(idx={self.index}, hash={self.current_hash[:8]}..., "
            f"prev={self.previous_hash[:8]}..., txs={len(self.transactions)}, node={self.node_id})"
        )
