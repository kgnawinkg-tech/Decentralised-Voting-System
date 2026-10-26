"""
Consistent Hashing & Distributed Sharding Tests
"""

import os
import tempfile
import pytest
from src.dsa.consistent_hashing import ConsistentHashingRing
from src.storage.database import Database
from src.storage.shard_store import ShardStore


def test_consistent_hashing_ring_distribution():
    ring = ConsistentHashingRing(virtual_nodes=50)
    ring.add_node("node_a")
    ring.add_node("node_b")
    ring.add_node("node_c")

    keys = [f"record_key_{i}" for i in range(300)]
    dist = ring.get_node_distribution(keys)

    # Every node should receive a fair share of keys (roughly 100 +/- 40)
    for node_id in ["node_a", "node_b", "node_c"]:
        assert len(dist[node_id]) > 40
        assert len(dist[node_id]) < 160


def test_shard_store_record_assignment():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "node_a.db"))
        ring = ConsistentHashingRing(virtual_nodes=50)
        ring.add_node("node_a")
        ring.add_node("node_b")

        shard = ShardStore("node_a", db, ring)

        # Find a key that maps to node_a and one that maps to node_b
        key_for_a = None
        key_for_b = None
        for i in range(100):
            k = f"test_key_{i}"
            mapped = ring.get_node(k)
            if mapped == "node_a" and key_for_a is None:
                key_for_a = k
            elif mapped == "node_b" and key_for_b is None:
                key_for_b = k
            if key_for_a and key_for_b:
                break

        # Storing key_for_a should succeed on node_a
        ok_a, _ = shard.store_record(key_for_a, "ballot", {"val": 123})
        assert ok_a is True

        # Storing key_for_b should be rejected by node_a
        ok_b, msg_b = shard.store_record(key_for_b, "ballot", {"val": 456})
        assert ok_b is False
        assert "routes to shard 'node_b'" in msg_b


def test_record_migration_after_node_addition():
    ring = ConsistentHashingRing(virtual_nodes=50)
    ring.add_node("node_a")
    ring.add_node("node_b")
    ring.add_node("node_c")

    keys = [f"item_{i}" for i in range(200)]
    initial_map = {k: ring.get_node(k) for k in keys}

    migrations = ring.calculate_migration(keys, "node_d")
    total_migrated = sum(len(items) for items in migrations.values())

    # Only a fraction of keys should move to node_d
    assert 0 < total_migrated < 100

    # For all keys that didn't move to node_d, their assignment must remain strictly unchanged!
    ring.add_node("node_d")
    for k in keys:
        new_assigned = ring.get_node(k)
        if new_assigned != "node_d":
            assert new_assigned == initial_map[k]
