# Comprehensive Data Structures and Algorithms (DSA) Report

This document details the **25 Data Structures and Algorithms** implemented, tested, and integrated within the **Decentralized Blockchain Voting System**.

---

## 1. Master DSA Integration Table

| # | Concept Name | Category | Source Module | Integration Workflow | Time Complexity (Avg / Worst) | Space Complexity |
|---|---|---|---|---|---|---|
| **1** | **Hash Table** | Structure | `src/dsa/hash_table.py` | In-memory voter lookups, local metadata caching, O(1) duplicate checks | $O(1) \ / \ O(N)$ | $O(N + M)$ |
| **2** | **Singly Linked List** | Structure | `src/dsa/singly_linked_list.py` | Sequential block linkage demonstration & forward chain traversal | $O(1)$ append $\ / \ O(N)$ search | $O(N)$ |
| **3** | **Doubly Linked List** | Structure | `src/dsa/doubly_linked_list.py` | Bidirectional block explorer navigation & in-memory audit logs | $O(1)$ insert $\ / \ O(N)$ traversal | $O(N)$ |
| **4** | **Stack** | Structure | `src/dsa/stack.py` | LIFO block verification state back-tracing & validation frames | $O(1)$ push/pop $\ / \ O(1)$ | $O(N)$ |
| **5** | **Queue** | Structure | `src/dsa/queue.py` | FIFO Mempool ordering for pending ballot transactions | $O(1)$ enqueue $\ / \ O(1)$ dequeue | $O(N)$ |
| **6** | **Priority Queue / Heap** | Structure | `src/dsa/priority_queue.py` | Min-heap peer synchronization & reconnection retry task scheduler | $O(\log N)$ push/pop | $O(N)$ |
| **7** | **Binary Search Tree** | Structure | `src/dsa/binary_search_tree.py` | Fast ordered index for block heights and audit log timestamps | $O(\log N) \ / \ O(N)$ | $O(N)$ |
| **8** | **AVL Tree** | Structure | `src/dsa/avl_tree.py` | Self-balancing tree guaranteeing logarithmic block lookup | $O(\log N) \ / \ O(\log N)$ | $O(N)$ |
| **9** | **Trie** | Structure | `src/dsa/trie.py` | Instant prefix autocompletion for candidates and voter search | $O(L + K)$ prefix search | $O(\Sigma \cdot L \cdot N)$ |
| **10** | **Graph (Adj Lists)** | Structure | `src/dsa/graph.py` | Physical/virtual peer network topology representation | $O(1)$ edge add $\ / \ O(\text{deg}(V))$ | $O(V + E)$ |
| **11** | **Union-Find (DSU)** | Structure | `src/dsa/union_find.py` | Path compression & rank for network partition analysis | $O(\alpha(N))$ nearly $O(1)$ | $O(N)$ |
| **12** | **Circular Queue** | Structure | `src/dsa/circular_queue.py` | Bounded ring buffer for incoming HTTP request flood control | $O(1)$ enqueue/dequeue | $O(K)$ |
| **13** | **Breadth-First Search** | Algorithm | `src/dsa/bfs.py` | Peer discovery across hop layers & unweighted shortest path | $O(V + E)$ | $O(V)$ |
| **14** | **Depth-First Search** | Algorithm | `src/dsa/dfs.py` | Peer component enumeration & deep network topology analysis | $O(V + E)$ | $O(V)$ |
| **15** | **Consistent Hashing** | Algorithm | `src/dsa/consistent_hashing.py` | SHA-256 virtual node ring for distributed sharding and record routing | $O(\log(N \cdot R))$ lookup | $O(N \cdot R)$ |
| **16** | **Binary Search** | Algorithm | `src/dsa/binary_search.py` | Logarithmic search over sorted block heights and audit snapshots | $O(\log N)$ | $O(1)$ |
| **17** | **Merge Sort** | Algorithm | `src/dsa/merge_sort.py` | Divide-and-conquer stable sorting for audit event timestamps | $O(N \log N)$ all cases | $O(N)$ |
| **18** | **Quick Sort** | Algorithm | `src/dsa/quick_sort.py` | Median-of-three pivot sorting for candidate tallies and latency ranking | $O(N \log N) \ / \ O(N^2)$ | $O(\log N)$ |
| **19** | **Dijkstra's Algorithm** | Algorithm | `src/dsa/dijkstra.py` | Minimum-latency routing across weighted peer network links | $O((V + E) \log V)$ | $O(V)$ |
| **20** | **Topological Sort** | Algorithm | `src/dsa/topological_sort.py` | Kahn's algorithm ordering of transaction validation and block pipelines | $O(V + E)$ | $O(V)$ |
| **21** | **Merkle Tree** | Additional | `src/blockchain/merkle_tree.py` | Binary hash tree for block roots, odd-leaf promotion, inclusion proofs | $O(N)$ build $\ / \ O(\log N)$ proof | $O(N)$ |
| **22** | **SHA-256 Hashing** | Additional | `src/security/hashing.py` | Canonical deterministic serialization & block tampering detection | $O(M)$ message bytes | $O(1)$ |
| **23** | **Digital Signatures** | Additional | `src/security/digital_signatures.py` | ECDSA (SECP256R1) signing of block proposals and consensus envelopes | $O(1)$ ECC scalar mult | $O(1)$ |
| **24** | **Hash Set** | Additional | `src/dsa/hash_set.py` | In-memory duplicate transaction detection & token reuse prevention | $O(1)$ average | $O(N)$ |
| **25** | **Cycle Detection** | Additional | `src/dsa/cycle_detection.py` | 3-Color DFS directed loop detection & undirected graph cycles | $O(V + E)$ | $O(V)$ |

---

## 2. Empirical Benchmark Measurements

Benchmarks executed on Apple Silicon (Python 3.13):

### A. Custom Hash Table Operations
| Records (N) | Insert Time (ms) | Search Time (ms) | Avg Search Latency ($\mu$s/key) |
|---|---|---|---|
| **100** | 0.35 ms | 0.10 ms | 1.0 $\mu$s |
| **1,000** | 3.97 ms | 1.14 ms | 1.14 $\mu$s |
| **5,000** | 20.58 ms | 7.32 ms | 1.46 $\mu$s |

*Observation:* Search time scales linearly with $N$ due to constant-time bucket lookups with load-factor dynamic resizing.

### B. Consistent Hashing Record Routing (SHA-256, 50 Replicas)
| Record Keys (N) | Total Routing Time (ms) | Routing Rate ($\mu$s/key) | Throughput (keys/sec) |
|---|---|---|---|
| **100** | 0.20 ms | 2.00 $\mu$s | ~500,000 / sec |
| **1,000** | 1.89 ms | 1.89 $\mu$s | ~529,000 / sec |
| **5,000** | 6.75 ms | 1.35 $\mu$s | ~740,000 / sec |

*Observation:* Binary search on ring tokens (`bisect_right`) ensures sub-2-microsecond routing decisions for arbitrary keys.

### C. Binary Merkle Tree Construction & Inclusion Proof Verification
| Leaves (Transactions) | Tree Construction (ms) | Proof Generation (ms) | Proof Verification (ms) | Verified Status |
|---|---|---|---|---|
| **16** | 0.08 ms | 0.015 ms | 0.025 ms | **True** |
| **64** | 0.11 ms | 0.012 ms | 0.019 ms | **True** |
| **256** | 0.40 ms | 0.014 ms | 0.019 ms | **True** |
| **1,024** | 1.96 ms | 0.018 ms | 0.026 ms | **True** |

*Observation:* Verification time remains constant at $\approx 0.02$ milliseconds even as transaction count increases by a factor of 64, demonstrating logarithmic proof scaling $O(\log N)$.

### D. Sorting Comparison (Merge Sort vs Quick Sort with Median-of-Three)
| Dataset Size (N) | Merge Sort (ms) | Quick Sort (ms) | Speedup Ratio |
|---|---|---|---|
| **100** | 0.61 ms | 0.18 ms | 3.3x |
| **1,000** | 4.24 ms | 1.71 ms | 2.5x |
| **5,000** | 18.29 ms | 9.83 ms | 1.9x |

*Observation:* Quick Sort demonstrates faster raw in-memory throughput due to in-place median-of-three partitioning, while Merge Sort guarantees stability for timestamps.

---

## 3. Security Assumptions & Known Limitations

1. **Educational Trust Model**: Consensus is based on a leader-quorum protocol with $N=3$ and quorum $Q=2$. It operates safely under crash-recovery assumptions. It does not claim Byzantine fault tolerance against malicious colluding leaders.
2. **Ballot Privacy Mechanism**: Voter eligibility is decoupled from candidate selection via single-use authorization tokens. While this prevents candidate selections from being recorded alongside voter IDs in publicly verifiable blocks, true election-grade anonymity in hostile environments requires zero-knowledge proofs (e.g. zk-SNARKs) and mix-nets.
3. **Network Perimeter**: By default, node HTTP endpoints bind to local interfaces (`127.0.0.1`). When deployed across physical LAN computers, firewall rules and TLS reverse proxies must protect node ports.
