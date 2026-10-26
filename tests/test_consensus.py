"""
Consensus Protocol & Failure Handling Tests
"""

import pytest
from src.blockchain.block import Block
from src.blockchain.chain import Blockchain
from src.networking.consensus import ConsensusManager
from src.security.digital_signatures import KeyPair


def test_follower_proposal_validation_success():
    chain = Blockchain(node_id="node_a")
    tip = chain.get_tip()

    follower_kp = KeyPair.generate()
    follower_consensus = ConsensusManager(
        local_node_id="node_b",
        keypair=follower_kp,
        quorum_size=2,
        is_leader=False,
    )

    valid_block = Block(
        index=tip.index + 1,
        transactions=[{"transaction_id": "tx1", "candidate_id": "cand_1"}],
        previous_hash=tip.current_hash,
        node_id="node_a",
    )

    endorsed, reason, signature = follower_consensus.validate_proposal(
        valid_block.to_dict(), chain_tip=tip
    )
    assert endorsed is True
    assert signature is not None
    assert "endorsed" in reason.lower()


def test_follower_proposal_validation_tampered_rejection():
    chain = Blockchain(node_id="node_a")
    tip = chain.get_tip()

    follower_kp = KeyPair.generate()
    follower_consensus = ConsensusManager(
        local_node_id="node_b",
        keypair=follower_kp,
        quorum_size=2,
        is_leader=False,
    )

    # Invalid previous hash
    invalid_block = Block(
        index=tip.index + 1,
        transactions=[{"transaction_id": "tx1", "candidate_id": "cand_1"}],
        previous_hash="wrong_hash" * 4,
        node_id="node_a",
    )

    endorsed, reason, signature = follower_consensus.validate_proposal(
        invalid_block.to_dict(), chain_tip=tip
    )
    assert endorsed is False
    assert signature is None
    assert "rejection" in reason.lower()


def test_consensus_quorum_failure_when_peers_unreachable():
    chain = Blockchain(node_id="node_a")
    tip = chain.get_tip()
    leader_kp = KeyPair.generate()
    leader_consensus = ConsensusManager(
        local_node_id="node_a",
        keypair=leader_kp,
        quorum_size=2,
        is_leader=True,
    )

    candidate_block = Block(
        index=tip.index + 1,
        transactions=[{"transaction_id": "tx1", "candidate_id": "cand_1"}],
        previous_hash=tip.current_hash,
    )

    # Broadcast to non-existent ports (offline peers)
    success, msg, endorsements = leader_consensus.propose_and_reach_consensus(
        candidate_block, peer_endpoints=["http://127.0.0.1:59998", "http://127.0.0.1:59999"], timeout=0.5
    )
    # Quorum of 2 cannot be reached with only leader vote (1 vote)
    assert success is False
    assert "failed" in msg.lower()
    assert len(endorsements) == 1
