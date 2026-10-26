"""
Unit and Integration Tests for Extended UI Features and Pages
Covers:
1. Explorer page rendering
2. Merkle Proof Auditor rendering
3. Network topology page rendering
4. Consensus dashboard rendering
5. Mempool queue page rendering
6. Sharding explorer rendering
7. DSA Laboratory rendering (all 25 concepts)
8. Admin portal rendering
9. System health & diagnostics rendering
10. Deployment guide rendering
11. DSA execution API endpoint
12. EVM voting UI rendering for authenticated voter
"""

import os
import shutil
import tempfile
import pytest
from voting_ui import create_voting_ui_app, VotingBackendAdapter


@pytest.fixture
def extended_test_env():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "ext_voting.db")

    backend = VotingBackendAdapter(node_url="http://127.0.0.1:59999", db_path=db_path)
    app = create_voting_ui_app(backend)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    client = app.test_client()

    yield {
        "app": app,
        "client": client,
        "backend": backend,
        "db_path": db_path,
        "temp_dir": temp_dir,
    }

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_explorer_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/explorer")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Blockchain Ledger Explorer" in html
    assert "BLOCK #0" in html


def test_merkle_proof_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/merkle_proof")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Merkle Inclusion Proof Auditor" in html
    assert "DSA CONCEPT 21" in html


def test_network_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/network")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Distributed 3-Node P2P Network" in html
    assert "Node A" in html


def test_consensus_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/consensus")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Consensus & Block Validation" in html
    assert "LEADER-QUORUM" in html


def test_mempool_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/mempool")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Mempool & FIFO Transaction Queue" in html
    assert "FIFO (Queue)" in html


def test_shards_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/shards")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Distributed Sharding Explorer" in html
    assert "Consistent Hashing Ring" in html


def test_dsa_lab_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/dsa")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "25 Data Structures & Algorithms Laboratory" in html
    # Check multiple distinct DSA concepts
    assert "Hash Table" in html
    assert "AVL Tree" in html
    assert "Dijkstra Shortest Path" in html
    assert "Consistent Hashing" in html
    assert "Merkle Tree" in html
    assert "Hash Set" in html


def test_admin_portal_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/admin")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Election Administration" in html
    assert "Official Ballot Candidates" in html


def test_system_health_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/health")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "System Health & Cryptographic Security" in html
    assert "PBKDF2-HMAC-SHA256" in html


def test_deployment_guide_page(extended_test_env):
    client = extended_test_env["client"]
    resp = client.get("/deployment")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Configuration & Multi-Computer Deployment Guide" in html
    assert "Deployment Mode A" in html
    assert "Deployment Mode B" in html


def test_dsa_api_endpoint(extended_test_env):
    client = extended_test_env["client"]
    resp = client.post("/api/dsa/hash_table")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "concept" in data
    assert data["concept"] == "hash_table"


def test_evm_authenticated_voting_ui(extended_test_env):
    client = extended_test_env["client"]
    backend = extended_test_env["backend"]

    # Register and login voter
    backend.register_voter("test_evm_voter", "EVM Citizen", "password123", "evm@example.com")

    # Set session
    with client.session_transaction() as sess:
        sess["voter_id"] = "test_evm_voter"
        sess["voter_name"] = "EVM Citizen"
        sess["voter_pw"] = "password123"

    resp = client.get("/vote")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "BALLOT CONTROL UNIT" in html
    assert "BALLOT UNIT: BU-01" in html
    assert "evm-blue-btn" in html
    assert "Alice Johnson" in html
