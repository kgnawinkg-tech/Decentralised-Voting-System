"""
DSA Module 15: Consistent Hashing Ring with Virtual Nodes

Complexity:
- Time:
  - Add Node: O(R * log(N * R)) where R is virtual replicas, N is physical nodes
  - Remove Node: O(R * log(N * R))
  - Get Node (Route): O(log(N * R)) using binary search on the ring
- Space: O(N * R) on the ring

Integration:
- Core distributed record partitioning engine!
  Routes synthetic voter records, ballot submissions, and shard data to Computer A (Node A),
  Computer B (Node B), or Computer C (Node C) deterministically using SHA-256.
  Calculates exact record migrations when nodes join or leave the network.
"""

import bisect
import hashlib
from typing import Dict, List, Optional, Set, Tuple


class ConsistentHashingRing:
    """
    Consistent Hashing ring with virtual nodes using cryptographic SHA-256.
    Ensures minimal record movement upon node addition or failure.
    """

    def __init__(self, virtual_nodes: int = 50):
        if virtual_nodes < 1:
            raise ValueError("Virtual nodes must be at least 1")
        self.virtual_nodes: int = virtual_nodes
        # Sorted list of hash integers on the ring [0, 2^256 - 1]
        self.ring: List[int] = []
        # Mapping from hash integer -> physical node ID
        self.hash_to_node: Dict[int, str] = {}
        # Set of active physical node IDs
        self.nodes: Set[str] = set()

    def _hash(self, key: str) -> int:
        """Deterministic cryptographic SHA-256 integer hash."""
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return int(digest, 16)

    def add_node(self, node_id: str) -> None:
        """Add physical node to the ring with its virtual replica tokens."""
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)

        for i in range(self.virtual_nodes):
            replica_key = f"{node_id}#vn_{i}"
            h = self._hash(replica_key)
            # Insert into sorted ring
            bisect.insort(self.ring, h)
            self.hash_to_node[h] = node_id

    def remove_node(self, node_id: str) -> bool:
        """Remove physical node and all its virtual replicas from the ring."""
        if node_id not in self.nodes:
            return False
        self.nodes.remove(node_id)

        # Remove replicas from ring and map
        new_ring = []
        for h in self.ring:
            if self.hash_to_node.get(h) == node_id:
                del self.hash_to_node[h]
            else:
                new_ring.append(h)
        self.ring = new_ring
        return True

    def get_node(self, key: str) -> Optional[str]:
        """
        Determine responsible physical node for a given record key.
        Uses binary search to find the first ring token >= hash(key), wrapping around at 2^256.
        """
        if not self.ring:
            return None

        h = self._hash(str(key))
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0  # Wraparound to first node on the ring

        token_hash = self.ring[idx]
        return self.hash_to_node[token_hash]

    def get_node_distribution(self, record_keys: List[str]) -> Dict[str, List[str]]:
        """Distribute a list of keys across active nodes on the ring."""
        distribution: Dict[str, List[str]] = {n: [] for n in self.nodes}
        for key in record_keys:
            node = self.get_node(key)
            if node:
                distribution[node].append(key)
        return distribution

    def calculate_migration(
        self, record_keys: List[str], new_node_id: str
    ) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Simulate adding a new node and determine which records must migrate.
        Returns mapping: source_node -> list of (key, source_node, target_node).
        """
        # Current mapping
        current_map = {k: self.get_node(k) for k in record_keys}

        # Add new node temporarily
        self.add_node(new_node_id)
        new_map = {k: self.get_node(k) for k in record_keys}
        # Rollback temporary addition
        self.remove_node(new_node_id)

        migrations: Dict[str, List[Tuple[str, str, str]]] = {}
        for k in record_keys:
            src = current_map[k]
            dst = new_map[k]
            if src != dst:
                if src not in migrations:
                    migrations[src] = []
                migrations[src].append((k, src, dst))

        return migrations
