"""
Distributed Shard Store & Consistent Hashing Router

Manages partition-level record assignment across nodes (Computer A, B, C)
using the Consistent Hashing Ring. Routes transactions, detects offline nodes,
and manages record migration when nodes join or leave the network.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.dsa.consistent_hashing import ConsistentHashingRing
from src.storage.database import Database
from src.security.hashing import sha256_hash


class ShardStore:
    """
    Manages sharded records for a node in conjunction with the Consistent Hashing Ring.
    """

    def __init__(self, node_id: str, db: Database, ring: ConsistentHashingRing):
        self.node_id: str = node_id
        self.db: Database = db
        self.ring: ConsistentHashingRing = ring

    def is_responsible_for(self, record_key: str) -> bool:
        """Check if this node is responsible for the given record key."""
        target_node = self.ring.get_node(record_key)
        return target_node == self.node_id

    def store_record(self, key: str, record_type: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Store a record in the local database if this node is responsible.
        Returns (success, message).
        """
        target_node = self.ring.get_node(key)
        if target_node != self.node_id:
            return (
                False,
                f"Record '{key}' routes to shard '{target_node}', not local node '{self.node_id}'",
            )

        import json
        payload_str = json.dumps(payload, sort_keys=True)
        self.db.save_shard_record(key, shard_id=self.node_id, record_type=record_type, payload=payload_str)
        self.db.log_audit("SHARD_RECORD_STORED", f"Stored key '{key}' in shard '{self.node_id}'")
        return True, f"Stored successfully in shard {self.node_id}"

    def get_local_records(self) -> List[Dict[str, Any]]:
        """Fetch all records stored locally in this shard."""
        return self.db.get_shard_records(shard_id=self.node_id)

    def rebalance_records(
        self, all_keys: List[str], new_node_id: str
    ) -> List[Tuple[str, str, str]]:
        """
        Calculate records currently residing on this node that must migrate to new_node_id.
        Returns list of (key, source_node, target_node).
        """
        migrations = self.ring.calculate_migration(all_keys, new_node_id)
        local_migrations = migrations.get(self.node_id, [])
        return local_migrations
