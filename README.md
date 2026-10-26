# Decentralized Blockchain Voting System

A production-grade educational **Decentralized Voting System** combining **Blockchain technology**, **25 Data Structures and Algorithms (DSA)**, and **Peer-to-Peer Networking**.

The system partitions records across multiple computers, validates ballots, prevents duplicate votes, enforces blockchain integrity, and tallies election results through a leader-quorum consensus protocol.

---

## Table of Contents
1. [Project Objectives](#1-project-objectives)
2. [System Architecture & Deployment Modes](#2-system-architecture--deployment-modes)
3. [Blockchain & Cryptographic Design](#3-blockchain--cryptographic-design)
4. [Distributed Record Sharding & Consistent Hashing](#4-distributed-record-sharding--consistent-hashing)
5. [Consensus Protocol & Failure Handling](#5-consensus-protocol--failure-handling)
6. [Decoupled Anonymous Ballot Workflow](#6-decoupled-anonymous-ballot-workflow)
7. [The 25 Data Structures & Algorithms (DSA)](#7-the-25-data-structures--algorithms-dsa)
8. [Installation & Setup](#8-installation--setup)
9. [Local 3-Node Simulation](#9-local-3-node-simulation)
10. [Physical Multi-Computer LAN Deployment](#10-physical-multi-computer-lan-deployment)
11. [HTTP API Endpoint Documentation](#11-http-api-endpoint-documentation)
12. [Web Dashboard Usage](#12-web-dashboard-usage)
13. [Automated Testing & 20-Step Demonstration](#13-automated-testing--20-step-demonstration)
14. [Security Assumptions & Limitations](#14-security-assumptions--limitations)

---

## 1. Project Objectives
- **Distribute records across multiple independent computers** instead of a central database.
- **Implement 25 distinct DSA concepts** with complete source modules, empirical benchmarks, and unit tests.
- **Enforce one accepted ballot per eligible voter** using memory HashSets and atomic SQLite uniqueness constraints.
- **Ensure ballot privacy** by decoupling voter authentication from candidate selection.
- **Maintain cryptographic auditability** using SHA-256 blocks, Merkle inclusion proofs, and ECDSA digital signatures.

---

## 2. System Architecture & Deployment Modes

The system consists of three logical nodes:
- **Node A (Computer A)**: Genesis coordinator & consensus proposer.
- **Node B (Computer B)**: Peer validator & shard replica.
- **Node C (Computer C)**: Peer validator & shard replica.

Each node runs its own:
- Dedicated Python process.
- Isolated SQLite database (`data/node_a/node_a.db`, `data/node_b/node_b.db`, etc.).
- Independent blockchain ledger.
- Dedicated Mempool FIFO Queue.
- Unique ECDSA keypair for signing block proposals and votes.

### Deployment Mode A: Single-Laptop 3-Node Simulation
Runs three concurrent processes on localhost:
- **Node A**: `http://127.0.0.1:5001`
- **Node B**: `http://127.0.0.1:5002`
- **Node C**: `http://127.0.0.1:5003`

### Deployment Mode B: Multiple Physical Computers over Wi-Fi / LAN
Each physical laptop runs one node and binds to `0.0.0.0`.
Configure peer LAN IP addresses in `config.yaml`:
```yaml
network:
  nodes:
    node_a:
      host: "192.168.1.10"
      port: 5001
      peers: ["http://192.168.1.11:5002", "http://192.168.1.12:5003"]
```

---

## 3. Blockchain & Cryptographic Design

Each block contains:
```json
{
  "index": 1,
  "timestamp": 1792479776.06,
  "previous_hash": "e0af1368b141fa70...",
  "current_hash": "bee9a7f37d61eb23...",
  "merkle_root": "965a359fa0e366e4...",
  "node_id": "node_a",
  "shard_id": "node_a",
  "version": 1,
  "transactions": [...]
}
```

- **Deterministic Serialization**: Block headers are serialized canonically (sorted keys, compact separators, UTF-8) before computing SHA-256.
- **Merkle Tree Inclusion Receipts**: Every committed transaction has an $O(\log N)$ inclusion path enabling voters to verify inclusion without exposing ballot data.
- **Canonical Genesis Block**: All nodes share an identical canonical genesis block (`index=0`, `timestamp=1700000000.0`, `previous_hash="0"*64`).

---

## 4. Distributed Record Sharding & Consistent Hashing

A cryptographic **Consistent Hashing Ring** with 50 virtual nodes per physical computer is implemented in `src/dsa/consistent_hashing.py`:
- Calculates `sha256(key)` mapped onto the integer ring $[0, 2^{256} - 1]$.
- Uses binary search (`bisect_right`) to find the responsible node in $O(\log(N \cdot R))$ time.
- Handles node additions and departures: only $K / N$ keys are reassigned during membership changes, preventing full-network reshuffling.

---

## 5. Consensus Protocol & Failure Handling

Implemented in `src/networking/consensus.py`:
1. **Block Proposal**: The leader gathers pending mempool transactions, constructs a candidate block, and signs its SHA-256 hash.
2. **Independent Follower Validation**: Receiving nodes verify previous-hash linkage, recalculated Merkle roots, and unspent transaction validity.
3. **Quorum Acceptance**: Followers return signed endorsements. A quorum threshold ($Q \ge 2$ out of 3 nodes) is required.
4. **Commit Broadcast**: If quorum is met, the leader commits the block and broadcasts a commit command to peers.
5. **Partition Safety**: If fewer than $Q$ nodes respond, consensus fails safely, transactions remain in the pending mempool, and no invalid block is committed.

---

## 6. Decoupled Anonymous Ballot Workflow

To prevent linking a voter's real identity to their candidate choice:
1. **Authentication**: Synthetic voter logs in with `(voter_id, password)`. Password is checked against PBKDF2-HMAC-SHA256 hash with salt.
2. **Single-Use Token**: If eligible, the system issues a cryptographically random token and records `sha256(token)` in `voting_authorizations` with a `UNIQUE(voter_id, election_id)` database constraint.
3. **Ballot Submission**: The voter submits `(candidate_id, authorization_token)` **without** attaching their `voter_id`.
4. **Atomic Redemption**: The system consumes `sha256(token)` atomically.
5. **Blockchain Inclusion**: The block only records `(transaction_id, token_hash, candidate_id, timestamp)`. `voter_id` is never recorded in blocks!

---

## 7. The 25 Data Structures & Algorithms (DSA)

| # | Concept | Module | Complexity | Application in System |
|---|---|---|---|---|
| 1 | **Hash Table** | `src/dsa/hash_table.py` | $O(1)$ avg / $O(N)$ worst | Separate-chaining voter and transaction lookup |
| 2 | **Singly Linked List** | `src/dsa/singly_linked_list.py` | $O(1)$ append / $O(N)$ search | Forward sequential block chain traversal |
| 3 | **Doubly Linked List** | `src/dsa/doubly_linked_list.py` | $O(1)$ insert / $O(N)$ walk | Bidirectional audit log and transaction history viewer |
| 4 | **Stack** | `src/dsa/stack.py` | $O(1)$ push/pop | LIFO block verification and rollback traversal |
| 5 | **Queue** | `src/dsa/queue.py` | $O(1)$ amortized | FIFO Mempool ordering for pending ballot transactions |
| 6 | **Priority Queue** | `src/dsa/priority_queue.py` | $O(\log N)$ push/pop | Min-heap peer synchronization & retry job scheduler |
| 7 | **Binary Search Tree** | `src/dsa/binary_search_tree.py` | $O(\log N)$ avg / $O(N)$ | Ordered block index and audit snapshot lookup |
| 8 | **AVL Tree** | `src/dsa/avl_tree.py` | $O(\log N)$ guaranteed | Self-balancing tree with LL, RR, LR, RL rotations |
| 9 | **Trie** | `src/dsa/trie.py` | $O(L + K)$ prefix | Autocomplete for candidate names and voter IDs |
| 10 | **Graph** | `src/dsa/graph.py` | $O(V + E)$ space | Adjacency list representation of peer network topology |
| 11 | **Union-Find** | `src/dsa/union_find.py` | $O(\alpha(N))$ amortized | Disjoint set union for network partition analysis |
| 12 | **Circular Queue** | `src/dsa/circular_queue.py` | $O(1)$ ring buffer | Bounded HTTP request buffer to prevent flood attacks |
| 13 | **BFS** | `src/dsa/bfs.py` | $O(V + E)$ | Layered peer discovery and shortest-hop routing |
| 14 | **DFS** | `src/dsa/dfs.py` | $O(V + E)$ | Network component enumeration and deep connectivity |
| 15 | **Consistent Hashing** | `src/dsa/consistent_hashing.py` | $O(\log(N \cdot R))$ | Virtual node ring for deterministic record sharding |
| 16 | **Binary Search** | `src/dsa/binary_search.py` | $O(\log N)$ | Logarithmic search over sorted block indices |
| 17 | **Merge Sort** | `src/dsa/merge_sort.py` | $O(N \log N)$ stable | Divide-and-conquer stable sorting for audit timestamps |
| 18 | **Quick Sort** | `src/dsa/quick_sort.py` | $O(N \log N)$ avg | Median-of-three pivot sorting for candidate tallies |
| 19 | **Dijkstra** | `src/dsa/dijkstra.py` | $O((V + E) \log V)$ | Shortest latency route computation across peer links |
| 20 | **Topological Sort** | `src/dsa/topological_sort.py` | $O(V + E)$ | Kahn's algorithm ordering of transaction validation DAG |
| 21 | **Merkle Tree** | `src/blockchain/merkle_tree.py` | $O(N)$ build / $O(\log N)$ | Binary inclusion proofs with odd-leaf duplication |
| 22 | **SHA-256** | `src/security/hashing.py` | $O(M)$ message bytes | Cryptographic tampering detection & block hashing |
| 23 | **Digital Signatures** | `src/security/digital_signatures.py` | $O(1)$ ECC scalar mult | ECDSA (SECP256R1) signing of block envelopes |
| 24 | **Hash Set** | `src/dsa/hash_set.py` | $O(1)$ avg | O(1) in-memory duplicate vote and token detection |
| 25 | **Cycle Detection** | `src/dsa/cycle_detection.py` | $O(V + E)$ | 3-Color DFS directed loop detection in dependency graphs |

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.13)
- `pip` package manager

### Install Dependencies
```bash
# macOS / Linux
python3 -m pip install -r requirements.txt

# Windows
python -m pip install -r requirements.txt
```

---

## 9. Local 3-Node Simulation

### Start All 3 Nodes Concurrently
```bash
# Starts Node A (5001), Node B (5002), and Node C (5003) in the background:
python3 scripts/start_local_network.py
```
To stop all nodes, press `Ctrl+C`.

### Start Individual Nodes Manually
In separate terminal windows:
```bash
# Terminal 1: Node A
python3 app.py --node-id node_a --port 5001

# Terminal 2: Node B
python3 app.py --node-id node_b --port 5002

# Terminal 3: Node C
python3 app.py --node-id node_c --port 5003
```

### Pre-Register Demo Synthetic Voters
```bash
python3 scripts/register_demo_voters.py http://127.0.0.1:5001
```

### Voter Portal Web UI (`voting_ui.py`)
Launch the dedicated voter registration and ballot-casting portal:
```bash
python3 voting_ui.py
# Opens at: http://127.0.0.1:5050/
```
Features:
- **Registration (`/register`)**: Register voter with Voter ID, full name, unique email, and PBKDF2-HMAC-SHA256 password hashing.
- **Login (`/login`)**: Authenticate by voter ID or email with secure session fixation protection.
- **Vote (`/vote`)**: Select certified election candidates with interactive confirmation modal and atomic single-use authorization token burn.
- **Receipt (`/confirmation/<tx_id>`)**: Verifiable cryptographic receipt with Merkle tree inclusion audit widget.
- **Results (`/results`)**: Live candidate distribution tallies and ledger integrity verification.

---

## 10. Physical Multi-Computer LAN Deployment

### Setup Instructions
1. Connect all computers to the same Wi-Fi router or Ethernet switch.
2. Determine each computer's LAN IP address:
   - macOS / Linux: `ifconfig` or `ip a` (e.g. `192.168.1.10`)
   - Windows: `ipconfig` (e.g. `192.168.1.11`)
3. Ensure firewalls allow incoming TCP connections on ports 5001, 5002, 5003.
4. On **Computer A**:
   ```bash
   python3 app.py --node-id node_a --host 0.0.0.0 --port 5001 --peers http://192.168.1.11:5002 http://192.168.1.12:5003
   ```
5. On **Computer B**:
   ```bash
   python3 app.py --node-id node_b --host 0.0.0.0 --port 5002 --peers http://192.168.1.10:5001 http://192.168.1.12:5003
   ```
6. On **Computer C**:
   ```bash
   python3 app.py --node-id node_c --host 0.0.0.0 --port 5003 --peers http://192.168.1.10:5001 http://192.168.1.11:5002
   ```

---

## 11. HTTP API Endpoint Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Node health status, block height, and tip hash |
| `GET` | `/api/node_info` | Detailed node status, mempool size, and stored records |
| `GET` | `/api/peers` | Discovered peer endpoints and latency measurements |
| `GET` | `/api/topology` | Network topology analytics (BFS, DFS, Dijkstra, Union-Find) |
| `POST` | `/api/voter/register` | Register a synthetic voter (`voter_id`, `name`, `password`) |
| `POST` | `/api/voter/auth_token` | Authenticate voter and issue single-use authorization token |
| `POST` | `/api/submit_ballot` | Submit anonymous ballot (`candidate_id`, `authorization_token`) |
| `POST` | `/api/mine` | Mine pending mempool transactions via consensus |
| `GET` | `/api/chain` | Export full blockchain with cryptographic integrity verification |
| `GET` | `/api/block/<index>` | Retrieve block by index |
| `GET` | `/api/merkle_proof/<tx_id>` | Generate Merkle inclusion proof for a committed ballot |
| `POST` | `/api/verify_receipt` | Mathematically verify a Merkle inclusion proof |
| `POST` | `/api/sync` | Trigger peer block synchronization |
| `GET` | `/api/tally` | Calculate certified election results directly from blockchain |
| `GET` | `/api/dsa/explore/<name>` | Execute live interactive demonstration for any of the 25 DSA concepts |

---

## 12. Web Dashboard Usage

Navigate to `http://127.0.0.1:5001/` in your browser.
The dashboard features 6 interactive sections:
1. **Overview**: Real-time block height, mempool count, accepted ballots, and election controls.
2. **Node Network**: Peer statuses, live round-trip latency, and graph analytics (BFS, DFS, Dijkstra).
3. **Voter Portal**: Authenticate demo voters, receive decoupled tokens, and submit anonymous ballots.
4. **Blockchain Explorer**: Inspect mined blocks, view transactions, and verify chain integrity.
5. **DSA Explorer**: Interactive live runner for all 25 Data Structures and Algorithms with real outputs.
6. **Election Results**: Live candidate vote counts, progress bars, and audit verification.

---

## 13. Automated Testing & 20-Step Demonstration

### Run Complete Pytest Suite (43 Tests)
```bash
pytest -v
```
All 43 unit, integration, and security tests execute in $< 1.0$ second.

### Run Automated 20-Step End-to-End Demonstration
```bash
python3 scripts/run_demo.py
```
This script launches 3 nodes, registers voters, submits ballots, rejects duplicate votes, commits blocks via consensus, verifies Merkle inclusion proofs, simulates a node crash and recovery, synchronizes records, tallies results, and executes live demonstrations of all 25 DSA concepts.

---

## 14. Security Assumptions & Limitations

- **Educational Nature**: Designed for educational demonstration and computer science pedagogy; not a certified national election system.
- **Consensus**: Implements a leader-quorum protocol ($N=3$, $Q=2$) that assumes crash-fault tolerance.
- **Ballot Anonymity**: Decouples voter identity from candidate choice using single-use authorization tokens. Production environments require Zero-Knowledge Proofs (e.g. zk-SNARKs) and mix-nets to prevent traffic analysis attacks.
