"""
Integration & Regression Tests for Interaction-First Physical EVM & Object Interface
Verifies that the physical EVM, its 6 control buttons, candidate rows, interactive blocks,
node server objects, Merkle nodes, and JSON proxy endpoints function accurately.
"""

import os
import pytest
from voting_ui import create_voting_ui_app, VotingBackendAdapter


@pytest.fixture
def client(tmp_path):
    db_file = str(tmp_path / "test_physical_ui.db")
    adapter = VotingBackendAdapter(db_path=db_file)
    app = create_voting_ui_app(adapter)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_physical_evm_interface_elements(client):
    """Verify that homepage loads the physical EVM chassis, control panel, and ballot unit."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Physical EVM 3D Chassis & Stage
    assert 'id="physicalEVMChassis"' in html
    assert 'id="evmStageWrapper"' in html

    # EVM LCD Screen & LEDs
    assert 'id="evmLcdScreen"' in html or 'evm-lcd-screen' in html
    assert 'id="ledPower"' in html
    assert 'id="ledBusy"' in html
    assert 'id="ledVote"' in html

    # The 6 Required Physical Machine Control Buttons directly on the EVM
    assert 'REGISTER VOTER' in html
    assert 'VOTER LOGIN' in html
    assert 'CAST VOTE' in html
    assert 'VERIFY RECEIPT' in html
    assert 'ELECTION RESULTS' in html
    assert 'HELP' in html or 'HELP / GUIDE' in html

    # Candidate Ballot Unit & 3D Blue Buttons
    assert 'evm-bu-section' in html
    assert 'evm-blue-btn' in html
    assert 'cand_1' in html or 'Alice Johnson' in html


def test_interactive_workspace_objects(client):
    """Verify interactive block objects, node server objects, and Merkle nodes exist."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Blockchain Block Objects & Inspector
    assert 'block-object' in html
    assert 'id="blockInspectorModal"' in html
    assert 'toggleTamperDemo' in html

    # 3-Node Physical Server Objects & Inspector
    assert 'node-server-object' in html
    assert 'id="nodeInspectorModal"' in html

    # Merkle Tree Interactive Hash Nodes
    assert 'merkle-hash-object' in html
    assert 'inspectMerkleNode' in html

    # DSA interactive workspaces
    assert 'id="dsaSection"' in html
    assert 'FIFO Mempool Queue' in html
    assert 'Consistent Hashing' in html


def test_script_and_api_endpoints(client):
    """Verify evm_interactive.js and API endpoints respond with valid status and JSON."""
    resp_js = client.get("/static/js/evm_interactive.js")
    assert resp_js.status_code == 200
    assert b"evm_interactive.js" in resp_js.data or b"window.EVM" in resp_js.data

    # Test /api/auth_status
    r_auth = client.get("/api/auth_status")
    assert r_auth.status_code == 200
    assert r_auth.get_json()["authenticated"] is False

    # Test /api/tally
    r_tally = client.get("/api/tally")
    assert r_tally.status_code == 200
    assert "candidate_results" in r_tally.get_json()

    # Test /api/nodes
    r_nodes = client.get("/api/nodes")
    assert r_nodes.status_code == 200
    assert "nodes" in r_nodes.get_json()


def test_evm_ajax_auth_flow(client):
    """Test in-place EVM AJAX registration and login flows."""
    # 1. Register voter via JSON
    reg_resp = client.post(
        "/register",
        json={
            "voter_id": "voter_evm_test",
            "name": "EVM Test Voter",
            "email": "evm@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert reg_resp.status_code == 200
    assert reg_resp.get_json()["success"] is True

    # 2. Login voter via JSON
    login_resp = client.post(
        "/login",
        json={
            "identifier": "voter_evm_test",
            "password": "password123",
        },
    )
    assert login_resp.status_code == 200
    assert login_resp.get_json()["success"] is True

    # 3. Check auth status now
    auth_resp = client.get("/api/auth_status")
    assert auth_resp.status_code == 200
    assert auth_resp.get_json()["authenticated"] is True
    assert auth_resp.get_json()["voter_id"] == "voter_evm_test"
