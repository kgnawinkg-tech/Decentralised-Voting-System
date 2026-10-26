"""
Blockchain & Integrity Verification Tests
"""

import pytest
from src.blockchain.block import Block
from src.blockchain.chain import Blockchain
from src.blockchain.validation import validate_single_block, validate_chain
from src.security.hashing import sha256_hash


def test_genesis_block_creation():
    chain = Blockchain(node_id="node_a")
    assert len(chain.blocks) == 1
    genesis = chain.blocks[0]
    assert genesis.index == 0
    assert genesis.previous_hash == "0" * 64
    assert len(genesis.transactions) == 0
    assert genesis.current_hash == genesis.calculate_hash()


def test_valid_block_addition_and_hash_linkage():
    chain = Blockchain(node_id="node_a")
    txs = [{"transaction_id": "tx_01", "candidate_id": "cand_1", "token_hash": "th_1"}]
    b1 = chain.add_block(txs)
    assert b1.index == 1
    assert b1.previous_hash == chain.blocks[0].current_hash
    assert len(chain.blocks) == 2

    # Verify chain integrity
    valid, msg = chain.verify_integrity()
    assert valid is True
    assert "verified" in msg.lower()


def test_tampering_detection_modified_transaction():
    chain = Blockchain(node_id="node_a")
    txs = [{"transaction_id": "tx_01", "candidate_id": "cand_1", "token_hash": "th_1"}]
    b1 = chain.add_block(txs)

    # Tamper with block transaction
    b1.transactions[0]["candidate_id"] = "cand_tampered"

    # Validation should catch Merkle root mismatch
    valid, reason = validate_single_block(b1, previous_block=chain.blocks[0])
    assert valid is False
    assert "merkle root mismatch" in reason.lower()


def test_tampering_detection_modified_previous_hash():
    chain = Blockchain(node_id="node_a")
    txs = [{"transaction_id": "tx_01", "candidate_id": "cand_1", "token_hash": "th_1"}]
    b1 = chain.add_block(txs)

    # Tamper with previous hash
    b1.previous_hash = "f" * 64
    # Recalculate hash so hash matches new previous_hash
    b1.current_hash = b1.calculate_hash()

    valid, reason = validate_single_block(b1, previous_block=chain.blocks[0])
    assert valid is False
    assert "previous_hash mismatch" in reason.lower()
