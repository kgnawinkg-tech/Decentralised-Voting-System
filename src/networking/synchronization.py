"""
Blockchain & Shard Synchronization Module

Synchronizes blocks and shard records across physical/simulated nodes.
Uses the Priority Queue (Concept 6) to schedule synchronization jobs, prioritizing peers
with the largest block gaps or highest latency discrepancies.
"""

from typing import Any, Dict, List, Optional, Tuple
import requests
from src.blockchain.block import Block
from src.blockchain.chain import Blockchain
from src.dsa.priority_queue import PriorityQueue
from src.storage.database import Database


class SyncJob:
    """Represents a scheduled peer synchronization job."""

    def __init__(self, peer_endpoint: str, peer_height: int, local_height: int):
        self.peer_endpoint = peer_endpoint
        self.peer_height = peer_height
        self.local_height = local_height
        # Priority is negative height gap (larger gap has smaller numerical value, so min-heap runs it first)
        self.gap = peer_height - local_height


class Synchronizer:
    """Orchestrates blockchain synchronization across peers."""

    def __init__(self, local_node_id: str, blockchain: Blockchain, db: Database):
        self.local_node_id = local_node_id
        self.blockchain = blockchain
        self.db = db
        self.sync_queue: PriorityQueue = PriorityQueue()

    def discover_and_queue_sync(self, peer_endpoints: List[str], timeout: float = 2.0) -> int:
        """Query peers for their chain heights and queue synchronization tasks."""
        local_height = len(self.blockchain.blocks)
        queued_count = 0

        for endpoint in peer_endpoints:
            url = f"{endpoint.rstrip('/')}/api/health"
            try:
                resp = requests.get(url, timeout=timeout)
                if resp.status_code == 200:
                    peer_height = resp.json().get("block_height", 0)
                    if peer_height > local_height:
                        gap = peer_height - local_height
                        job = SyncJob(endpoint, peer_height, local_height)
                        # Negative gap so largest gap is popped first
                        self.sync_queue.push(job, priority=-float(gap))
                        queued_count += 1
            except Exception:
                continue

        return queued_count

    def process_sync_queue(self, timeout: float = 3.0) -> Tuple[int, List[str]]:
        """
        Process synchronization tasks from PriorityQueue.
        Downloads missing blocks from peer, verifies each block, and appends to local chain.
        Returns (blocks_synced, status_logs).
        """
        logs = []
        total_synced = 0

        while not self.sync_queue.is_empty():
            job: SyncJob = self.sync_queue.pop()
            logs.append(f"Starting sync from peer {job.peer_endpoint} (gap: {job.gap} blocks)")

            curr_height = len(self.blockchain.blocks)
            # Fetch missing blocks sequentially
            for idx in range(curr_height, job.peer_height):
                block_url = f"{job.peer_endpoint.rstrip('/')}/api/block/{idx}"
                try:
                    resp = requests.get(block_url, timeout=timeout)
                    if resp.status_code == 200:
                        block_data = resp.json().get("block")
                        if not block_data:
                            break
                        candidate_block = Block.from_dict(block_data)
                        success = self.blockchain.append_existing_block(candidate_block)
                        if success:
                            # Save to local database
                            self.db.save_block(candidate_block.to_dict())
                            total_synced += 1
                            logs.append(f"Synchronized & verified block {candidate_block.index}")
                        else:
                            logs.append(f"Sync validation FAILED on block {idx} from {job.peer_endpoint}")
                            break
                    else:
                        break
                except Exception as e:
                    logs.append(f"Sync connection error with {job.peer_endpoint}: {str(e)}")
                    break

        return total_synced, logs
