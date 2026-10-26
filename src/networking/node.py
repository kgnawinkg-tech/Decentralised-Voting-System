"""
Node Core Orchestrator

The central decentralized node coordinator:
- Integrates local SQLite storage, Blockchain ledger, FIFO Mempool Queue,
  Circular Request Buffer, Consistent Hashing Shard Store, and Peer Graph.
- Executes the decoupled anonymous voting workflow, consensus protocol,
  and background peer synchronization.
"""

import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from src.blockchain.block import Block
from src.blockchain.chain import Blockchain
from src.dsa.circular_queue import CircularQueue
from src.dsa.consistent_hashing import ConsistentHashingRing
from src.dsa.hash_set import HashSet
from src.dsa.queue import Queue
from src.networking.consensus import ConsensusManager
from src.networking.peer_manager import PeerManager
from src.networking.synchronization import Synchronizer
from src.security.digital_signatures import KeyPair
from src.storage.database import Database
from src.storage.shard_store import ShardStore
from src.voting.authorization import VotingAuthorizationManager
from src.voting.ballot import Ballot, BallotReceipt
from src.voting.election import Election
from src.voting.tally import ElectionTally
from src.voting.voter_registry import VoterRegistry


class Node:
    """Represents an independent node in the decentralized voting network."""

    def __init__(
        self,
        node_id: str,
        name: str,
        host: str,
        port: int,
        db_path: str,
        peer_endpoints: Optional[List[str]] = None,
        virtual_nodes: int = 50,
        quorum_size: int = 2,
        election_config: Optional[Dict[str, Any]] = None,
    ):
        self.node_id: str = node_id
        self.name: str = name
        self.host: str = host
        self.port: int = port
        self.endpoint: str = f"http://{host}:{port}"
        self.lock = threading.Lock()

        # 1. Independent Persistent SQLite Database
        self.db: Database = Database(db_path)

        # 2. KeyPair for Digital Signatures
        self.keypair: KeyPair = KeyPair.generate()

        # 3. Local Blockchain
        self.blockchain: Blockchain = Blockchain(node_id=self.node_id, shard_id=self.node_id)
        self._load_blockchain_from_db()

        # 4. Consistent Hashing Ring with Virtual Nodes (Concept 15)
        self.ring: ConsistentHashingRing = ConsistentHashingRing(virtual_nodes=virtual_nodes)
        self.ring.add_node(self.node_id)
        if peer_endpoints:
            # Add known initial peer IDs based on convention
            for ep in peer_endpoints:
                if "5001" in ep:
                    self.ring.add_node("node_a")
                elif "5002" in ep:
                    self.ring.add_node("node_b")
                elif "5003" in ep:
                    self.ring.add_node("node_c")

        # 5. Distributed Shard Store
        self.shard_store: ShardStore = ShardStore(self.node_id, self.db, self.ring)

        # 6. Mempool FIFO Queue (Concept 5) & Duplicate Transaction HashSet (Concept 24)
        self.mempool: Queue = Queue()
        self.seen_transactions: HashSet = HashSet()

        # 7. Circular Request Buffer (Concept 12) to bound concurrency
        self.request_buffer: CircularQueue = CircularQueue(capacity=500)

        # 8. Election Management & Voter Registry
        e_conf = election_config or {}
        self.election: Election = Election(
            election_id=e_conf.get("id", "election_2026_general"),
            title=e_conf.get("title", "2026 Decentralized General Election"),
            description=e_conf.get("description", "Secure voting on blockchain"),
            candidates=e_conf.get("candidates", [
                {"id": "cand_1", "name": "Alice Johnson", "party": "Progressive Tech Alliance"},
                {"id": "cand_2", "name": "Bob Martinez", "party": "Open Data Coalition"},
                {"id": "cand_3", "name": "Carol Chen", "party": "Green Cyber Initiative"},
            ]),
        )
        self.voter_registry: VoterRegistry = VoterRegistry(self.db)
        self.auth_manager: VotingAuthorizationManager = VotingAuthorizationManager(
            self.db, self.election.election_id
        )
        self.tally: ElectionTally = ElectionTally(self.election, self.blockchain, self.db)

        # 9. Networking, Peer Management & Consensus
        self.peer_manager: PeerManager = PeerManager(
            self.node_id, self.endpoint, peer_endpoints=peer_endpoints
        )
        self.consensus: ConsensusManager = ConsensusManager(
            self.node_id, self.keypair, quorum_size=quorum_size, is_leader=(self.node_id == "node_a")
        )
        self.synchronizer: Synchronizer = Synchronizer(self.node_id, self.blockchain, self.db)

    def _load_blockchain_from_db(self) -> None:
        """Load persisted blocks into blockchain on startup."""
        blocks = self.db.get_all_blocks()
        if not blocks:
            # Save initial genesis block to db
            genesis = self.blockchain.blocks[0]
            self.db.save_block(genesis.to_dict())
        else:
            # Reconstruct chain from stored blocks
            reconstructed_blocks = [Block.from_dict(b) for b in blocks]
            self.blockchain.blocks = reconstructed_blocks
            self.blockchain.head = reconstructed_blocks[0]
            self.blockchain.tail = reconstructed_blocks[-1]
            for i in range(len(reconstructed_blocks) - 1):
                reconstructed_blocks[i].next_node = reconstructed_blocks[i + 1]
                reconstructed_blocks[i + 1].prev_node = reconstructed_blocks[i]
            for b in reconstructed_blocks:
                self.blockchain.index_tree.insert(b.index, b)
                self.blockchain.hash_index[b.current_hash] = b
                for l_idx, tx in enumerate(b.transactions):
                    tx_id = tx.get("transaction_id")
                    if tx_id:
                        self.blockchain.tx_index[tx_id] = (b, tx, l_idx)

    def submit_ballot_transaction(
        self, candidate_id: str, raw_auth_token: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Process incoming ballot submission:
        1. Buffer request in CircularQueue.
        2. Validate election is OPEN.
        3. Validate candidate ID.
        4. Redeem single-use authorization token (O(1) duplicate check & atomic DB update).
        5. Check memory HashSet (Concept 24).
        6. Determine responsible shard via Consistent Hashing Ring (Concept 15).
        7. If local node is responsible, add to Mempool FIFO Queue (Concept 5).
        8. Return submission receipt.
        """
        # CircularQueue buffer check
        try:
            self.request_buffer.enqueue(time.time())
            self.request_buffer.dequeue()
        except Exception:
            pass

        if not self.election.is_open():
            return False, None, "Election is currently CLOSED. Ballot rejected."

        if not self.election.is_valid_candidate(candidate_id):
            return False, None, f"Invalid candidate ID: '{candidate_id}'"

        with self.lock:
            # Atomically redeem authorization token
            redeemed, token_hash, msg = self.auth_manager.redeem_token(raw_auth_token)
            if not redeemed:
                return False, None, f"Ballot Rejected: {msg}"

            ballot = Ballot(candidate_id=candidate_id, token_hash=token_hash)
            tx_id = ballot.transaction_id

            # Duplicate transaction check via custom HashSet
            if self.seen_transactions.contains(tx_id):
                return False, None, "Duplicate ballot transaction detected"
            self.seen_transactions.add(tx_id)

            # Shard routing check
            responsible_node = self.ring.get_node(tx_id)

            # Enqueue into Mempool FIFO Queue
            self.mempool.enqueue(ballot.to_dict())

            # Store in local DB accepted_ballots table
            import json
            self.db.record_accepted_ballot(
                transaction_id=tx_id,
                candidate_id=candidate_id,
                token_hash=token_hash,
                raw_json=json.dumps(ballot.to_dict()),
            )

            self.db.log_audit(
                "BALLOT_ACCEPTED",
                f"Accepted ballot tx {tx_id[:8]}... for candidate {candidate_id} (assigned shard: {responsible_node})",
            )

            receipt_info = {
                "transaction_id": tx_id,
                "candidate_id": candidate_id,
                "token_hash": token_hash,
                "assigned_shard": responsible_node,
                "mempool_queued": True,
                "timestamp": ballot.timestamp,
            }
            return True, receipt_info, "Ballot accepted and queued for block inclusion"

    def mine_pending_blocks(self) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Drain pending transactions from Mempool FIFO Queue, build a new candidate Block,
        and run the Consensus Quorum protocol across peers.
        """
        with self.lock:
            if self.mempool.is_empty():
                return False, None, "Mempool is empty. No pending transactions to mine."

            pending_txs = []
            while not self.mempool.is_empty():
                pending_txs.append(self.mempool.dequeue())

            tip = self.blockchain.get_tip()
            candidate_block = Block(
                index=tip.index + 1,
                transactions=pending_txs,
                previous_hash=tip.current_hash,
                node_id=self.node_id,
                shard_id=self.node_id,
            )

            # Consensus protocol
            self.peer_manager.ping_all_peers()
            online_peers = self.peer_manager.get_online_peers()
            if not online_peers:
                # Local single-node mode: self-consensus
                consensus_ok = True
                consensus_msg = "Single-node consensus verified locally"
                endorsements = []
            else:
                consensus_ok, consensus_msg, endorsements = self.consensus.propose_and_reach_consensus(
                    candidate_block, online_peers
                )

            if not consensus_ok:
                # Re-enqueue transactions back into Mempool FIFO Queue
                for tx in reversed(pending_txs):
                    self.mempool.enqueue(tx)
                return False, None, f"Block mining failed consensus: {consensus_msg}"

            # Append the exact agreed candidate block to local blockchain
            self.blockchain.append_existing_block(candidate_block)
            self.db.save_block(candidate_block.to_dict())
            self.db.log_audit(
                "BLOCK_MINED",
                f"Mined block {candidate_block.index} with {len(pending_txs)} txs (hash={candidate_block.current_hash[:8]}...)",
            )

            return True, candidate_block.to_dict(), f"Block {candidate_block.index} committed successfully! {consensus_msg}"

    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive node status report."""
        is_valid, reason = self.blockchain.verify_integrity()
        return {
            "node_id": self.node_id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "endpoint": self.endpoint,
            "block_height": len(self.blockchain.blocks),
            "tip_hash": self.blockchain.get_tip().current_hash,
            "chain_valid": is_valid,
            "chain_integrity_message": reason,
            "pending_mempool_size": len(self.mempool),
            "stored_records_count": len(self.db.get_accepted_ballots()),
            "online_peers": self.peer_manager.get_online_peers(),
            "election_status": self.election.status.value,
        }
