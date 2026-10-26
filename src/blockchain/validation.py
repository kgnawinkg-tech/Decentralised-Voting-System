"""
Blockchain Validation Module

Provides rigorous verification of blocks, transactions, cryptographic links,
Merkle roots, and full chain integrity. Rejects any tampering attempt.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.blockchain.block import Block
from src.blockchain.merkle_tree import MerkleTree
from src.security.hashing import sha256_hash


class BlockValidationError(ValueError):
    """Raised when a block fails cryptographic or structural validation."""
    pass


def validate_block_transactions(transactions: List[Dict[str, Any]]) -> bool:
    """Verify syntactic correctness of transactions inside a block."""
    for tx in transactions:
        if not isinstance(tx, dict):
            return False
        if "transaction_id" not in tx or "candidate_id" not in tx:
            return False
    return True


def validate_single_block(
    block: Block, previous_block: Optional[Block] = None
) -> Tuple[bool, str]:
    """
    Validate a single block:
    1. Verify current_hash matches recalculated hash of block header.
    2. Verify Merkle root matches recalculated Merkle tree of transactions.
    3. If previous_block is provided:
       - Verify block.index == previous_block.index + 1
       - Verify block.previous_hash == previous_block.current_hash
       - Verify block.timestamp >= previous_block.timestamp
    4. If genesis block (index 0):
       - Verify previous_hash == "0" * 64 or "0"

    Returns (is_valid, error_reason).
    """
    # 1. Check recalculated hash
    expected_hash = block.calculate_hash()
    if block.current_hash != expected_hash:
        return (
            False,
            f"Block {block.index} hash mismatch: claimed '{block.current_hash}', calculated '{expected_hash}'",
        )

    # 2. Check Merkle root
    tx_hashes = [sha256_hash(tx) for tx in block.transactions]
    expected_merkle = MerkleTree(tx_hashes).root
    if block.merkle_root != expected_merkle:
        return (
            False,
            f"Block {block.index} Merkle root mismatch: claimed '{block.merkle_root}', calculated '{expected_merkle}'",
        )

    # 3. Check transaction structure
    if not validate_block_transactions(block.transactions):
        return False, f"Block {block.index} contains malformed transaction structures"

    # 4. Check chain linkage
    if previous_block is not None:
        if block.index != previous_block.index + 1:
            return (
                False,
                f"Block index sequence broken: expected {previous_block.index + 1}, got {block.index}",
            )
        if block.previous_hash != previous_block.current_hash:
            return (
                False,
                f"Block {block.index} previous_hash mismatch: expected '{previous_block.current_hash}', got '{block.previous_hash}'",
            )
        if block.timestamp < previous_block.timestamp - 1.0:  # Allow 1 sec clock skew
            return (
                False,
                f"Block {block.index} timestamp {block.timestamp} precedes parent timestamp {previous_block.timestamp}",
            )
    else:
        # Genesis block check
        if block.index != 0:
            return False, f"Non-genesis block {block.index} has no previous block reference"
        if block.previous_hash not in ("0", "0" * 64):
            return False, f"Genesis block must have previous_hash of '0', got '{block.previous_hash}'"

    return True, "Valid block"


def validate_chain(chain: List[Block]) -> Tuple[bool, str]:
    """
    Verify entire blockchain from genesis to tip.
    Returns (is_valid, status_message).
    """
    if not chain:
        return False, "Chain is empty"

    # Validate genesis block
    valid_genesis, reason = validate_single_block(chain[0], previous_block=None)
    if not valid_genesis:
        return False, f"Genesis block invalid: {reason}"

    # Validate each successive block
    for i in range(1, len(chain)):
        valid_block, reason = validate_single_block(chain[i], previous_block=chain[i - 1])
        if not valid_block:
            return False, f"Chain corrupted at block {i}: {reason}"

    return True, "Entire blockchain integrity verified successfully"
