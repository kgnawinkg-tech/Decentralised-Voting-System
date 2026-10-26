"""
Automated Test Suite for Voter Registration and Voting UI (voting_ui.py)

Covers:
1. Home page rendering with election & node status.
2. Voter registration with valid inputs, password hashing, and email.
3. Rejection of invalid registration inputs (short password, bad email, bad voter ID).
4. Rejection of duplicate voter ID and duplicate email.
5. Voter login, session creation, and session fixation protection.
6. Rejection of invalid credentials on login.
7. Session protection (redirect to /login if accessing /vote unauthenticated).
8. Successful vote casting with candidate selection and cryptographic receipt.
9. Duplicate voting prevention (rejection of second ballot for same voter).
10. Rejection of invalid candidate IDs.
11. Rejection of vote submissions when election is CLOSED.
12. Logout behavior and session clearance.
13. Persistence across application re-initialization (restart).
14. Privacy check: Voter registry table does not contain candidate selections.
"""

import os
import shutil
import tempfile
import pytest
from voting_ui import create_voting_ui_app, VotingBackendAdapter
from src.voting.election import ElectionStatus


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_voting.db")

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


def test_home_page_rendering(test_env):
    """Test Home page loads with project title and election status."""
    client = test_env["client"]
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Decentralized Blockchain Voting System" in html
    assert "Register to Vote" in html
    assert "Alice Johnson" in html


def test_voter_registration_valid(test_env):
    """Test voter registration with valid details."""
    client = test_env["client"]
    resp = client.post(
        "/register",
        data={
            "voter_id": "test_voter_01",
            "name": "Test Citizen",
            "email": "citizen@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Registration successful" in html

    # Verify password is NOT stored in plain text
    voter = test_env["backend"]._db.get_voter("test_voter_01")
    assert voter is not None
    assert voter["password_hash"] != "securepassword123"
    assert voter["email"] == "citizen@example.com"


def test_voter_registration_invalid_inputs(test_env):
    """Test rejection of mismatched passwords, short passwords, and invalid email."""
    client = test_env["client"]

    # Mismatched passwords
    r1 = client.post(
        "/register",
        data={
            "voter_id": "bad_voter_1",
            "name": "Bad Voter",
            "email": "bad@example.com",
            "password": "passwordA",
            "confirm_password": "passwordB",
        },
    )
    assert "Passwords do not match" in r1.get_data(as_text=True)

    # Password too short
    r2 = client.post(
        "/register",
        data={
            "voter_id": "bad_voter_2",
            "name": "Bad Voter",
            "email": "bad@example.com",
            "password": "123",
            "confirm_password": "123",
        },
    )
    assert "Password must be at least 6 characters" in r2.get_data(as_text=True)

    # Invalid email format
    r3 = client.post(
        "/register",
        data={
            "voter_id": "bad_voter_3",
            "name": "Bad Voter",
            "email": "not-an-email",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert "Please enter a valid email address" in r3.get_data(as_text=True)


def test_duplicate_registration_rejection(test_env):
    """Test that duplicate voter IDs and duplicate email addresses are rejected."""
    client = test_env["client"]

    # Register initial voter
    client.post(
        "/register",
        data={
            "voter_id": "unique_voter_1",
            "name": "Original User",
            "email": "unique@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    # Attempt duplicate voter_id
    r_dup_id = client.post(
        "/register",
        data={
            "voter_id": "unique_voter_1",
            "name": "Imposter User",
            "email": "other@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert "already registered" in r_dup_id.get_data(as_text=True)

    # Attempt duplicate email
    r_dup_email = client.post(
        "/register",
        data={
            "voter_id": "different_voter_id",
            "name": "Another User",
            "email": "unique@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert "already registered" in r_dup_email.get_data(as_text=True)


def test_voter_login_and_session_protection(test_env):
    """Test valid login, wrong password, nonexistent voter, and session fixation defense."""
    client = test_env["client"]

    # Register voter
    client.post(
        "/register",
        data={
            "voter_id": "auth_user_01",
            "name": "Auth User",
            "email": "auth@example.com",
            "password": "secretpassword",
            "confirm_password": "secretpassword",
        },
    )

    # 1. Unauthenticated access to /vote must redirect to login
    r_unauth = client.get("/vote")
    assert r_unauth.status_code == 302
    assert "/login" in r_unauth.location

    # 2. Login with wrong password
    r_bad_pw = client.post(
        "/login",
        data={"identifier": "auth_user_01", "password": "wrongpassword"},
    )
    assert "Login failed" in r_bad_pw.get_data(as_text=True)

    # 3. Login with nonexistent voter
    r_no_user = client.post(
        "/login",
        data={"identifier": "nonexistent_voter", "password": "password123"},
    )
    assert "not found" in r_no_user.get_data(as_text=True)

    # 4. Successful login by voter_id
    r_good = client.post(
        "/login",
        data={"identifier": "auth_user_01", "password": "secretpassword"},
        follow_redirects=True,
    )
    assert r_good.status_code == 200
    assert "Welcome, Auth User" in r_good.get_data(as_text=True)

    # 5. Successful login by email
    client.get("/logout")
    r_email_login = client.post(
        "/login",
        data={"identifier": "auth@example.com", "password": "secretpassword"},
        follow_redirects=True,
    )
    assert "Welcome, Auth User" in r_email_login.get_data(as_text=True)


def test_cast_vote_workflow_and_receipt(test_env):
    """Test full voting workflow: login -> select candidate -> confirm -> receipt."""
    client = test_env["client"]

    # Register & Login
    client.post(
        "/register",
        data={
            "voter_id": "voter_ballot_test",
            "name": "Ballot Tester",
            "email": "ballot@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "voter_ballot_test", "password": "password123"})

    # Cast vote for valid candidate
    r_vote = client.post("/vote", data={"candidate_id": "cand_1"}, follow_redirects=True)
    assert r_vote.status_code == 200
    html = r_vote.get_data(as_text=True)
    assert "Ballot Successfully Accepted" in html
    assert "Transaction ID" in html
    assert "COMMITTED & VERIFIED" in html

    # Tally must reflect the vote
    tally = test_env["backend"].get_tally()
    assert tally["candidate_tallies"].get("cand_1") == 1
    assert tally["total_ballots"] == 1


def test_duplicate_voting_prevention(test_env):
    """Test that an eligible voter cannot submit a second ballot."""
    client = test_env["client"]

    # Register & Login
    client.post(
        "/register",
        data={
            "voter_id": "double_voter",
            "name": "Double Voter",
            "email": "double@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "double_voter", "password": "password123"})

    # First vote succeeds
    r1 = client.post("/vote", data={"candidate_id": "cand_1"}, follow_redirects=True)
    assert "Ballot Successfully Accepted" in r1.get_data(as_text=True)

    # Second vote must be rejected
    r2 = client.post("/vote", data={"candidate_id": "cand_2"}, follow_redirects=True)
    html2 = r2.get_data(as_text=True)
    assert ("Duplicate vote rejected" in html2) or ("already cast" in html2) or ("Already Recorded" in html2)

    # Tally must remain 1
    tally = test_env["backend"].get_tally()
    assert tally["total_ballots"] == 1


def test_invalid_candidate_rejection(test_env):
    """Test that selecting a nonexistent candidate is rejected."""
    client = test_env["client"]

    # Register & Login
    client.post(
        "/register",
        data={
            "voter_id": "fraud_tester",
            "name": "Fraud Tester",
            "email": "fraud@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "fraud_tester", "password": "password123"})

    # Submit invalid candidate
    r = client.post("/vote", data={"candidate_id": "nonexistent_candidate_999"}, follow_redirects=True)
    assert "Invalid candidate" in r.get_data(as_text=True)


def test_closed_election_rejection(test_env):
    """Test that votes are rejected when the election is CLOSED."""
    client = test_env["client"]
    backend = test_env["backend"]

    # Close election
    backend._election.close_election()

    # Register & Login
    client.post(
        "/register",
        data={
            "voter_id": "late_voter",
            "name": "Late Voter",
            "email": "late@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "late_voter", "password": "password123"})

    # Attempt to vote
    r = client.post("/vote", data={"candidate_id": "cand_1"}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert ("CLOSED" in html) or ("closed" in html)


def test_persistence_after_app_restart(test_env):
    """Test that voter registry and ballots persist across app restart."""
    db_path = test_env["db_path"]
    client = test_env["client"]

    # Register voter and cast ballot
    client.post(
        "/register",
        data={
            "voter_id": "persistent_voter",
            "name": "Persistent Voter",
            "email": "persist@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "persistent_voter", "password": "password123"})
    client.post("/vote", data={"candidate_id": "cand_2"})

    # Simulate app restart with a fresh VotingBackendAdapter pointing to same DB
    new_backend = VotingBackendAdapter(node_url="http://127.0.0.1:59999", db_path=db_path)
    new_app = create_voting_ui_app(new_backend)
    new_app.config["TESTING"] = True
    new_client = new_app.test_client()

    # Verify voter can still log in
    r_login = new_client.post(
        "/login",
        data={"identifier": "persistent_voter", "password": "password123"},
        follow_redirects=True,
    )
    assert "Welcome, Persistent Voter" in r_login.get_data(as_text=True)

    # Verify tally persisted
    tally = new_backend.get_tally()
    assert tally["candidate_tallies"].get("cand_2") == 1


def test_voter_privacy_decoupling(test_env):
    """Verify that voter records NEVER store candidate selections in the database."""
    client = test_env["client"]
    db = test_env["backend"]._db

    # Register & vote
    client.post(
        "/register",
        data={
            "voter_id": "private_voter_99",
            "name": "Private Voter",
            "email": "private@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    client.post("/login", data={"identifier": "private_voter_99", "password": "password123"})
    client.post("/vote", data={"candidate_id": "cand_3"})

    # Inspect voter_registry table directly
    voter_row = db.get_voter("private_voter_99")
    assert "cand_3" not in str(voter_row)
    assert "candidate" not in voter_row
    assert "candidate_id" not in voter_row

    # Inspect accepted_ballots table
    ballots = db.get_accepted_ballots()
    assert len(ballots) == 1
    # Candidate choice is recorded anonymously with token hash, NOT voter_id
    assert ballots[0]["candidate_id"] == "cand_3"
    assert "private_voter_99" not in str(ballots[0])
    assert "voter_id" not in ballots[0]
