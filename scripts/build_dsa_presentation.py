"""
Build an academic presentation (.pptx) adhering to 23AID205 Project Guidelines,
incorporating all 4 team members, 25 DSA modules, and high-resolution architectural images.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PPTX = "Decentralized_Blockchain_Voting_System_DSA.pptx"
ASSETS_DIR = "presentation_assets"

# Color Palette
COLOR_BG = RGBColor(11, 15, 25)         # #0B0F19
COLOR_CARD = RGBColor(19, 28, 46)       # #131C2E
COLOR_BORDER = RGBColor(31, 46, 71)     # #1F2E47
COLOR_CYAN = RGBColor(0, 240, 255)      # #00F0FF
COLOR_EMERALD = RGBColor(16, 185, 129)  # #10B981
COLOR_AMBER = RGBColor(245, 158, 11)    # #F59E0B
COLOR_PURPLE = RGBColor(168, 85, 247)   # #A855F7
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_MUTED = RGBColor(148, 163, 184)   # #94A3B8
COLOR_CARD_DARK = RGBColor(15, 23, 42)  # #0F172A

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_bg(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG

def add_header(slide, section_tag, title_text):
    # Section Tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = section_tag.upper()
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

def add_card(slide, left, top, width, height, title, items, border_color=COLOR_BORDER, title_color=COLOR_CYAN):
    # Card Background Shape
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)

    # Card Content Text Box
    pad = Inches(0.18)
    tb = slide.shapes.add_textbox(left + pad, top + pad, width - (2 * pad), height - (2 * pad))
    tf = tb.text_frame
    tf.word_wrap = True

    # Title paragraph
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = title_color
    p0.space_after = Pt(8)

    # Items
    for item in items:
        p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(4)
        if item.startswith("•") or item.startswith("-"):
            p.font.size = Pt(10)
            p.font.color.rgb = RGBColor(226, 232, 240)

# ==============================================================================
# Slide 1: Title Slide (with all 4 Team Members)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_bg(s1)

# Super Header
sh_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(0.4))
sh_p = sh_box.text_frame.paragraphs[0]
sh_p.text = "2025.R.AID.1.23AID205 — DATA STRUCTURES & ALGORITHMS CAPSTONE REVIEW"
sh_p.font.size = Pt(11)
sh_p.font.bold = True
sh_p.font.color.rgb = COLOR_CYAN

# Main Title
t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.25), Inches(11.333), Inches(1.2))
t_p = t_box.text_frame.paragraphs[0]
t_p.text = "Decentralized Blockchain Voting System"
t_p.font.size = Pt(32)
t_p.font.bold = True
t_p.font.color.rgb = COLOR_WHITE

# Subtitle
sub_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(0.6))
sub_p = sub_box.text_frame.paragraphs[0]
sub_p.text = "A Zero-Trust Electronic Voting Architecture Engineered with 25 Native Data Structures & Algorithms"
sub_p.font.size = Pt(14)
sub_p.font.color.rgb = COLOR_EMERALD

# 4 Team Members Cards
members = [
    ("Ashwin Krishna V", "cb.ai.u4aid25108", "DSA & Verification Lead", COLOR_CYAN),
    ("Madhan S", "cb.ai.u4aid25127", "Consensus & P2P Architect", COLOR_EMERALD),
    ("Nakul Shravan", "cb.ai.u4aid25134", "Cryptographic Hashing & Merkle", COLOR_AMBER),
    ("Nawin K G", "cb.ai.u4aid25135", "System Architect & UI Lead", COLOR_PURPLE)
]

for idx, (m_name, m_roll, m_role, m_col) in enumerate(members):
    c_left = Inches(1.0 + idx * 2.9)
    shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, Inches(3.2), Inches(2.65), Inches(2.3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD
    shape.line.color.rgb = m_col
    shape.line.width = Pt(1.5)

    tb = s1.shapes.add_textbox(c_left + Inches(0.15), Inches(3.35), Inches(2.35), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = m_name
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_WHITE

    p1 = tf.add_paragraph()
    p1.text = m_roll
    p1.font.size = Pt(10)
    p1.font.color.rgb = m_col
    p1.font.bold = True
    p1.space_before = Pt(4)

    p2 = tf.add_paragraph()
    p2.text = m_role
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = COLOR_MUTED
    p2.space_before = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "Amrita Vishwa Vidyapeetham"
    p3.font.size = Pt(8.5)
    p3.font.color.rgb = RGBColor(100, 116, 139)
    p3.space_before = Pt(4)

# Footer metadata banner
foot = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.85), Inches(11.333), Inches(0.95))
foot.fill.solid()
foot.fill.fore_color.rgb = COLOR_CARD_DARK
foot.line.color.rgb = COLOR_BORDER

tb_f = s1.shapes.add_textbox(Inches(1.2), Inches(5.95), Inches(11.0), Inches(0.75))
tf_f = tb_f.text_frame
tf_f.word_wrap = True
pf = tf_f.paragraphs[0]
pf.text = "Repository: https://github.com/kgnawinkg-tech/Decentralised-Voting-System  |  Email: kgnawinkg@gmail.com"
pf.font.size = Pt(11)
pf.font.color.rgb = COLOR_CYAN
pf.font.bold = True

pf2 = tf_f.add_paragraph()
pf2.text = "Scope: 25 Master DSA Modules  •  Zero 3rd-Party Blockchain Frameworks  •  Pure Python 3.13  •  Multi-Node Consensus"
pf2.font.size = Pt(9.5)
pf2.font.color.rgb = COLOR_MUTED
pf2.space_before = Pt(3)

# ==============================================================================
# Slide 2: Guideline Section B.I — Introduction & Motivation
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2)
add_header(s2, "Guideline Section B.I", "1. Introduction & Motivation: The Electronic Voting Trust Crisis")

add_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "The Centralized Failure",
         ["• Single Point of Failure (SPOF): Central voting databases are vulnerable to internal tampering, unauthorized SQL overrides, and DDoS attacks.",
          "• Black-Box Opaque Counting: Voters receive no mathematical proof that their ballot was correctly counted or unaltered.",
          "• Coercion & Privacy Conflict: Existing e-voting platforms link voter credentials directly to ballots, creating identity leak risks.",
          "• Administrative Monopoly: Centralized election servers grant root admins unilateral control over tallies."],
         border_color=RGBColor(239, 68, 68), title_color=RGBColor(248, 113, 113))

add_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Why DSA Over AI/ML?",
         ["• Mathematical Determinism: AI/ML models are probabilistic, approximate, and non-deterministic—unacceptable for elections.",
          "• Absolute Audit Guarantees: DSA structures (Hash Tables, Doubly Linked Lists, Merkle Trees) enforce rigorous mathematical proof.",
          "• Cryptographic Integrity: Altering 1 bit changes the SHA-256 hash completely; detected in O(1) step.",
          "• Provable Big-O Complexity: Every operation has hard theoretical time and memory bounds proven mathematically."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s2, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "The Decentralized Solution",
         ["• Multi-Node P2P Consensus: Independent nodes (A, B, C) cross-validate every block using Quorum rules (Q = 2/3).",
          "• Decoupled Token Anonymity: Voter eligibility is separated from ballot choices via single-use burned authorization tokens.",
          "• Merkle Audit Receipts: Voters receive an O(log N) cryptographic proof to audit their ballot from any mobile device.",
          "• 100% Native Implementation: Built from first principles in Python 3.13 without heavy external blockchain bloat."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

# ==============================================================================
# Slide 3: Guideline Section B.II — Problem Statement & Real-World Relevance
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_bg(s3)
add_header(s3, "Guideline Section B.II", "2. Problem Statement & Real-World Architectural Relevance")

add_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Formal Problem Statement",
         ["Engineering a transparent, secure, and decentralized electronic voting infrastructure that simultaneously guarantees:",
          "1. Strict Single-Vote Invariance: No voter can cast more than one ballot, even across concurrent requests or multi-node race conditions.",
          "2. Complete Ballot Secrecy: Impossible for any entity (including node administrators) to map a candidate vote back to voter identity.",
          "3. Tamper-Evident Immutability: Once confirmed, past ballots cannot be altered or removed without breaking the cryptographic chain.",
          "4. Public Verifiability: Any voter can audit that their specific ballot is included in the final tally using logarithmic proofs.",
          "5. Partition Fault Tolerance: The system functions seamlessly across network partitions as long as a quorum of peers remains active."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

add_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Real-World Relevance & Impact",
         ["• National & Municipal Elections: Eliminates accusations of ballot-box stuffing and electronic voting machine (EVM) tampering.",
          "• University & Academic Governance: Enables transparent student senate elections, faculty senate votes, and thesis evaluations.",
          "• Corporate Shareholder Proxy Voting: Protects minority shareholders from board manipulation with verifiable audit receipts.",
          "• Decentralized Autonomous Organizations (DAOs): Provides transparent governance without relying on expensive gas fees on public networks.",
          "• Educational First-Principles Reference: Proves that complex distributed ledgers can be engineered using fundamental Computer Science DSA."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 4: Guideline Section B.III — Objectives and Scope
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4)
add_header(s4, "Guideline Section B.III", "3. Project Objectives & Architectural Scope")

add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Core Technical Objectives",
         ["• Native 25-DSA Taxonomy: Implement and test 25 core data structures and algorithms covering linear, trees, graphs, and sorting.",
          "• Zero Third-Party Blockchain Dependencies: No web3.py, Ethereum, or Hyperledger. 100% custom ledger logic.",
          "• Distributed 3-Node Architecture: Independent peer nodes running on separate ports/machines with asynchronous gossip.",
          "• Sub-Millisecond Duplicate Rejection: O(1) Hash Table and atomic SQLite unique constraints rejecting double votes in < 1 µs.",
          "• Logarithmic Merkle Receipts: O(log N) inclusion proofs verified in ~0.02 ms regardless of ledger size.",
          "• Comprehensive Automated Validation: 100% test pass rate across 25 unit and integration test suites."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Project Architectural Scope",
         ["• IN SCOPE:",
          "  - P2P network simulation with Dijkstra minimum-latency routing and BFS peer discovery.",
          "  - Leader-quorum consensus protocol handling crash-recovery faults (N=3, Q=2).",
          "  - Distributed sharding via SHA-256 consistent hashing ring with 50 virtual replicas.",
          "  - Full-stack web portal for voters, live blockchain explorer, and interactive 25-DSA lab.",
          "  - LAN deployment support for multi-computer physical demonstration over Wi-Fi.",
          "• OUT OF SCOPE (Educational Trust Model):",
          "  - Byzantine fault tolerance against colluding malicious leaders (planned for PBFT upgrade).",
          "  - Hardware security modules (HSMs) and biometric voter identity binding."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

# ==============================================================================
# Slide 5: Guideline Section B.IV.1 — Input Data Representation & Schema
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_bg(s5)
add_header(s5, "Guideline Section B.IV.1", "4. Input Data Representation & Schema (DSA Perspective)")

add_card(s5, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Voter & Candidate Entities",
         ["• Voter Registry Record (Hash Table):",
          "  { voter_id: string (PK),",
          "    hashed_pin: string (SHA-256),",
          "    has_voted: boolean,",
          "    auth_token: string | null }",
          "• Candidate Registry:",
          "  { candidate_id: string (PK),",
          "    name: string,",
          "    party: string,",
          "    vote_count: integer }",
          "• Trie Prefix Structure: Fast O(L) autocompletion for voter search and ballot candidates."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s5, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Anonymous Ballot Transaction",
         ["• Ballot Data Structure (FIFO Queue):",
          "  { ballot_id: UUIDv4,",
          "    election_id: string,",
          "    candidate_id: string,",
          "    timestamp: float (UTC),",
          "    auth_token_hash: string }",
          "• Privacy Representation:",
          "  - voter_id is strictly absent from the ballot schema.",
          "  - auth_token_hash ensures the token cannot be reused, but reveals zero voter identity."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s5, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Cryptographic Block Schema",
         ["• Block Node Structure (Doubly Linked List):",
          "  { index: integer (Height),",
          "    timestamp: float,",
          "    previous_hash: string (64 hex),",
          "    merkle_root: string (64 hex),",
          "    transactions: list[Ballot],",
          "    node_id: string (Proposer),",
          "    signature: string (ECDSA),",
          "    current_hash: string (64 hex) }",
          "• Forward & Backward pointers: prev_node and next_node references."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 6: Guideline Section B.IV.2 — Data Preprocessing & Canonical Serialization
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_bg(s6)
add_header(s6, "Guideline Section B.IV.2", "5. Data Preprocessing & Canonical Serialization")

add_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Canonical JSON Serialization Pipeline",
         ["• The Serialization Challenge: Dictionaries in standard runtimes have non-deterministic key ordering. Inconsistent serialization breaks SHA-256 hash matching across nodes.",
          "• Canonical Preprocessing Algorithm:",
          "  1. Recursive key sorting: Order all JSON object keys lexicographically.",
          "  2. Strict whitespace removal: Force separators=(',', ':') to eliminate space variances.",
          "  3. UTF-8 byte encoding: Standardize text byte streams.",
          "  4. Deterministic hashing: SHA-256 digest guaranteed identical on every node regardless of OS or Python version.",
          "• Code Implementation:",
          "  canonical_bytes = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')",
          "  block_hash = hashlib.sha256(canonical_bytes).hexdigest()"],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

add_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Token Burn & Sanitization Preprocessing",
         ["• Input Sanitization (src/security/input_validation.py):",
          "  - Regex inspection prevents SQL injection, script injection, and buffer overruns.",
          "  - Strict type coercion for timestamps and election IDs.",
          "• One-Time Token Burn Lifecycle:",
          "  1. Voter requests ballot -> Authority verifies voter -> Generates cryptographically secure token.",
          "  2. Authority writes token to voter row and sets state to 'ISSUED'.",
          "  3. When voter casts ballot, token is verified, immediately marked 'BURNED', and decoupled from voter record.",
          "  4. Atomic SQLite transaction ensures token cannot be burned twice even under simultaneous concurrent threads."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

# ==============================================================================
# Slide 7: Guideline Section B.IV.3 — Exploratory Profiling & System Metrics
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_bg(s7)
add_header(s7, "Guideline Section B.IV.3", "6. Exploratory Complexity Profiling & System Metrics")

add_card(s7, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Real-Time Mempool Dynamics",
         ["• FIFO Queue Inspection: Pending transactions accumulate in a bounded queue buffer.",
          "• Rate-Limiting Circular Queue: Rejects flood spikes over 100 req/sec to prevent DDoS.",
          "• Batch Packaging: When threshold (e.g. 10 ballots) or timer expires, Mempool is drained into a new block.",
          "• Zero Dropped Transactions: Ballots remain safely in memory until quorum consensus confirms block acceptance."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s7, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Visual Block Explorer",
         ["• Live Ledger Traversal: Bidirectional exploration across block heights using Doubly Linked List pointers.",
          "• Tamper Detection Visualizer: Injects simulated bit flips into past blocks to illustrate chain verification failure.",
          "• Real-Time Quorum Tracking: Displays heartbeat pings, node health, and block height sync across Node A, B, and C.",
          "• Audit Receipt Inspector: Voters paste their Merkle proof to visually verify path traversal to Root."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s7, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "The 25-DSA Interactive Lab",
         ["• Live Laboratory Interface: Dedicated web page (templates/dsa.html) exposing all 25 algorithms live.",
          "• Interactive Triggers: Run Dijkstra path calculation, AVL tree rotations, Trie lookups, and Quick Sort in real time.",
          "• Microsecond Latency Counters: Visualizes execution duration and memory consumption on screen.",
          "• Pedagogical Tool: Bridges academic theory with functional decentralized system engineering."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 8: Guideline Section B.IV.4 — Master DSA Taxonomy (Linear & Hash Structures)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_bg(s8)
add_header(s8, "Guideline Section B.IV.4", "7. Master DSA Taxonomy: Linear & Hash Structures")

dsa_linear = [
    ("1. Hash Table", "src/dsa/hash_table.py", "O(1) Avg / O(N) Worst", "Voter registry indexing, metadata cache, token lookups"),
    ("2. Singly Linked List", "src/dsa/singly_linked_list.py", "O(1) Append / O(N) Search", "Sequential block linkage demonstration & forward ledger traversal"),
    ("3. Doubly Linked List", "src/dsa/doubly_linked_list.py", "O(1) Insert / O(N) Traversal", "Bidirectional block explorer navigation & in-memory audit logs"),
    ("4. Stack", "src/dsa/stack.py", "O(1) Push/Pop", "LIFO block verification rollback, transaction validation frames"),
    ("5. Queue (FIFO)", "src/dsa/queue.py", "O(1) Enqueue/Dequeue", "FIFO Mempool queue for fair transaction batching before mining"),
    ("6. Circular Queue", "src/dsa/circular_queue.py", "O(1) Enqueue/Dequeue", "Bounded ring buffer for HTTP request rate-limiting & flood defense")
]

for idx, (name, path, comp, use) in enumerate(dsa_linear):
    col_idx = idx % 3
    row_idx = idx // 3
    left = Inches(0.8 + col_idx * 4.0)
    top = Inches(1.6 + row_idx * 2.65)
    add_card(s8, left, top, Inches(3.7), Inches(2.45), name,
             [f"File: {path}", f"Complexity: {comp}", f"Role: {use}"],
             border_color=COLOR_CYAN, title_color=COLOR_CYAN)

# ==============================================================================
# Slide 9: Guideline Section B.IV.4 — Master DSA Taxonomy (Trees & Priority Queues)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9)
add_header(s9, "Guideline Section B.IV.4", "8. Master DSA Taxonomy: Trees, Tries & Priority Queues")

dsa_trees = [
    ("7. Binary Search Tree", "src/dsa/binary_search_tree.py", "O(log N) Avg / O(N) Worst", "Ordered index for block heights and audit log timestamps"),
    ("8. AVL Tree", "src/dsa/avl_tree.py", "O(log N) Guaranteed", "Self-balancing tree guaranteeing logarithmic block lookup via rotations"),
    ("9. Trie", "src/dsa/trie.py", "O(L + K) Prefix Search", "Instant prefix autocompletion for candidate selection and voter search"),
    ("10. Priority Queue (Heap)", "src/dsa/priority_queue.py", "O(log N) Push/Pop", "Min-heap peer synchronization & reconnection retry task scheduler"),
    ("11. Binary Merkle Tree", "src/blockchain/merkle_tree.py", "O(N) Build / O(log N) Proof", "Cryptographic root hashing and zero-knowledge inclusion proofs"),
    ("12. Consistent Hash Ring", "src/dsa/consistent_hashing.py", "O(log(N·R)) Lookup", "SHA-256 virtual node ring for balanced distributed sharding")
]

for idx, (name, path, comp, use) in enumerate(dsa_trees):
    col_idx = idx % 3
    row_idx = idx // 3
    left = Inches(0.8 + col_idx * 4.0)
    top = Inches(1.6 + row_idx * 2.65)
    add_card(s9, left, top, Inches(3.7), Inches(2.45), name,
             [f"File: {path}", f"Complexity: {comp}", f"Role: {use}"],
             border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 10: Guideline Section B.IV.4 — Master DSA Taxonomy (Graphs & Sorting)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10)
add_header(s10, "Guideline Section B.IV.4", "9. Master DSA Taxonomy: Graphs, Sorting & Algorithms")

dsa_graphs = [
    ("13. Graph (Adj Lists)", "src/dsa/graph.py", "O(V + E) Space", "Physical & virtual peer network topology representation"),
    ("14. BFS Algorithm", "src/dsa/bfs.py", "O(V + E) Time", "Peer discovery across hop layers & unweighted shortest path"),
    ("15. DFS Algorithm", "src/dsa/dfs.py", "O(V + E) Time", "Peer component enumeration & deep network topology analysis"),
    ("16. Dijkstra's Algorithm", "src/dsa/dijkstra.py", "O((V + E) log V)", "Minimum-latency routing across weighted peer network links"),
    ("17. Union-Find (DSU)", "src/dsa/union_find.py", "O(α(N)) Nearly O(1)", "Network partition detection and peer cluster connectivity"),
    ("18. Quick Sort & Merge Sort", "src/dsa/quick_sort.py", "O(N log N)", "Live candidate tally ranking and stable chronological audit sorting")
]

for idx, (name, path, comp, use) in enumerate(dsa_graphs):
    col_idx = idx % 3
    row_idx = idx // 3
    left = Inches(0.8 + col_idx * 4.0)
    top = Inches(1.6 + row_idx * 2.65)
    add_card(s10, left, top, Inches(3.7), Inches(2.45), name,
             [f"File: {path}", f"Complexity: {comp}", f"Role: {use}"],
             border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

# ==============================================================================
# Slide 11: Guideline Section B.IV.4 — Methodology: Blockchain Doubly Linked List [WITH IMAGE]
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_bg(s11)
add_header(s11, "Guideline Section B.IV.4 (Methodology)", "10. Blockchain Data Structure: Doubly Linked List of Cryptographic Blocks")

# Left Column: Explanation Text Card
add_card(s11, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Algorithmic Mechanics",
         ["• Bi-Directional Node Linking:",
          "  Each block acts as a node in a Doubly Linked List with prev_node and next_node pointers.",
          "• Cryptographic Hash Pointers:",
          "  Block[i].previous_hash == SHA-256(Block[i-1]).",
          "  Forms an immutable cryptographic chain.",
          "• O(1) Append, O(N) Full Audit:",
          "  Appending a newly mined block takes O(1) time at the tail pointer.",
          "• Tamper Evident Guarantee:",
          "  Modifying even a single character in Block 1 alters its Current Hash.",
          "  Block 2's previous_hash immediately fails validation, instantly alerting all peers."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

# Right Column: High-Res Diagram
img_path1 = os.path.join(ASSETS_DIR, "blockchain_architecture.png")
if os.path.exists(img_path1):
    s11.shapes.add_picture(img_path1, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 12: Guideline Section B.IV.4 — Methodology: Binary Merkle Tree [WITH IMAGE]
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_bg(s12)
add_header(s12, "Guideline Section B.IV.4 (Methodology)", "11. Binary Merkle Tree: Cryptographic Root & O(log N) Inclusion Proofs")

add_card(s12, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Cryptographic Verification",
         ["• Hierarchical Binary Tree:",
          "  Ballot transactions form leaf nodes. Pairs of hashes are concatenated and hashed recursively to produce the single Merkle Root.",
          "• Odd-Leaf Promotion Rule:",
          "  If an odd number of ballots exists at any level, the last hash is promoted or duplicated to maintain binary balance.",
          "• Logarithmic Proof Scaling:",
          "  A block containing N=1,024 ballots requires only 10 sibling hashes for inclusion proof.",
          "• Voter Privacy Preserved:",
          "  A voter can mathematically verify their vote was recorded without downloading the entire ledger or seeing anyone else's vote."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

img_path2 = os.path.join(ASSETS_DIR, "merkle_tree_diagram.png")
if os.path.exists(img_path2):
    s12.shapes.add_picture(img_path2, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 13: Guideline Section B.IV.4 — Methodology: Consistent Hashing Ring [WITH IMAGE]
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_bg(s13)
add_header(s13, "Guideline Section B.IV.4 (Methodology)", "12. Consistent Hashing Ring & Distributed Sharding Architecture")

add_card(s13, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Distributed Partitioning",
         ["• Virtual Node Ring Topology:",
          "  Both physical nodes and ballot partition keys are mapped onto a 2^256 SHA-256 integer ring.",
          "• Hotspot Elimination (R = 50):",
          "  Each physical node maintains 50 virtual replica tokens across the perimeter to guarantee uniform distribution.",
          "• Logarithmic Routing O(log(N·R)):",
          "  Routing uses binary search (bisect_right) to find the first clockwise node in < 2 microseconds.",
          "• Minimal Reshuffling Property:",
          "  Adding or dropping 1 node reassigns only K/N keys, preventing massive network re-partitioning spikes."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

img_path3 = os.path.join(ASSETS_DIR, "consistent_hash_ring.png")
if os.path.exists(img_path3):
    s13.shapes.add_picture(img_path3, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 14: Guideline Section B.IV.4 — Methodology: Network Topology & Dijkstra [WITH IMAGE]
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_bg(s14)
add_header(s14, "Guideline Section B.IV.4 (Methodology)", "13. P2P Network Mesh & Dijkstra Minimum-Latency Block Routing")

add_card(s14, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Network Graph Algorithms",
         ["• Weighted Mesh Graph:",
          "  Nodes measure link latency in milliseconds. Represented via adjacency lists: O(V + E) space.",
          "• Dijkstra's Algorithm:",
          "  Priority Queue (Min-Heap) computes minimum-latency propagation paths in O((V + E) log V).",
          "• BFS Peer Discovery:",
          "  Explores network layer-by-layer to discover new participating validator nodes.",
          "• Disjoint-Set Union (Union-Find):",
          "  Tracks connected components with path compression in O(α(V)) time to detect network splits."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

img_path4 = os.path.join(ASSETS_DIR, "network_topology_dijkstra.png")
if os.path.exists(img_path4):
    s14.shapes.add_picture(img_path4, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 15: Guideline Section B.IV.5 — Methodology: Decoupled Anonymous Ballot Flow [WITH IMAGE]
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_bg(s15)
add_header(s15, "Guideline Section B.IV.5 (Privacy)", "14. Decoupled Cryptographic Anonymity Protocol Workflow")

add_card(s15, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Single-Use Token Burn",
         ["• Privacy Through Decoupling:",
          "  Voter authentication is mathematically separated from ballot submission.",
          "• 4-Step Anonymity Pipeline:",
          "  1. Voter verifies identity with PIN (Hash Table check).",
          "  2. Authority issues a random cryptographic token.",
          "  3. Voter submits ballot with token—NO Voter ID is transmitted.",
          "  4. Node burns token atomically in SQLite; adds ballot to FIFO Mempool.",
          "• Double-Vote Defense:",
          "  SQLite UNIQUE(token_hash) prevents re-casting. Attempting to vote again is rejected instantly in < 1 µs."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

img_path5 = os.path.join(ASSETS_DIR, "anonymous_ballot_flow.png")
if os.path.exists(img_path5):
    s15.shapes.add_picture(img_path5, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 16: Guideline Section B.IV.5 — Consensus Protocol & Algorithmic Validation [WITH IMAGE]
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
set_slide_bg(s16)
add_header(s16, "Guideline Section B.IV.5", "15. Leader-Quorum Consensus Protocol & Block Validation")

add_card(s16, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Consensus Pipeline (Q=2/3)",
         ["• Leader Proposal (Node A):",
          "  Drains FIFO Mempool queue, builds Merkle Tree, signs block with ECDSA SECP256R1, and broadcasts proposal.",
          "• Independent Peer Validation:",
          "  Node B and C verify ECDSA signature, confirm previous_hash matches local tail, recompute Merkle Root, and guard against duplicate votes in local SQLite.",
          "• Quorum Commit (Q >= 2/3):",
          "  Once Leader receives >= 2 positive signed affirmations, it commits the block and broadcasts COMMIT signal.",
          "• Fault Tolerance:",
          "  Tolerates 1 offline node (2/3 quorum maintained) without network stall."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

img_path_cons = os.path.join(ASSETS_DIR, "consensus_protocol_flow.png")
if os.path.exists(img_path_cons):
    s16.shapes.add_picture(img_path_cons, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))


# ==============================================================================
# Slide 17: Guideline Section B.IV.6 — Evaluation Metrics & Empirical Benchmarks [WITH IMAGE]
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
set_slide_bg(s17)
add_header(s17, "Guideline Section B.IV.6", "16. Evaluation Metrics & Empirical Performance Analysis")

add_card(s17, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Benchmark Highlights",
         ["• Apple Silicon M-Series / Python 3.13:",
          "• Merkle Proof Scaling:",
          "  - N=16: 0.025 ms verification",
          "  - N=1,024: 0.026 ms verification",
          "  - Proves constant O(log N) verification regardless of chain size.",
          "• Sorting Throughput:",
          "  - Quick Sort is 2.5x - 3.3x faster than Merge Sort due to median-of-three in-place cache locality.",
          "• Consistent Hash Routing:",
          "  - 500,000+ keys/sec routing throughput with sub-2 µs latency."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

img_path6 = os.path.join(ASSETS_DIR, "benchmark_charts.png")
if os.path.exists(img_path6):
    s17.shapes.add_picture(img_path6, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 18: Guideline Section B.IV.7 — Comparative Analysis of Alternative Algorithms
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
set_slide_bg(s18)
add_header(s18, "Guideline Section B.IV.7", "17. Comparative Analysis of Alternative Algorithms & Approaches")

add_card(s18, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.55),
         "Merge Sort vs Quick Sort (Median-of-3)",
         ["• Merge Sort: Guaranteed O(N log N) in all cases, stable ordering for identical audit timestamps, requires O(N) auxiliary memory.",
          "• Quick Sort: In-place O(log N) memory, faster cache locality, but potentially O(N^2) without median-of-three pivot.",
          "• System Selection: Quick Sort for live candidate tally rankings; Merge Sort for chronological audit trail logs."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

add_card(s18, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.55),
         "Hash Table vs AVL Tree for Block Lookup",
         ["• Hash Table: Average O(1) lookup, but does not support range queries or sorted chronological iteration.",
          "• AVL Tree: Guaranteed O(log N) lookup, height-balanced with self-rotations, allows fast range queries over block heights.",
          "• System Selection: Hash Table for token lookups; AVL Tree for indexed block height verification."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s18, Inches(0.8), Inches(4.35), Inches(5.6), Inches(2.55),
         "Merkle Inclusion Proofs vs Full Ledger Scan",
         ["• Full Ledger Scan: Requires downloading entire blockchain O(N) to prove a vote exists; exposes all other voter ballots.",
          "• Merkle Proof: Lightweight audit receipt requiring only O(log N) hashes; zero exposure of neighboring ballots.",
          "• System Selection: Merkle Tree provides zero-knowledge ballot verification for resource-constrained voter phones."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s18, Inches(6.8), Inches(4.35), Inches(5.7), Inches(2.55),
         "Consistent Hashing vs Centralized Modulo Hash",
         ["• Modulo Hashing (Hash(K) mod N): Adding or removing 1 node causes 100% key churn and massive network reshuffling.",
          "• Consistent Hashing: Adding or removing a node reassigns only K/N keys, keeping 99% of data localized.",
          "• System Selection: Consistent Hashing enables elastic peer joining and dynamic shard distribution."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

# ==============================================================================
# Slide 19: Guideline Section B.IV.8 — Software Architecture & Full Stack [WITH IMAGE]
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
set_slide_bg(s19)
add_header(s19, "Guideline Section B.IV.8", "18. Full Software Stack & Architectural Implementation")

add_card(s19, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
         "Implementation Highlights",
         ["• Core Language: Python 3.13 (pure standard library + cryptography).",
          "• Web Framework: Flask RESTful API engine with CORS and session protection.",
          "• Independent SQLite Storage: WAL mode journaling and foreign keys per node.",
          "• Multi-Node Cluster:",
          "  - Node A: Port 5001 (Coordinator)",
          "  - Node B: Port 5002 (Validator)",
          "  - Node C: Port 5003 (Validator)",
          "• Modern Voter UI: Flask portal on port 5050 with real-time receipt verification."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

img_path7 = os.path.join(ASSETS_DIR, "system_architecture_stack.png")
if os.path.exists(img_path7):
    s19.shapes.add_picture(img_path7, Inches(5.6), Inches(1.6), width=Inches(6.9), height=Inches(5.3))

# ==============================================================================
# Slide 20: Guideline Section B.V — Results & Security Discussion
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
set_slide_bg(s20)
add_header(s20, "Guideline Section B.V", "19. Results & Security Discussion")

add_card(s20, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.55),
         "100% Automated Test Pass Rate",
         ["• 25 automated pytest suites covering all 25 DSA implementations.",
          "• Exhaustive edge cases: empty trees, hash collisions, tree rotations, graph cycles, ring wraparounds.",
          "• Consensus stress tested under simulated node crashes and network drops."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s20, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.55),
         "Tamper-Evident Ledger Integrity",
         ["• Modifying a single bit inside an accepted ballot instantly alters its SHA-256 hash.",
          "• Subsequent block previous_hash validation fails immediately across all 3 nodes.",
          "• Merkle inclusion proof recalculation detects leaf tampering in O(log N) time."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s20, Inches(0.8), Inches(4.35), Inches(5.6), Inches(2.55),
         "Zero Duplicate Ballots Allowed",
         ["• HashSet in-memory screening catches double-vote attempts in < 1 microsecond.",
          "• SQLite atomic UNIQUE(voter_id, election_id) constraint prevents race condition attacks.",
          "• Zero duplicate votes accepted across 5,000 synthetic test ballots."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

add_card(s20, Inches(6.8), Inches(4.35), Inches(5.7), Inches(2.55),
         "Graceful Partition Handling",
         ["• When 1 node disconnects, remaining 2 nodes maintain quorum (Q >= 2/3) and continue mining.",
          "• When 2 nodes disconnect, consensus halts safely; transactions remain safely in Mempool Queue.",
          "• Zero ledger forks or orphan inconsistencies generated."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 21: Guideline Section C — Demonstration Instructions & Reproduction Guide
# ==============================================================================
s21 = prs.slides.add_slide(blank_layout)
set_slide_bg(s21)
add_header(s21, "Guideline Section C", "20. Demonstration Instructions & Reproduction Guide")

add_card(s21, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Step 1: Start 3 Nodes",
         ["• Automated Launcher:",
          "  python3 scripts/start_local_network.py",
          "• Or Manual Terminals:",
          "  Term 1: python3 app.py --node-id node_a --port 5001",
          "  Term 2: python3 app.py --node-id node_b --port 5002",
          "  Term 3: python3 app.py --node-id node_c --port 5003",
          "• Nodes initialize independent SQLite databases in data/."],
         border_color=COLOR_CYAN, title_color=COLOR_CYAN)

add_card(s21, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Step 2: Seed & Run UI",
         ["• Register Demo Voters:",
          "  python3 scripts/register_demo_voters.py http://127.0.0.1:5001",
          "• Launch Voter Portal UI:",
          "  python3 voting_ui.py",
          "• Open browser at:",
          "  http://127.0.0.1:5050/",
          "• Cast votes, inspect receipts, and validate Merkle paths."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s21, Inches(8.8), Inches(1.6), Inches(3.6), Inches(5.2),
         "Step 3: Verification",
         ["• Run Full Test Suite:",
          "  pytest tests/ -v",
          "• Run 20-Step Demo Script:",
          "  python3 scripts/demo_local_network.py",
          "• Inspect 25-DSA Lab:",
          "  Open http://127.0.0.1:5001/dsa for live browser execution of all 25 algorithms."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 22: Guideline Section B.VI — Conclusion & Future Enhancements
# ==============================================================================
s22 = prs.slides.add_slide(blank_layout)
set_slide_bg(s22)
add_header(s22, "Guideline Section B.VI", "21. Conclusion & Future Enhancements")

add_card(s22, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Project Conclusions",
         ["• Proof of Feasibility: Successfully demonstrated that a production-grade decentralized voting system can be engineered from first-principles Data Structures & Algorithms without proprietary blockchain frameworks.",
          "• Algorithmic Precision: Deterministic DSA modules provide absolute audit guarantees and mathematical correctness that AI/ML models fundamentally cannot offer.",
          "• Decoupled Privacy: Proved that ballot anonymity and strict single-vote verification can coexist through single-use authorization token burn.",
          "• Real-World Portability: Seamless operation on both single-machine local simulation and multi-computer physical Wi-Fi networks."],
         border_color=COLOR_EMERALD, title_color=COLOR_EMERALD)

add_card(s22, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Future Enhancements",
         ["• Zero-Knowledge Proofs (zk-SNARKs): Enable voters to prove their ballot satisfies eligibility constraints without revealing any token or cryptographic receipt.",
          "• Byzantine Fault Tolerance (PBFT / Raft): Upgrade leader-quorum consensus to handle malicious, actively colluding Byzantine nodes.",
          "• Kademlia Distributed Hash Table (DHT): Implement XOR metric peer discovery to scale network from 3 nodes to tens of thousands of decentralized nodes.",
          "• Post-Quantum Cryptography: Migrate from ECDSA SECP256R1 to lattice-based signatures (e.g. CRYSTALS-Dilithium) to resist quantum decryption."],
         border_color=COLOR_PURPLE, title_color=COLOR_PURPLE)

# ==============================================================================
# Slide 23: Guideline Section B.VII & B.VIII — References & Contributors
# ==============================================================================
s23 = prs.slides.add_slide(blank_layout)
set_slide_bg(s23)
add_header(s23, "Guideline Section B.VII & B.VIII", "22. References & Project Contributors")

add_card(s23, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Academic & Algorithmic References",
         ["1. Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.",
          "2. Merkle, R. C. (1987). A Digital Signature Based on a Conventional Encryption Function. CRYPTO '87, pp. 369-378.",
          "3. Karger, D., et al. (1997). Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the Web. ACM STOC.",
          "4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press.",
          "5. Chaum, D. (1981). Untraceable Electronic Mail, Return Addresses, and Digital Pseudonyms. CACM, 24(2), 84-90."],
         border_color=COLOR_AMBER, title_color=COLOR_AMBER)

# Contributors Card with all 4 team members
shape_c = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
shape_c.fill.solid()
shape_c.fill.fore_color.rgb = COLOR_CARD
shape_c.line.color.rgb = COLOR_CYAN
shape_c.line.width = Pt(1.5)

tb_c = s23.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

p_c0 = tf_c.paragraphs[0]
p_c0.text = "Team Contributors & Metadata"
p_c0.font.size = Pt(13)
p_c0.font.bold = True
p_c0.font.color.rgb = COLOR_CYAN
p_c0.space_after = Pt(8)

contrib_items = [
    ("• Ashwin Krishna V", "cb.ai.u4aid25108", "DSA & Verification Lead"),
    ("• Madhan S", "cb.ai.u4aid25127", "Consensus & P2P Architect"),
    ("• Nakul Shravan", "cb.ai.u4aid25134", "Cryptographic Hashing & Merkle"),
    ("• Nawin K G", "cb.ai.u4aid25135", "System Architect & UI Lead")
]

for name, roll, role in contrib_items:
    p = tf_c.add_paragraph()
    p.text = f"{name} [{roll}] — {role}"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(3)

p_sep = tf_c.add_paragraph()
p_sep.text = "────────────────────────────────────────"
p_sep.font.size = Pt(8)
p_sep.font.color.rgb = COLOR_BORDER

meta_items = [
    ("Course Code", "2025.R.AID.1.23AID205"),
    ("Course Name", "Data Structures & Algorithms Capstone"),
    ("GitHub Repo", "https://github.com/kgnawinkg-tech/Decentralised-Voting-System"),
    ("Contact Email", "kgnawinkg@gmail.com"),
    ("Test Suites", "25 Pytest Suites (100% Pass Rate)")
]

for label, val in meta_items:
    p = tf_c.add_paragraph()
    p.text = f"{label}: {val}"
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_after = Pt(2)

prs.save(OUTPUT_PPTX)
print(f"Presentation saved successfully to: {OUTPUT_PPTX}")
