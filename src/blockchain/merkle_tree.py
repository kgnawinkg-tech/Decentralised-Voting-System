"""
DSA Module 21: Merkle Tree (Binary Hash Tree & Inclusion Proofs)

Complexity:
- Tree Construction: Time O(N), Space O(N)
- Proof Generation: Time O(log N), Proof Size O(log N)
- Proof Verification: Time O(log N), Space O(1)

Integration:
- Anchors transaction sets in block headers via a single 32-byte Merkle Root.
- Provides cryptographic inclusion receipts to voters, allowing any synthetic voter
  to mathematically verify their ballot's presence in a mined block without downloading
  the entire block or reading other voters' ballots.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.security.hashing import sha256_hash


class MerkleProofStep:
    """Represents a single step in a Merkle inclusion proof."""

    def __init__(self, sibling_hash: str, is_right: bool):
        self.sibling_hash: str = sibling_hash
        self.is_right: bool = is_right  # True if sibling was on the right

    def to_dict(self) -> Dict[str, Any]:
        return {"sibling_hash": self.sibling_hash, "is_right": self.is_right}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MerkleProofStep":
        return cls(sibling_hash=d["sibling_hash"], is_right=d["is_right"])


class MerkleTree:
    """
    Binary Merkle Tree implementation.
    Handles empty, single-leaf, odd-leaf, and even-leaf transaction sets.
    """

    EMPTY_ROOT: str = "0" * 64

    def __init__(self, raw_leaves: Optional[List[str]] = None):
        self.leaves: List[str] = []
        self.levels: List[List[str]] = []
        self.root: str = self.EMPTY_ROOT

        if raw_leaves:
            self.build(raw_leaves)

    def _hash_pair(self, left: str, right: str) -> str:
        """Hash two child nodes in deterministic order."""
        return sha256_hash(left + right)

    def build(self, raw_leaves: List[str]) -> str:
        """
        Build the Merkle tree from a list of leaf hashes or strings.
        Returns the calculated Merkle root.
        """
        if not raw_leaves:
            self.leaves = []
            self.levels = [[]]
            self.root = self.EMPTY_ROOT
            return self.root

        # Ensure leaves are SHA-256 hashes
        self.leaves = [
            leaf if len(leaf) == 64 and all(c in "0123456789abcdef" for c in leaf.lower())
            else sha256_hash(leaf)
            for leaf in raw_leaves
        ]

        current_level = list(self.leaves)
        self.levels = [current_level]

        while len(current_level) > 1:
            next_level: List[str] = []
            n = len(current_level)

            for i in range(0, n, 2):
                left = current_level[i]
                if i + 1 < n:
                    right = current_level[i + 1]
                else:
                    # Odd-leaf handling: duplicate the last leaf to maintain binary structure
                    right = left
                parent = self._hash_pair(left, right)
                next_level.append(parent)

            self.levels.append(next_level)
            current_level = next_level

        self.root = self.levels[-1][0]
        return self.root

    def get_proof(self, leaf_index: int) -> List[MerkleProofStep]:
        """
        Generate inclusion proof for the leaf at leaf_index.
        Returns list of MerkleProofStep objects from leaf to root.
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError(f"Leaf index {leaf_index} out of bounds (0..{len(self.leaves) - 1})")

        proof: List[MerkleProofStep] = []
        idx = leaf_index

        for level in self.levels[:-1]:
            # Determine sibling index
            if idx % 2 == 0:
                # idx is left child, sibling is right
                if idx + 1 < len(level):
                    sibling = level[idx + 1]
                else:
                    sibling = level[idx]  # Duplicated odd leaf
                proof.append(MerkleProofStep(sibling_hash=sibling, is_right=True))
            else:
                # idx is right child, sibling is left
                sibling = level[idx - 1]
                proof.append(MerkleProofStep(sibling_hash=sibling, is_right=False))

            idx = idx // 2

        return proof

    @classmethod
    def verify_proof(cls, leaf_hash: str, proof: List[MerkleProofStep], expected_root: str) -> bool:
        """
        Verify a Merkle inclusion proof against an expected Merkle root.
        Returns True if proof is valid and matches root, False otherwise.
        """
        if not proof:
            return leaf_hash == expected_root

        current = leaf_hash
        for step in proof:
            if step.is_right:
                current = sha256_hash(current + step.sibling_hash)
            else:
                current = sha256_hash(step.sibling_hash + current)

        return current == expected_root
