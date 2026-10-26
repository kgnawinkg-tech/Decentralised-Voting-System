"""
HTTP API & Web Endpoints Module

Exposes RESTful endpoints for physical and simulated nodes:
- Health and Peer Discovery
- Transaction submission, sharding routing, and Mempool queue
- Consensus block proposals, validation endorsements, and commit broadcasts
- Merkle proof verification and ballot receipts
- Live DSA concept interactive demonstrations for all 25 concepts
"""

import json
from typing import Any, Dict
from flask import Flask, jsonify, render_template, request, send_from_directory
from src.blockchain.block import Block
from src.blockchain.merkle_tree import MerkleTree, MerkleProofStep
from src.networking.node import Node
from src.security.input_validation import validate_ballot_payload, validate_id


def create_api_app(node: Node) -> Flask:
    """Create Flask application bound to the given Node instance."""
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # --- Health & Node Info ---
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "node_id": node.node_id,
            "name": node.name,
            "block_height": len(node.blockchain.blocks),
            "tip_hash": node.blockchain.get_tip().current_hash,
            "election_status": node.election.status.value,
        })

    @app.route("/api/node_info", methods=["GET"])
    def node_info():
        return jsonify(node.get_status())

    @app.route("/api/peers", methods=["GET", "POST"])
    def peers():
        if request.method == "POST":
            data = request.get_json() or {}
            peer_url = data.get("endpoint")
            if peer_url:
                node.peer_manager.add_peer(peer_url)
                return jsonify({"success": True, "message": f"Peer {peer_url} added"})
            return jsonify({"success": False, "error": "Missing endpoint"}), 400

        node.peer_manager.ping_all_peers()
        return jsonify({
            "local_node": node.node_id,
            "peers": node.peer_manager.peer_status,
            "online_count": len(node.peer_manager.get_online_peers()),
        })

    @app.route("/api/topology", methods=["GET"])
    def topology():
        node.peer_manager.ping_all_peers()
        analytics = node.peer_manager.analyze_network_connectivity()
        return jsonify(analytics)

    # --- Voting & Ballots ---
    @app.route("/api/voter/register", methods=["POST"])
    def register_voter():
        data = request.get_json() or {}
        try:
            voter_id = validate_id(data.get("voter_id", ""), "voter_id")
            name = str(data.get("name", "")).strip()
            password = str(data.get("password", ""))
            email = data.get("email")
            if email:
                email = str(email).strip().lower()
            if not name or not password:
                return jsonify({"success": False, "error": "Name and password are required"}), 400

            success, msg = node.voter_registry.register_voter(voter_id, name, password, email=email)
            status_code = 200 if success else 400
            return jsonify({"success": success, "message": msg, "voter_id": voter_id}), status_code
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/voter/auth_token", methods=["POST"])
    def get_auth_token():
        data = request.get_json() or {}
        voter_id = data.get("voter_id", "")
        password = data.get("password", "")

        auth_ok, voter, auth_msg = node.voter_registry.authenticate_voter(voter_id, password)
        if not auth_ok:
            return jsonify({"success": False, "error": auth_msg}), 401

        issued, token, issue_msg = node.auth_manager.issue_token(voter_id)
        if not issued:
            return jsonify({"success": False, "error": issue_msg}), 400

        return jsonify({
            "success": True,
            "authorization_token": token,
            "message": issue_msg,
            "voter_name": voter["name"] if voter else "",
            "election_id": node.election.election_id,
        })

    @app.route("/api/voter/search", methods=["GET"])
    def search_voters():
        prefix = request.args.get("prefix", "")
        results = node.voter_registry.search_voters_by_prefix(prefix)
        return jsonify({"prefix": prefix, "matches": results})

    @app.route("/api/submit_ballot", methods=["POST"])
    def submit_ballot():
        data = request.get_json() or {}
        try:
            validated = validate_ballot_payload(data)
            candidate_id = validated["candidate_id"]
            auth_token = validated["authorization_token"]

            success, receipt, msg = node.submit_ballot_transaction(candidate_id, auth_token)
            status_code = 200 if success else 400
            return jsonify({"success": success, "receipt": receipt, "message": msg}), status_code
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/mine", methods=["POST"])
    def mine_blocks():
        success, block_data, msg = node.mine_pending_blocks()
        status_code = 200 if success else 400
        return jsonify({"success": success, "block": block_data, "message": msg}), status_code

    # --- Blockchain Queries ---
    @app.route("/api/chain", methods=["GET"])
    def get_chain():
        is_valid, reason = node.blockchain.verify_integrity()
        return jsonify({
            "length": len(node.blockchain.blocks),
            "chain": node.blockchain.to_list(),
            "is_valid": is_valid,
            "integrity_message": reason,
        })

    @app.route("/api/block/<int:index>", methods=["GET"])
    def get_block(index):
        b = node.blockchain.get_block_by_index(index)
        if b:
            return jsonify({"found": True, "block": b.to_dict()})
        return jsonify({"found": False, "error": f"Block index {index} not found"}), 404

    @app.route("/api/merkle_proof/<string:tx_id>", methods=["GET"])
    def get_merkle_proof(tx_id):
        proof_data = node.blockchain.get_merkle_proof(tx_id)
        if proof_data:
            return jsonify({"found": True, "proof_data": proof_data})
        return jsonify({"found": False, "error": f"Transaction {tx_id} not found in committed blocks"}), 404

    @app.route("/api/verify_receipt", methods=["POST"])
    def verify_receipt():
        data = request.get_json() or {}
        tx_id = data.get("transaction_id", "")
        leaf_hash = data.get("leaf_hash") or tx_id
        merkle_root = data.get("merkle_root", "")
        proof_steps_raw = data.get("merkle_proof", [])

        if not leaf_hash or not merkle_root or proof_steps_raw is None:
            return jsonify({"verified": False, "error": "Missing receipt verification fields"}), 400

        steps = [MerkleProofStep.from_dict(s) for s in proof_steps_raw]
        is_verified = MerkleTree.verify_proof(leaf_hash, steps, merkle_root)
        return jsonify({
            "verified": is_verified,
            "transaction_id": tx_id,
            "leaf_hash": leaf_hash,
            "merkle_root": merkle_root,
            "message": "Merkle inclusion verified!" if is_verified else "Invalid Merkle proof",
        })

    # --- Consensus Proposals ---
    @app.route("/api/propose_block", methods=["POST"])
    def propose_block():
        data = request.get_json() or {}
        block_dict = data.get("block", {})
        proposer_id = data.get("proposer_id", "unknown")

        tip = node.blockchain.get_tip()
        endorsed, reason, signature = node.consensus.validate_proposal(block_dict, chain_tip=tip)

        return jsonify({
            "node_id": node.node_id,
            "proposer_id": proposer_id,
            "endorsed": endorsed,
            "reason": reason,
            "public_key": node.keypair.get_public_pem() if endorsed else None,
            "signature": signature,
        })

    @app.route("/api/commit_block", methods=["POST"])
    def commit_block():
        data = request.get_json() or {}
        block_dict = data.get("block", {})
        try:
            b = Block.from_dict(block_dict)
            success = node.blockchain.append_existing_block(b)
            if success:
                node.db.save_block(b.to_dict())
                return jsonify({"committed": True, "block_index": b.index})
            return jsonify({"committed": False, "error": "Block validation failed"}), 400
        except Exception as e:
            return jsonify({"committed": False, "error": str(e)}), 400

    # --- Synchronization ---
    @app.route("/api/sync", methods=["POST"])
    def trigger_sync():
        online_peers = node.peer_manager.get_online_peers()
        queued = node.synchronizer.discover_and_queue_sync(online_peers)
        synced, logs = node.synchronizer.process_sync_queue()
        return jsonify({
            "jobs_queued": queued,
            "blocks_synced": synced,
            "logs": logs,
            "current_height": len(node.blockchain.blocks),
        })

    # --- Election & Tally ---
    @app.route("/api/election", methods=["GET"])
    def get_election():
        return jsonify(node.election.to_dict())

    @app.route("/api/election/status", methods=["POST"])
    def update_election_status():
        data = request.get_json() or {}
        status = data.get("status", "").upper()
        if status == "OPEN":
            node.election.open_election()
        elif status == "CLOSED":
            node.election.close_election()
        else:
            return jsonify({"success": False, "error": "Status must be OPEN or CLOSED"}), 400
        return jsonify({"success": True, "new_status": node.election.status.value})

    @app.route("/api/tally", methods=["GET"])
    def get_tally():
        results = node.tally.calculate_results()
        return jsonify(results)

    # --- Shards & Record Partitioning ---
    @app.route("/api/shards", methods=["GET"])
    def get_shards():
        records = node.shard_store.get_local_records()
        return jsonify({
            "local_node": node.node_id,
            "active_ring_nodes": list(node.ring.nodes),
            "stored_record_count": len(records),
            "records": records[:50],  # Return up to 50
        })

    # --- Interactive DSA Explorer Demo Endpoint (All 25 Concepts!) ---
    @app.route("/api/dsa/explore/<string:concept_name>", methods=["GET", "POST"])
    def explore_dsa(concept_name):
        from src.dsa.hash_table import HashTable
        from src.dsa.singly_linked_list import SinglyLinkedList
        from src.dsa.doubly_linked_list import DoublyLinkedList
        from src.dsa.stack import Stack
        from src.dsa.queue import Queue
        from src.dsa.priority_queue import PriorityQueue
        from src.dsa.binary_search_tree import BinarySearchTree
        from src.dsa.avl_tree import AVLTree
        from src.dsa.trie import Trie
        from src.dsa.graph import Graph
        from src.dsa.union_find import UnionFind
        from src.dsa.circular_queue import CircularQueue
        from src.dsa.bfs import bfs_traversal
        from src.dsa.dfs import dfs_traversal
        from src.dsa.consistent_hashing import ConsistentHashingRing
        from src.dsa.binary_search import binary_search
        from src.dsa.merge_sort import merge_sort
        from src.dsa.quick_sort import quick_sort
        from src.dsa.dijkstra import dijkstra_shortest_path
        from src.dsa.topological_sort import topological_sort
        from src.dsa.cycle_detection import detect_cycle_directed, detect_cycle_undirected
        from src.dsa.hash_set import HashSet
        from src.blockchain.merkle_tree import MerkleTree
        from src.security.hashing import sha256_hash
        from src.security.digital_signatures import KeyPair, verify_signature

        c = concept_name.lower()
        res: Dict[str, Any] = {"concept": concept_name}

        if c == "hash_table":
            ht = HashTable(initial_capacity=8)
            ht.insert("voter_101", {"status": "eligible", "name": "Nawin"})
            ht.insert("voter_102", {"status": "eligible", "name": "Alice"})
            ht.insert("voter_103", {"status": "voted", "name": "Bob"})
            val = ht.search("voter_101")
            res.update({
                "name": "1. Hash Table with Separate Chaining",
                "time_complexity": "Average O(1), Worst O(N)",
                "space_complexity": "O(N + M)",
                "input": ["voter_101", "voter_102", "voter_103"],
                "lookup_result": val,
                "items": ht.items(),
                "buckets_count": ht.capacity,
            })
        elif c == "singly_linked_list":
            sll = SinglyLinkedList()
            sll.append("Block_0_Genesis")
            sll.append("Block_1_TXs_5")
            sll.append("Block_2_TXs_3")
            res.update({
                "name": "2. Singly Linked List",
                "time_complexity": "Append O(1), Traversal O(N)",
                "space_complexity": "O(N)",
                "traversal": sll.to_list(),
                "node_count": len(sll),
            })
        elif c == "doubly_linked_list":
            dll = DoublyLinkedList()
            dll.append("Audit_Event_1")
            dll.append("Audit_Event_2")
            dll.append("Audit_Event_3")
            res.update({
                "name": "3. Doubly Linked List",
                "time_complexity": "Forward/Backward O(N), Insert/Delete O(1)",
                "space_complexity": "O(N)",
                "forward": dll.forward_traversal(),
                "backward": dll.backward_traversal(),
            })
        elif c == "stack":
            st = Stack()
            st.push("State_Genesis")
            st.push("State_Pending")
            st.push("State_Committed")
            top = st.pop()
            res.update({
                "name": "4. Stack (LIFO)",
                "time_complexity": "Push O(1), Pop O(1)",
                "space_complexity": "O(N)",
                "popped_element": top,
                "remaining_stack": st.to_list(),
            })
        elif c == "queue":
            q = Queue()
            q.enqueue("TX_Alice_Vote")
            q.enqueue("TX_Bob_Vote")
            q.enqueue("TX_Carol_Vote")
            first = q.dequeue()
            res.update({
                "name": "5. Queue (FIFO Mempool)",
                "time_complexity": "Enqueue O(1), Dequeue O(1) amortized",
                "space_complexity": "O(N)",
                "dequeued_first": first,
                "remaining_mempool": q.to_list(),
            })
        elif c == "priority_queue":
            pq = PriorityQueue()
            pq.push("Sync_Block_Gap_5", priority=1.0)
            pq.push("Peer_Heartbeat_Ping", priority=3.0)
            pq.push("Critical_Fork_Reconcile", priority=0.5)
            highest_priority_task = pq.pop()
            res.update({
                "name": "6. Priority Queue (Binary Heap)",
                "time_complexity": "Insert O(log N), Extract-Min O(log N)",
                "space_complexity": "O(N)",
                "highest_priority_task": highest_priority_task,
                "remaining_tasks": pq.to_sorted_list(),
            })
        elif c == "binary_search_tree":
            bst = BinarySearchTree()
            for idx in [50, 30, 70, 20, 40, 60, 80]:
                bst.insert(idx, f"Block_Header_{idx}")
            res.update({
                "name": "7. Binary Search Tree",
                "time_complexity": "Average O(log N), Worst O(N)",
                "space_complexity": "O(N)",
                "in_order_sorted": bst.in_order(),
                "search_60": bst.search(60),
            })
        elif c == "avl_tree":
            avl = AVLTree()
            # Inserting in ascending order forces self-balancing rotations!
            for idx in [10, 20, 30, 40, 50, 25]:
                avl.insert(idx, f"Block_{idx}")
            res.update({
                "name": "8. AVL Tree (Self-Balancing BST)",
                "time_complexity": "Guaranteed O(log N) for Insert/Search/Delete",
                "space_complexity": "O(N)",
                "root_key": avl.root.key if avl.root else None,
                "root_height": avl.root.height if avl.root else 0,
                "in_order_balanced": avl.in_order(),
            })
        elif c == "trie":
            trie = Trie()
            trie.insert("Alice Johnson", "cand_1")
            trie.insert("Alexander Smith", "cand_alt")
            trie.insert("Bob Martinez", "cand_2")
            trie.insert("Carol Chen", "cand_3")
            prefix_matches = trie.get_words_with_prefix("Al")
            res.update({
                "name": "9. Trie (Prefix Tree)",
                "time_complexity": "Prefix Search O(L + K)",
                "space_complexity": "O(Sigma * L * N)",
                "prefix_searched": "Al",
                "matches": prefix_matches,
            })
        elif c == "graph":
            g = Graph(directed=False)
            g.add_edge("Node_A", "Node_B", weight=12.5)
            g.add_edge("Node_B", "Node_C", weight=15.0)
            g.add_edge("Node_A", "Node_C", weight=22.0)
            res.update({
                "name": "10. Graph (Adjacency Lists)",
                "time_complexity": "Add Vertex/Edge O(1), Get Neighbors O(deg(V))",
                "space_complexity": "O(V + E)",
                "vertices": g.get_vertices(),
                "edges": g.get_edges(),
            })
        elif c == "union_find":
            uf = UnionFind(["Node_A", "Node_B", "Node_C", "Node_D"])
            uf.union("Node_A", "Node_B")
            uf.union("Node_C", "Node_D")
            res.update({
                "name": "11. Disjoint Set Union (Union-Find)",
                "time_complexity": "Nearly O(1) amortized - O(alpha(N))",
                "space_complexity": "O(N)",
                "is_A_connected_to_B": uf.connected("Node_A", "Node_B"),
                "is_A_connected_to_C": uf.connected("Node_A", "Node_C"),
                "components": uf.get_components(),
                "component_count": uf.count(),
            })
        elif c == "circular_queue":
            cq = CircularQueue(capacity=4)
            cq.enqueue("Request_1")
            cq.enqueue("Request_2")
            cq.enqueue("Request_3")
            item1 = cq.dequeue()
            cq.enqueue("Request_4")
            cq.enqueue("Request_5")  # Wraps around
            res.update({
                "name": "12. Circular Queue (Ring Buffer)",
                "time_complexity": "Enqueue/Dequeue O(1)",
                "space_complexity": "O(Capacity)",
                "dequeued_item": item1,
                "current_buffer": cq.to_list(),
                "is_full": cq.is_full(),
            })
        elif c == "bfs":
            g = Graph(directed=False)
            g.add_edge("Node_A", "Node_B")
            g.add_edge("Node_A", "Node_C")
            g.add_edge("Node_B", "Node_D")
            g.add_edge("Node_C", "Node_E")
            traversal = bfs_traversal(g, "Node_A")
            res.update({
                "name": "13. Breadth-First Search (BFS)",
                "time_complexity": "O(V + E)",
                "space_complexity": "O(V)",
                "start_node": "Node_A",
                "traversal_order": traversal,
            })
        elif c == "dfs":
            g = Graph(directed=False)
            g.add_edge("Node_A", "Node_B")
            g.add_edge("Node_B", "Node_C")
            g.add_edge("Node_D", "Node_E")
            traversal = dfs_traversal(g, "Node_A")
            res.update({
                "name": "14. Depth-First Search (DFS)",
                "time_complexity": "O(V + E)",
                "space_complexity": "O(V)",
                "start_node": "Node_A",
                "traversal_order": traversal,
            })
        elif c == "consistent_hashing":
            ring = ConsistentHashingRing(virtual_nodes=50)
            ring.add_node("Node_A")
            ring.add_node("Node_B")
            ring.add_node("Node_C")
            sample_keys = [f"voter_synthetic_{i}" for i in range(12)]
            dist = ring.get_node_distribution(sample_keys)
            migrations = ring.calculate_migration(sample_keys, "Node_D")
            res.update({
                "name": "15. Consistent Hashing Ring (SHA-256 Virtual Nodes)",
                "time_complexity": "Lookup O(log(N * R)), Add/Remove O(R log(N * R))",
                "space_complexity": "O(N * R)",
                "distribution_across_nodes": dist,
                "migration_to_new_node_D": migrations,
            })
        elif c == "binary_search":
            sorted_block_indices = [0, 1, 2, 5, 8, 13, 21, 34, 55, 89]
            idx_found = binary_search(sorted_block_indices, 21)
            idx_missing = binary_search(sorted_block_indices, 99)
            res.update({
                "name": "16. Binary Search",
                "time_complexity": "O(log N)",
                "space_complexity": "O(1)",
                "array": sorted_block_indices,
                "search_21_index": idx_found,
                "search_99_missing": idx_missing,
            })
        elif c == "merge_sort":
            raw_audit_records = [
                {"id": 4, "time": 1700000040},
                {"id": 1, "time": 1700000010},
                {"id": 3, "time": 1700000030},
                {"id": 2, "time": 1700000020},
            ]
            sorted_res = merge_sort(raw_audit_records, key=lambda x: x["time"])
            res.update({
                "name": "17. Merge Sort (Divide-and-Conquer Stable Sort)",
                "time_complexity": "O(N log N) in all cases",
                "space_complexity": "O(N)",
                "sorted_output": sorted_res,
            })
        elif c == "quick_sort":
            raw_scores = [42, 17, 88, 17, 3, 99, 54, 76]
            sorted_scores = quick_sort(raw_scores)
            res.update({
                "name": "18. Quick Sort (Median-of-Three Pivot)",
                "time_complexity": "Average O(N log N), Space O(log N)",
                "input": raw_scores,
                "sorted_output": sorted_scores,
            })
        elif c == "dijkstra":
            g = Graph(directed=False)
            g.add_edge("Node_A", "Node_B", weight=10.0)
            g.add_edge("Node_B", "Node_C", weight=5.0)
            g.add_edge("Node_A", "Node_C", weight=25.0)
            g.add_edge("Node_C", "Node_D", weight=8.0)
            distances, predecessors = dijkstra_shortest_path(g, "Node_A")
            res.update({
                "name": "19. Dijkstra's Shortest Path Algorithm",
                "time_complexity": "O((V + E) log V)",
                "space_complexity": "O(V)",
                "shortest_distances_from_Node_A": distances,
            })
        elif c == "topological_sort":
            g = Graph(directed=True)
            g.add_edge("1_Voter_Auth", "2_Token_Redeem")
            g.add_edge("2_Token_Redeem", "3_Mempool_Queue")
            g.add_edge("3_Mempool_Queue", "4_Block_Proposal")
            g.add_edge("4_Block_Proposal", "5_Consensus_Commit")
            order = topological_sort(g)
            res.update({
                "name": "20. Topological Sort (Dependency DAG)",
                "time_complexity": "O(V + E)",
                "space_complexity": "O(V)",
                "pipeline_execution_order": order,
            })
        elif c == "merkle_tree":
            leaves = ["tx_hash_1", "tx_hash_2", "tx_hash_3", "tx_hash_4"]
            tree = MerkleTree(leaves)
            proof = tree.get_proof(1)
            verified = MerkleTree.verify_proof(tree.leaves[1], proof, tree.root)
            res.update({
                "name": "21. Merkle Tree (Inclusion Proofs)",
                "time_complexity": "Build O(N), Proof Verify O(log N)",
                "space_complexity": "O(N)",
                "merkle_root": tree.root,
                "leaf_1_proof": [p.to_dict() for p in proof],
                "proof_verified": verified,
            })
        elif c == "sha256" or c == "hashing":
            sample_data = {"election": "2026", "candidate": "Alice Johnson", "nonce": 12345}
            h1 = sha256_hash(sample_data)
            sample_data_tampered = {"election": "2026", "candidate": "Alice Johnson", "nonce": 12346}
            h2 = sha256_hash(sample_data_tampered)
            res.update({
                "name": "22. SHA-256 Cryptographic Hashing",
                "time_complexity": "O(M) message bytes",
                "space_complexity": "O(1) 256 bits",
                "original_hash": h1,
                "tampered_hash": h2,
                "avalanche_effect_detected": h1 != h2,
            })
        elif c == "digital_signatures":
            kp = KeyPair.generate()
            msg = {"vote": "cand_1", "voter_token_hash": "a1b2c3..."}
            sig = kp.sign(msg)
            valid = verify_signature(kp.get_public_pem(), msg, sig)
            invalid = verify_signature(kp.get_public_pem(), {"vote": "cand_tampered"}, sig)
            res.update({
                "name": "23. ECDSA Digital Signatures (SECP256R1)",
                "time_complexity": "O(1) ECC scalar mult",
                "space_complexity": "256-bit key",
                "signature": sig[:32] + "...",
                "valid_signature_check": valid,
                "tampered_payload_check": invalid,
            })
        elif c == "hash_set":
            hs = HashSet()
            added1 = hs.add("auth_token_999")
            added2 = hs.add("auth_token_999")  # Duplicate!
            res.update({
                "name": "24. Hash Set for Duplicate Detection",
                "time_complexity": "O(1) average lookup/insert",
                "space_complexity": "O(N)",
                "first_insert_success": added1,
                "duplicate_insert_detected": (not added2),
                "total_unique_items": len(hs),
            })
        elif c == "cycle_detection":
            g_cyclic = Graph(directed=True)
            g_cyclic.add_edge("A", "B")
            g_cyclic.add_edge("B", "C")
            g_cyclic.add_edge("C", "A")
            has_cycle, cycle_path = detect_cycle_directed(g_cyclic)
            res.update({
                "name": "25. Graph Cycle Detection (3-Color DFS)",
                "time_complexity": "O(V + E)",
                "space_complexity": "O(V)",
                "graph_edges": g_cyclic.get_edges(),
                "cycle_detected": has_cycle,
                "cycle_path": cycle_path,
            })
        else:
            return jsonify({"error": f"Unknown concept '{concept_name}'"}), 404

        return jsonify(res)

    # --- Web Dashboard UI Route ---
    @app.route("/", methods=["GET"])
    def dashboard():
        return render_template("dashboard.html", node=node)

    return app
