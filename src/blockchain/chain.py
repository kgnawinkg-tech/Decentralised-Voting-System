"""
Blockchain Manager

Maintains the persistent chain of blocks, doubly linked in-memory structures,
AVL/BST indexing for fast block retrieval, and chain integrity verification.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.blockchain.block import Block
from src.blockchain.merkle_tree import MerkleTree, MerkleProofStep
from src.blockchain.validation import validate_single_block, validate_chain
from src.dsa.avl_tree import AVLTree
from src.dsa.doubly_linked_list import DoublyLinkedList
from src.security.hashing import sha256_hash


class Blockchain:
    """
    Manages the ledger of blocks.
    Employs Doubly Linked List for traversal and AVL Tree for O(log N) block lookups.
    """

    def __init__(self, node_id: str = "node_a", shard_id: str = "shard_default"):
        self.node_id: str = node_id
        self.shard_id: str = shard_id
        self.blocks: List[Block] = []
        self.head: Optional[Block] = None
        self.tail: Optional[Block] = None

        # AVL Tree index: block_index -> Block
        self.index_tree: AVLTree = AVLTree()
        # Hash table: block_hash -> Block
        self.hash_index: Dict[str, Block] = {}
        # Transaction ID index: tx_id -> (Block, tx_dict, leaf_index)
        self.tx_index: Dict[str, Tuple[Block, Dict[str, Any], int]] = {}

        # Initialize with genesis block
        self._create_genesis_block()

    def _create_genesis_block(self) -> Block:
        """Create and append the immutable genesis block."""
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash="0" * 64,
            timestamp=1700000000.0,  # Fixed canonical timestamp
            node_id="genesis_network",
            shard_id="genesis_network",
            version=1,
            merkle_root=MerkleTree.EMPTY_ROOT,
        )
        self.blocks.append(genesis)
        self.head = genesis
        self.tail = genesis
        self.index_tree.insert(0, genesis)
        self.hash_index[genesis.current_hash] = genesis
        return genesis

    def get_tip(self) -> Block:
        """Return latest verified block at chain tip."""
        assert self.tail is not None
        return self.tail

    def get_height(self) -> int:
        """Return current block height (number of blocks)."""
        return len(self.blocks)

    def add_block(
        self,
        transactions: List[Dict[str, Any]],
        timestamp: Optional[float] = None,
        node_id: Optional[str] = None,
    ) -> Block:
        """
        Create, validate, and append a new block to the blockchain.
        Returns the newly mined block.
        """
        tip = self.get_tip()
        new_block = Block(
            index=tip.index + 1,
            transactions=transactions,
            previous_hash=tip.current_hash,
            timestamp=timestamp,
            node_id=node_id if node_id else self.node_id,
            shard_id=self.shard_id,
            version=1,
        )

        valid, reason = validate_single_block(new_block, previous_block=tip)
        if not valid:
            raise ValueError(f"Block proposal invalid: {reason}")

        # Update doubly linked list pointers
        tip.next_node = new_block
        new_block.prev_node = tip
        self.tail = new_block

        # Append to array & indexes
        self.blocks.append(new_block)
        self.index_tree.insert(new_block.index, new_block)
        self.hash_index[new_block.current_hash] = new_block

        # Index transactions
        for leaf_idx, tx in enumerate(new_block.transactions):
            tx_id = tx.get("transaction_id", sha256_hash(tx))
            self.tx_index[tx_id] = (new_block, tx, leaf_idx)

        return new_block

    def append_existing_block(self, block: Block) -> bool:
        """Append an imported block from peer synchronization after strict validation."""
        tip = self.get_tip()
        if block.index != tip.index + 1:
            return False

        valid, reason = validate_single_block(block, previous_block=tip)
        if not valid:
            return False

        tip.next_node = block
        block.prev_node = tip
        self.tail = block

        self.blocks.append(block)
        self.index_tree.insert(block.index, block)
        self.hash_index[block.current_hash] = block

        for leaf_idx, tx in enumerate(block.transactions):
            tx_id = tx.get("transaction_id", sha256_hash(tx))
            self.tx_index[tx_id] = (block, tx, leaf_idx)

        return True

    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Look up block by index in O(log N) using AVL Tree."""
        return self.index_tree.search(index)

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Look up block by hash."""
        return self.hash_index.get(block_hash)

    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Look up transaction record by ID."""
        entry = self.tx_index.get(tx_id)
        if entry:
            block, tx, _ = entry
            return {
                "transaction": tx,
                "block_index": block.index,
                "block_hash": block.current_hash,
                "merkle_root": block.merkle_root,
                "timestamp": block.timestamp,
            }
        return None

    def get_merkle_proof(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Generate Merkle inclusion proof for a committed transaction."""
        entry = self.tx_index.get(tx_id)
        if not entry:
            return None

        block, tx, leaf_idx = entry
        tree = block.get_merkle_tree()
        proof_steps = tree.get_proof(leaf_idx)
        leaf_hash = tree.leaves[leaf_idx]

        return {
            "transaction_id": tx_id,
            "leaf_hash": leaf_hash,
            "block_index": block.index,
            "block_hash": block.current_hash,
            "merkle_root": block.merkle_root,
            "proof": [step.to_dict() for step in proof_steps],
        }

    def verify_integrity(self) -> Tuple[bool, str]:
        """Verify full chain integrity from genesis to tip."""
        return validate_chain(self.blocks)

    def to_list(self) -> List[Dict[str, Any]]:
        """Export chain as list of block dictionaries."""
        return [b.to_dict() for b in self.blocks]
