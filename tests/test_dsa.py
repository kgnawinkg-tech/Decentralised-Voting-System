"""
Unit & Integration Tests for all 25 DSA Concepts
"""

import pytest
from src.dsa.hash_table import HashTable
from src.dsa.singly_linked_list import SinglyLinkedList
from src.dsa.doubly_linked_list import DoublyLinkedList
from src.dsa.stack import Stack, StackUnderflowError
from src.dsa.queue import Queue, QueueUnderflowError
from src.dsa.priority_queue import PriorityQueue, PriorityQueueUnderflowError
from src.dsa.binary_search_tree import BinarySearchTree
from src.dsa.avl_tree import AVLTree
from src.dsa.trie import Trie
from src.dsa.graph import Graph
from src.dsa.union_find import UnionFind
from src.dsa.circular_queue import CircularQueue, CircularQueueOverflowError, CircularQueueUnderflowError
from src.dsa.bfs import bfs_traversal, bfs_shortest_path
from src.dsa.dfs import dfs_traversal, dfs_connected_components
from src.dsa.consistent_hashing import ConsistentHashingRing
from src.dsa.binary_search import binary_search, binary_search_leftmost
from src.dsa.merge_sort import merge_sort
from src.dsa.quick_sort import quick_sort
from src.dsa.dijkstra import dijkstra_shortest_path, reconstruct_dijkstra_path
from src.dsa.topological_sort import topological_sort, CycleDependencyError
from src.dsa.cycle_detection import detect_cycle_directed, detect_cycle_undirected
from src.dsa.hash_set import HashSet
from src.blockchain.merkle_tree import MerkleTree
from src.security.hashing import sha256_hash
from src.security.digital_signatures import KeyPair, verify_signature


# 1. Hash Table Tests
def test_hash_table_operations_and_collisions():
    ht = HashTable(initial_capacity=4)  # Small capacity to force collisions and resizing
    keys = [f"voter_{i}" for i in range(25)]
    for i, k in enumerate(keys):
        ht.insert(k, f"payload_{i}")

    assert len(ht) == 25
    assert ht.capacity > 4  # Resized dynamically

    for i, k in enumerate(keys):
        assert ht.search(k) == f"payload_{i}"

    # Update existing
    ht.insert("voter_0", "updated_payload")
    assert ht.search("voter_0") == "updated_payload"
    assert len(ht) == 25

    # Delete
    assert ht.delete("voter_0") is True
    assert ht.search("voter_0") is None
    assert len(ht) == 24
    assert ht.delete("nonexistent") is False


# 2. Singly Linked List Tests
def test_singly_linked_list():
    sll = SinglyLinkedList()
    assert len(sll) == 0
    sll.append("block_0")
    sll.append("block_1")
    sll.prepend("genesis_pre")
    assert sll.to_list() == ["genesis_pre", "block_0", "block_1"]
    assert len(sll) == 3

    assert sll.delete("block_0") is True
    assert sll.to_list() == ["genesis_pre", "block_1"]
    assert sll.delete("nonexistent") is False


# 3. Doubly Linked List Tests
def test_doubly_linked_list():
    dll = DoublyLinkedList()
    dll.append("audit_1")
    dll.append("audit_2")
    dll.append("audit_3")
    assert dll.forward_traversal() == ["audit_1", "audit_2", "audit_3"]
    assert dll.backward_traversal() == ["audit_3", "audit_2", "audit_1"]

    dll.delete("audit_2")
    assert dll.forward_traversal() == ["audit_1", "audit_3"]
    assert dll.backward_traversal() == ["audit_3", "audit_1"]


# 4. Stack Tests
def test_stack_operations_and_underflow():
    st = Stack()
    assert st.is_empty()
    with pytest.raises(StackUnderflowError):
        st.pop()
    with pytest.raises(StackUnderflowError):
        st.peek()

    st.push(10)
    st.push(20)
    assert st.peek() == 20
    assert st.pop() == 20
    assert st.pop() == 10
    assert st.is_empty()


# 5. Queue Tests
def test_queue_ordering_and_underflow():
    q = Queue()
    assert q.is_empty()
    with pytest.raises(QueueUnderflowError):
        q.dequeue()

    q.enqueue("tx_1")
    q.enqueue("tx_2")
    q.enqueue("tx_3")
    assert q.peek() == "tx_1"
    assert q.dequeue() == "tx_1"
    assert q.dequeue() == "tx_2"
    assert q.dequeue() == "tx_3"
    assert q.is_empty()


# 6. Priority Queue Tests
def test_priority_queue():
    pq = PriorityQueue()
    assert pq.is_empty()
    with pytest.raises(PriorityQueueUnderflowError):
        pq.pop()

    pq.push("task_low", priority=10.0)
    pq.push("task_urgent", priority=1.0)
    pq.push("task_medium", priority=5.0)

    assert pq.peek() == "task_urgent"
    assert pq.pop() == "task_urgent"
    assert pq.pop() == "task_medium"
    assert pq.pop() == "task_low"


# 7. Binary Search Tree Tests
def test_binary_search_tree():
    bst = BinarySearchTree()
    values = [40, 20, 60, 10, 30, 50, 70]
    for v in values:
        bst.insert(v, f"data_{v}")

    assert bst.size() == 7
    assert bst.search(30) == "data_30"
    assert bst.search(999) is None

    # In-order traversal gives sorted keys
    in_order_keys = [k for k, _ in bst.in_order()]
    assert in_order_keys == [10, 20, 30, 40, 50, 60, 70]

    # Deletion of node with 2 children
    assert bst.delete(20) is True
    assert bst.search(20) is None
    assert [k for k, _ in bst.in_order()] == [10, 30, 40, 50, 60, 70]


# 8. AVL Tree Tests (Testing LL, RR, LR, RL Rotations)
def test_avl_rotations_and_balancing():
    # Case 1: Right-Right (RR) rotation
    avl_rr = AVLTree()
    avl_rr.insert(10, "10")
    avl_rr.insert(20, "20")
    avl_rr.insert(30, "30")
    assert avl_rr.root.key == 20
    assert avl_rr.root.left.key == 10
    assert avl_rr.root.right.key == 30

    # Case 2: Left-Left (LL) rotation
    avl_ll = AVLTree()
    avl_ll.insert(30, "30")
    avl_ll.insert(20, "20")
    avl_ll.insert(10, "10")
    assert avl_ll.root.key == 20
    assert avl_ll.root.left.key == 10
    assert avl_ll.root.right.key == 30

    # Case 3: Left-Right (LR) rotation
    avl_lr = AVLTree()
    avl_lr.insert(30, "30")
    avl_lr.insert(10, "10")
    avl_lr.insert(20, "20")
    assert avl_lr.root.key == 20
    assert avl_lr.root.left.key == 10
    assert avl_lr.root.right.key == 30

    # Case 4: Right-Left (RL) rotation
    avl_rl = AVLTree()
    avl_rl.insert(10, "10")
    avl_rl.insert(30, "30")
    avl_rl.insert(20, "20")
    assert avl_rl.root.key == 20
    assert avl_rl.root.left.key == 10
    assert avl_rl.root.right.key == 30

    # Deletion test
    assert avl_rl.delete(10) is True
    assert avl_rl.search(10) is None


# 9. Trie Tests
def test_trie():
    trie = Trie()
    trie.insert("Alice Johnson", "cand_1")
    trie.insert("Alexander Smith", "cand_2")
    trie.insert("Bob Martinez", "cand_3")

    assert trie.search_exact("Alice Johnson") == "cand_1"
    assert trie.search_exact("Alice") is None
    assert trie.starts_with("Al") is True
    assert trie.starts_with("Zoo") is False

    matches = trie.get_words_with_prefix("Al")
    match_words = [m[0] for m in matches]
    assert "Alexander Smith" in match_words
    assert "Alice Johnson" in match_words


# 10. Graph Tests
def test_graph_operations():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=5.0)
    g.add_edge("B", "C", weight=7.0)
    assert g.vertex_count() == 3
    assert g.edge_count() == 2
    assert ("B", 5.0) in g.get_neighbors("A")
    assert ("A", 5.0) in g.get_neighbors("B")


# 11. Disjoint Set Union Tests
def test_union_find():
    uf = UnionFind(["A", "B", "C", "D", "E"])
    assert uf.count() == 5
    assert not uf.connected("A", "B")

    uf.union("A", "B")
    uf.union("B", "C")
    assert uf.connected("A", "C")
    assert not uf.connected("A", "D")
    assert uf.count() == 3


# 12. Circular Queue Tests
def test_circular_queue():
    cq = CircularQueue(capacity=3)
    assert cq.is_empty()
    cq.enqueue("item_1")
    cq.enqueue("item_2")
    cq.enqueue("item_3")
    assert cq.is_full()

    with pytest.raises(CircularQueueOverflowError):
        cq.enqueue("overflow_item")

    assert cq.dequeue() == "item_1"
    assert not cq.is_full()
    cq.enqueue("item_4")  # Wraparound
    assert cq.to_list() == ["item_2", "item_3", "item_4"]


# 13 & 14. BFS & DFS Tests
def test_bfs_and_dfs_on_disconnected_graphs():
    g = Graph(directed=False)
    # Component 1: A - B - C
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    # Component 2: D - E
    g.add_edge("D", "E")

    bfs_res = bfs_traversal(g, "A")
    assert set(bfs_res) == {"A", "B", "C"}
    assert "D" not in bfs_res

    dfs_res = dfs_traversal(g, "A")
    assert set(dfs_res) == {"A", "B", "C"}

    components = dfs_connected_components(g)
    assert len(components) == 2
    assert ["A", "B", "C"] in components
    assert ["D", "E"] in components


# 15. Consistent Hashing Tests
def test_consistent_hashing():
    ring = ConsistentHashingRing(virtual_nodes=50)
    ring.add_node("node_a")
    ring.add_node("node_b")
    ring.add_node("node_c")

    # Determinism: same key always maps to same node
    node1 = ring.get_node("record_123")
    node2 = ring.get_node("record_123")
    assert node1 == node2
    assert node1 in {"node_a", "node_b", "node_c"}

    # Migration calculation
    keys = [f"key_{i}" for i in range(100)]
    migrations = ring.calculate_migration(keys, "node_d")
    # Adding 4th node to a 3-node ring should migrate roughly ~25% of keys
    migrated_keys = [item for sublist in migrations.values() for item in sublist]
    assert len(migrated_keys) < 60  # Far less than 100% (minimal reassignment property!)


# 16. Binary Search Tests
def test_binary_search():
    arr = [10, 20, 30, 40, 50, 60]
    assert binary_search(arr, 30) == 2
    assert binary_search(arr, 10) == 0
    assert binary_search(arr, 60) == 5
    assert binary_search(arr, 99) == -1
    assert binary_search([], 10) == -1


# 17 & 18. Sorting Tests vs sorted()
def test_sorting_algorithms():
    import random
    data = [random.randint(0, 1000) for _ in range(100)]
    # Include duplicates and edge cases
    data.extend([42, 42, 42, -5, 0])

    expected = sorted(data)
    assert merge_sort(data) == expected
    assert quick_sort(data) == expected
    assert merge_sort([]) == []
    assert quick_sort([]) == []


# 19. Dijkstra Tests
def test_dijkstra():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=4.0)
    g.add_edge("A", "C", weight=2.0)
    g.add_edge("C", "B", weight=1.0)
    g.add_edge("B", "D", weight=5.0)
    g.add_vertex("UNREACHABLE")

    distances, preds = dijkstra_shortest_path(g, "A")
    assert distances["A"] == 0.0
    assert distances["C"] == 2.0
    assert distances["B"] == 3.0  # Path A -> C -> B (2 + 1 = 3 < 4)
    assert distances["D"] == 8.0
    assert distances["UNREACHABLE"] == float("inf")

    path = reconstruct_dijkstra_path(preds, "A", "B")
    assert path == ["A", "C", "B"]

    # Negative weight rejection
    g.add_edge("X", "Y", weight=-1.0)
    with pytest.raises(ValueError):
        dijkstra_shortest_path(g, "A")


# 20. Topological Sort Tests
def test_topological_sort():
    g = Graph(directed=True)
    g.add_edge("task_1", "task_2")
    g.add_edge("task_2", "task_3")
    g.add_edge("task_1", "task_3")

    order = topological_sort(g)
    assert order.index("task_1") < order.index("task_2")
    assert order.index("task_2") < order.index("task_3")

    # Cycle rejection
    g.add_edge("task_3", "task_1")
    with pytest.raises(CycleDependencyError):
        topological_sort(g)


# 21. Merkle Tree Tests
def test_merkle_tree():
    leaves = ["tx1", "tx2", "tx3", "tx4"]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(2)
    assert MerkleTree.verify_proof(tree.leaves[2], proof, tree.root) is True
    # Tampered leaf
    assert MerkleTree.verify_proof(sha256_hash("tampered_tx"), proof, tree.root) is False

    # Odd leaf test
    tree_odd = MerkleTree(["tx1", "tx2", "tx3"])
    proof_odd = tree_odd.get_proof(2)
    assert MerkleTree.verify_proof(tree_odd.leaves[2], proof_odd, tree_odd.root) is True

    # Single leaf test
    tree_single = MerkleTree(["tx1"])
    proof_single = tree_single.get_proof(0)
    assert MerkleTree.verify_proof(tree_single.leaves[0], proof_single, tree_single.root) is True


# 22. SHA-256 Hashing Tests
def test_sha256_canonical_hashing():
    d1 = {"b": 2, "a": 1}
    d2 = {"a": 1, "b": 2}
    # Deterministic canonical serialization ensures identical hashes despite key insertion order
    assert sha256_hash(d1) == sha256_hash(d2)


# 23. Digital Signatures Tests
def test_digital_signatures():
    kp = KeyPair.generate()
    msg = {"vote": "cand_1", "nonce": 42}
    sig = kp.sign(msg)
    assert verify_signature(kp.get_public_pem(), msg, sig) is True
    assert verify_signature(kp.get_public_pem(), {"vote": "tampered"}, sig) is False


# 24. Hash Set Duplicate Detection Tests
def test_hash_set_duplicate_detection():
    hs = HashSet()
    assert hs.add("token_abc") is True
    assert hs.add("token_abc") is False  # Duplicate detected!
    assert hs.contains("token_abc") is True
    assert hs.contains("token_xyz") is False
    assert len(hs) == 1


# 25. Cycle Detection Tests
def test_cycle_detection():
    g_dir = Graph(directed=True)
    g_dir.add_edge("A", "B")
    g_dir.add_edge("B", "C")
    assert detect_cycle_directed(g_dir)[0] is False
    g_dir.add_edge("C", "A")
    assert detect_cycle_directed(g_dir)[0] is True

    g_undir = Graph(directed=False)
    g_undir.add_edge("A", "B")
    g_undir.add_edge("B", "C")
    assert detect_cycle_undirected(g_undir)[0] is False
    g_undir.add_edge("C", "A")
    assert detect_cycle_undirected(g_undir)[0] is True
