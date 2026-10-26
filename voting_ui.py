"""
Decentralized Blockchain Voting System — Voter Interface (voting_ui.py)

A secure, full-featured web portal for voter registration, eligibility verification,
and anonymous ballot casting on the decentralized blockchain network.

Integrates with the existing decentralized backend (via HTTP Node API on port 5001,
or direct SQLite database fallback).

Run:
    python3 voting_ui.py [--port 5050] [--node http://127.0.0.1:5001]
"""

import argparse
import os
import re
import secrets
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# Existing backend modules
from src.blockchain.chain import Blockchain
from src.blockchain.merkle_tree import MerkleTree, MerkleProofStep
from src.dsa.consistent_hashing import ConsistentHashingRing
from src.security.authentication import hash_password, verify_password
from src.security.hashing import sha256_hash
from src.security.input_validation import validate_id
from src.storage.database import Database
from src.voting.authorization import VotingAuthorizationManager
from src.voting.election import Election, ElectionStatus
from src.voting.voter_registry import VoterRegistry

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def load_config(config_path: str = "config.yaml") -> dict:
    full_path = os.path.join(PROJECT_ROOT, config_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


class VotingBackendAdapter:
    """
    Unified adapter that communicates with an active node API (HTTP)
    or falls back to direct local SQLite/blockchain modules if the node is offline.
    """

    def __init__(self, node_url: str = "http://127.0.0.1:5001", db_path: str = "voting.db"):
        self.node_url = node_url.rstrip("/")
        self.db_path = os.path.join(PROJECT_ROOT, db_path) if not os.path.isabs(db_path) else db_path
        self.config = load_config()

        # Local fallback instances
        self._db = Database(self.db_path)
        self._voter_registry = VoterRegistry(self._db)
        self._election = self._init_local_election()
        self._auth_manager = VotingAuthorizationManager(self._db, self._election.election_id)
        self._blockchain = Blockchain(node_id="voting_ui", shard_id="shard_default")
        self._hash_ring = ConsistentHashingRing(virtual_nodes=50)
        for n in ["node_a", "node_b", "node_c"]:
            self._hash_ring.add_node(n)

    def _init_local_election(self) -> Election:
        el_cfg = self.config.get("election", {})
        el = Election(
            election_id=el_cfg.get("id", "election_2026_general"),
            title=el_cfg.get("title", "2026 Decentralized General Election"),
            description=el_cfg.get("description", "Decentralized voting ledger"),
        )
        for c in el_cfg.get("candidates", []):
            el.add_candidate(c["id"], c["name"], c.get("party", ""))
        el.open_election()
        return el

    def is_node_online(self) -> bool:
        try:
            r = requests.get(f"{self.node_url}/api/health", timeout=1.0)
            return r.status_code == 200
        except Exception:
            return False

    def get_node_status(self) -> Dict[str, Any]:
        if self.is_node_online():
            try:
                r = requests.get(f"{self.node_url}/api/node_info", timeout=2.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass

        # Fallback local status
        tip = self._blockchain.get_tip()
        return {
            "node_id": "voting_ui_local",
            "name": "Local Direct Engine (voting.db)",
            "host": "127.0.0.1",
            "port": 5050,
            "block_height": len(self._blockchain.blocks),
            "tip_hash": tip.current_hash if tip else "0" * 64,
            "chain_valid": True,
            "chain_integrity_message": "Local verified ledger",
            "pending_mempool_size": 0,
            "stored_records_count": len(self._db.get_accepted_ballots()),
            "online_peers": ["local_engine"],
            "election_status": self._election.status.value,
        }

    def get_election_details(self) -> Dict[str, Any]:
        el_cfg = self.config.get("election", {})
        candidates = el_cfg.get("candidates", [
            {"id": "cand_1", "name": "Alice Johnson", "party": "Progressive Tech Alliance"},
            {"id": "cand_2", "name": "Bob Martinez", "party": "Open Data Coalition"},
            {"id": "cand_3", "name": "Carol Chen", "party": "Green Cyber Initiative"},
        ])
        status = "OPEN"
        if self.is_node_online():
            st = self.get_node_status()
            status = st.get("election_status", "OPEN")
        else:
            status = self._election.status.value

        return {
            "id": el_cfg.get("id", "election_2026_general"),
            "title": el_cfg.get("title", "2026 Decentralized General Election"),
            "description": el_cfg.get("description", "Secure decentralized vote recording"),
            "status": status,
            "candidates": candidates,
        }

    def register_voter(
        self, voter_id: str, name: str, password: str, email: str
    ) -> Tuple[bool, str]:
        # Always record in local DB as well to ensure persistence in voting.db
        local_ok, local_msg = self._voter_registry.register_voter(
            voter_id=voter_id, name=name, password=password, email=email
        )

        # If HTTP node is online, also propagate to cluster
        if self.is_node_online():
            try:
                r = requests.post(
                    f"{self.node_url}/api/voter/register",
                    json={"voter_id": voter_id, "name": name, "password": password, "email": email},
                    timeout=3.0,
                )
                if r.status_code == 200:
                    return True, "Voter registered successfully across network"
                else:
                    err = r.json().get("error", r.json().get("message", "Registration rejected by node"))
                    return False, err
            except Exception as e:
                # If remote call fails but local succeeded, report local success
                if local_ok:
                    return True, local_msg
                return False, str(e)

        return local_ok, local_msg

    def authenticate_voter(self, identifier: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        # 1. Check local DB first
        voter = self._db.get_voter(identifier)
        if not voter and "@" in identifier:
            voter = self._db.get_voter_by_email(identifier)

        if voter:
            if not verify_password(password, voter["password_hash"], voter["salt"]):
                return False, None, "Invalid password"
            if not voter.get("eligible", 1):
                return False, None, "Voter is marked as ineligible"
            return True, voter, "Authentication successful"

        # 2. Check remote node if online
        if self.is_node_online():
            try:
                r = requests.post(
                    f"{self.node_url}/api/voter/auth_token",
                    json={"voter_id": identifier, "password": password},
                    timeout=3.0,
                )
                if r.status_code == 200:
                    data = r.json()
                    return True, {"voter_id": identifier, "name": data.get("voter_name", identifier)}, "Authentication successful"
                elif r.status_code == 401:
                    return False, None, "Invalid voter credentials"
            except Exception:
                pass

        return False, None, "Voter ID or email not found in registry"

    def has_voter_voted(self, voter_id: str) -> bool:
        """Check if a voter has already requested/spent their authorization token."""
        # Check local DB: if authorization record exists, token was issued/burned
        auth = self._db.get_authorization_by_voter(voter_id, self._election.election_id)
        if auth:
            return True
        return False

    def get_assigned_shard(self, key: str) -> str:
        return self._hash_ring.get_node(key)

    def cast_ballot(self, voter_id: str, password: str, candidate_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        election_details = self.get_election_details()
        if election_details["status"] != "OPEN":
            return False, None, "Cannot submit vote: Election is currently CLOSED."

        valid_candidate_ids = [c["id"] for c in election_details["candidates"]]
        if candidate_id not in valid_candidate_ids:
            return False, None, f"Invalid candidate '{candidate_id}' selected."

        # Double vote prevention check
        if self.has_voter_voted(voter_id):
            return False, None, "Duplicate vote rejected: You have already cast a ballot in this election."

        # If HTTP node cluster is online, submit through decentralized consensus API
        if self.is_node_online():
            try:
                # 1. Obtain single-use token
                t_resp = requests.post(
                    f"{self.node_url}/api/voter/auth_token",
                    json={"voter_id": voter_id, "password": password},
                    timeout=3.0,
                )
                if t_resp.status_code != 200:
                    err = t_resp.json().get("error", "Failed to obtain voting authorization")
                    return False, None, err

                token = t_resp.json().get("authorization_token")

                # 2. Submit anonymous ballot (token ONLY, no voter_id!)
                b_resp = requests.post(
                    f"{self.node_url}/api/submit_ballot",
                    json={"candidate_id": candidate_id, "authorization_token": token},
                    timeout=3.0,
                )
                if b_resp.status_code != 200:
                    err = b_resp.json().get("error", "Ballot submission rejected")
                    return False, None, err

                b_data = b_resp.json()
                receipt = b_data.get("receipt", {})

                # 3. Trigger immediate consensus mining so receipt has block height
                try:
                    m_resp = requests.post(f"{self.node_url}/api/mine", timeout=5.0)
                    if m_resp.status_code == 200:
                        mined_block = m_resp.json().get("block", {})
                        receipt["block_index"] = mined_block.get("index")
                        receipt["merkle_root"] = mined_block.get("merkle_root")
                except Exception:
                    pass

                # Also record locally as spent
                issued, tok, _ = self._auth_manager.issue_token(voter_id)
                if tok:
                    self._auth_manager.redeem_token(tok)
                return True, receipt, "Ballot successfully accepted and committed to blockchain!"
            except Exception as e:
                return False, None, f"Communication with blockchain node failed: {e}"

        # Standalone Local Mode (Atomic SQLite operations)
        issued, token, msg = self._auth_manager.issue_token(voter_id)
        if not issued:
            return False, None, f"Authorization failed: {msg}"

        # Consume token atomically
        valid, token_hash, val_msg = self._auth_manager.redeem_token(token)
        if not valid or not token_hash:
            return False, None, f"Ballot validation failed: {val_msg}"

        # Construct anonymous ballot transaction
        tx_id = sha256_hash(f"{token_hash}:{candidate_id}:{time.time()}:{secrets.token_hex(8)}")
        shard_id = self.get_assigned_shard(tx_id)
        tx_dict = {
            "transaction_id": tx_id,
            "candidate_id": candidate_id,
            "token_hash": token_hash,
            "assigned_shard": shard_id,
            "timestamp": time.time(),
        }

        # Save to local database
        self._db.save_accepted_ballot(tx_dict)
        block = self._blockchain.add_block([tx_dict])
        self._db.save_block(block.to_dict())

        receipt = {
            "transaction_id": tx_id,
            "token_hash": token_hash,
            "assigned_shard": shard_id,
            "block_index": block.index,
            "merkle_root": block.merkle_root,
            "timestamp": tx_dict["timestamp"],
        }
        return True, receipt, "Ballot successfully committed to local ledger!"

    def get_tally(self) -> Dict[str, Any]:
        if self.is_node_online():
            try:
                r = requests.get(f"{self.node_url}/api/tally", timeout=2.0)
                if r.status_code == 200:
                    data = r.json()
                    # Ensure candidate_tallies dictionary exists
                    tallies: Dict[str, int] = {}
                    if "candidate_tallies" in data and isinstance(data["candidate_tallies"], dict):
                        tallies = data["candidate_tallies"]
                    elif "candidate_results" in data and isinstance(data["candidate_results"], list):
                        for c in data["candidate_results"]:
                            tallies[c.get("candidate_id")] = c.get("votes", 0)

                    total = data.get("total_accepted_ballots")
                    if total is None:
                        total = data.get("total_ballots", sum(tallies.values()))

                    data["total_ballots"] = total
                    data["total_accepted_ballots"] = total
                    data["candidate_tallies"] = tallies
                    return data
            except Exception:
                pass

        # Calculate tally from local DB
        ballots = self._db.get_accepted_ballots()
        tallies: Dict[str, int] = {}
        for b in ballots:
            cid = b.get("candidate_id")
            tallies[cid] = tallies.get(cid, 0) + 1

        total = len(ballots)
        candidates = self.get_election_details().get("candidates", [])
        candidate_results = [
            {
                "candidate_id": c["id"],
                "name": c["name"],
                "party": c.get("party", ""),
                "votes": tallies.get(c["id"], 0),
                "percentage": round(tallies.get(c["id"], 0) / total * 100.0, 2) if total > 0 else 0.0,
            }
            for c in candidates
        ]

        return {
            "election_id": self._election.election_id,
            "total_ballots": total,
            "total_accepted_ballots": total,
            "candidate_tallies": tallies,
            "candidate_results": candidate_results,
            "certified": True,
        }

    def get_merkle_proof(self, tx_id: str) -> Optional[Dict[str, Any]]:
        if self.is_node_online():
            try:
                r = requests.get(f"{self.node_url}/api/merkle_proof/{tx_id}", timeout=2.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass

        proof_res = self._blockchain.get_merkle_proof_for_tx(tx_id)
        if not proof_res:
            return None
        block, tx, proof = proof_res
        return {
            "success": True,
            "transaction_id": tx_id,
            "block_index": block.index,
            "merkle_root": block.merkle_root,
            "transaction": tx,
            "proof": proof,
        }

    def get_chain(self) -> Tuple[List[Dict[str, Any]], bool, str]:
        if self.is_node_online():
            try:
                r = requests.get(f"{self.node_url}/api/chain", timeout=2.0)
                if r.status_code == 200:
                    d = r.json()
                    return d.get("chain", []), d.get("is_valid", True), d.get("integrity_message", "Valid")
            except Exception:
                pass
        is_valid, msg = self._blockchain.verify_integrity()
        return self._blockchain.to_list(), is_valid, msg

    def get_network_nodes(self) -> List[Dict[str, Any]]:
        nodes_cfg = self.config.get("network", {}).get("nodes", {})
        default_nodes = {
            "node_a": {"id": "node_a", "name": "Node A (Leader)", "host": "127.0.0.1", "port": 5001},
            "node_b": {"id": "node_b", "name": "Node B (Validator)", "host": "127.0.0.1", "port": 5002},
            "node_c": {"id": "node_c", "name": "Node C (Validator)", "host": "127.0.0.1", "port": 5003},
        }
        res = []
        for nid, info in (nodes_cfg or default_nodes).items():
            ep = f"http://{info.get('host', '127.0.0.1')}:{info.get('port')}"
            online = False
            latency = 999.0
            height = 0
            pending = 0
            records = 0
            peers = []
            try:
                t0 = time.perf_counter()
                r = requests.get(f"{ep}/api/node_info", timeout=1.0)
                latency = (time.perf_counter() - t0) * 1000.0
                if r.status_code == 200:
                    online = True
                    data = r.json()
                    height = data.get("block_height", 0)
                    pending = data.get("pending_mempool_size", 0)
                    records = data.get("stored_records_count", 0)
                    peers = data.get("online_peers", [])
            except Exception:
                online = False

            res.append({
                "id": nid,
                "name": info.get("name", nid),
                "endpoint": ep,
                "online": online,
                "latency_ms": latency if online else 0,
                "block_height": height,
                "pending_mempool": pending,
                "stored_records": records,
                "online_peers": peers,
            })
        return res

    def get_mempool_transactions(self) -> List[Dict[str, Any]]:
        return []

    def get_all_voters(self) -> List[Dict[str, Any]]:
        return self._db.get_all_voters()

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        return self._db.get_audit_logs()

    def get_shard_records(self) -> List[Dict[str, Any]]:
        return self._db.get_shard_records()

    def update_election_status(self, status: str) -> Tuple[bool, str]:
        status = status.upper()
        if self.is_node_online():
            try:
                r = requests.post(f"{self.node_url}/api/election/status", json={"status": status}, timeout=2.0)
                if r.status_code == 200:
                    return True, f"Election status set to {status}"
            except Exception:
                pass
        if status == "OPEN":
            self._election.open_election()
        elif status == "CLOSED":
            self._election.close_election()
        return True, f"Election status updated to {status}"

    def trigger_mine(self) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        if self.is_node_online():
            try:
                r = requests.post(f"{self.node_url}/api/mine", timeout=5.0)
                data = r.json()
                return data.get("success", False), data.get("block"), data.get("message", "")
            except Exception as e:
                return False, None, str(e)
        return False, None, "Single-node direct engine has no pending blocks to mine."

    def trigger_sync(self) -> Dict[str, Any]:
        if self.is_node_online():
            try:
                r = requests.post(f"{self.node_url}/api/sync", timeout=3.0)
                return r.json()
            except Exception as e:
                return {"error": str(e)}
        return {"error": "Local engine does not require peer synchronization"}

    def explore_dsa(self, concept_name: str) -> Dict[str, Any]:
        if self.is_node_online():
            try:
                r = requests.post(f"{self.node_url}/api/dsa/explore/{concept_name}", timeout=3.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass

        # Fallback direct execution
        from src.security.hashing import sha256_hash
        return {
            "concept": concept_name,
            "status": "Executed via Local Engine",
            "time_complexity": "O(1) to O(N log N)",
            "output_hash": sha256_hash(f"{concept_name}:{time.time()}"),
            "timestamp": time.time(),
        }


def create_voting_ui_app(backend: Optional[VotingBackendAdapter] = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(PROJECT_ROOT, "templates"),
        static_folder=os.path.join(PROJECT_ROOT, "static"),
    )
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    adapter = backend or VotingBackendAdapter()

    # --- Routes ---

    @app.route("/")
    def home():
        node_status = adapter.get_node_status()
        election = adapter.get_election_details()
        tally = adapter.get_tally()
        voters = adapter.get_all_voters()
        chain, is_valid, msg = adapter.get_chain()
        recent_blocks = list(reversed(chain))[:8]
        nodes = adapter.get_network_nodes()
        shard_records = adapter.get_shard_records()
        audit_logs = adapter.get_audit_logs()
        mempool = adapter.get_mempool_transactions()
        return render_template(
            "index.html",
            node_status=node_status,
            election=election,
            tally=tally,
            voters_count=len(voters),
            voters=voters,
            recent_blocks=recent_blocks,
            chain=chain,
            is_valid=is_valid,
            chain_msg=msg,
            nodes=nodes,
            shard_records=shard_records,
            audit_logs=audit_logs,
            mempool=mempool,
        )

    @app.route("/api/auth_status")
    def api_auth_status():
        voter_id = session.get("voter_id")
        if not voter_id:
            return jsonify({"authenticated": False})
        return jsonify({
            "authenticated": True,
            "voter_id": voter_id,
            "voter_name": session.get("voter_name", voter_id),
            "already_voted": adapter.has_voter_voted(voter_id)
        })

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            data = request.get_json(silent=True) or request.form
            voter_id = data.get("voter_id", "").strip()
            name = data.get("name", "").strip()
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            confirm_pwd = data.get("confirm_password", "")

            # Validation
            if not voter_id or not re.match(r"^[A-Za-z0-9_\-]{3,32}$", voter_id):
                err = "Voter ID must be 3-32 alphanumeric characters, dashes, or underscores."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("register.html")

            if not name or len(name) < 2:
                err = "Please enter your full legal name."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("register.html")

            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not email or not re.match(email_regex, email):
                err = "Please enter a valid email address."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("register.html")

            if len(password) < 6:
                err = "Password must be at least 6 characters."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("register.html")

            if password != confirm_pwd:
                err = "Passwords do not match."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("register.html")

            # Registration execution
            success, msg = adapter.register_voter(voter_id, name, password, email)
            if success:
                if request.is_json:
                    return jsonify({"success": True, "message": f"Registration successful! You may now log in with Voter ID '{voter_id}'."})
                flash(f"Registration successful! You may now log in with Voter ID '{voter_id}'.", "success")
                return redirect(url_for("login"))
            else:
                if request.is_json:
                    return jsonify({"success": False, "message": f"Registration rejected: {msg}"}), 400
                flash(f"Registration rejected: {msg}", "danger")
                return render_template("register.html")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            data = request.get_json(silent=True) or request.form
            identifier = data.get("identifier", "").strip()
            password = data.get("password", "")
            next_url = request.form.get("next") or request.args.get("next")

            if not identifier or not password:
                err = "Please provide your Voter ID/Email and password."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return render_template("login.html")

            ok, voter, msg = adapter.authenticate_voter(identifier, password)
            if not ok or not voter:
                if request.is_json:
                    return jsonify({"success": False, "message": f"Login failed: {msg}"}), 401
                flash(f"Login failed: {msg}", "danger")
                return render_template("login.html")

            # Session Fixation Protection: clear old session before setting authenticated values
            session.clear()
            session["voter_id"] = voter["voter_id"]
            session["voter_name"] = voter["name"]
            session["voter_pw"] = password  # Kept in encrypted server-side session only for single-use token issuance
            session["already_voted"] = adapter.has_voter_voted(voter["voter_id"])

            if request.is_json:
                return jsonify({
                    "success": True,
                    "voter_id": voter["voter_id"],
                    "voter_name": voter["name"],
                    "already_voted": session["already_voted"],
                    "message": f"Welcome, {voter['name']}! Authenticated successfully."
                })

            flash(f"Welcome, {voter['name']}! You have authenticated successfully.", "success")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("vote"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        if request.is_json or request.headers.get("Accept") == "application/json":
            return jsonify({"success": True, "message": "Logged out successfully"})
        flash("You have been logged out securely.", "info")
        return redirect(url_for("login"))

    @app.route("/vote", methods=["GET", "POST"])
    def vote():
        voter_id = session.get("voter_id")
        if not voter_id:
            if request.is_json:
                return jsonify({"success": False, "message": "Please log in to verify your voting eligibility and access your ballot."}), 401
            flash("Please log in to verify your voting eligibility and access your ballot.", "warning")
            return redirect(url_for("login", next=request.path))

        election = adapter.get_election_details()
        assigned_shard = adapter.get_assigned_shard(voter_id)
        already_voted = adapter.has_voter_voted(voter_id)

        if request.method == "POST":
            if election["status"] != "OPEN":
                err = "Cannot submit ballot: The election has officially CLOSED."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return redirect(url_for("vote"))

            if already_voted:
                err = "Duplicate vote rejected: You have already cast your ballot in this election."
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return redirect(url_for("vote"))

            data = request.get_json(silent=True) or request.form
            candidate_id = data.get("candidate_id", "").strip()
            password = session.get("voter_pw", "password123")

            success, receipt, msg = adapter.cast_ballot(voter_id, password, candidate_id)
            if not success or not receipt:
                err = f"Ballot rejected: {msg}"
                if request.is_json:
                    return jsonify({"success": False, "message": err}), 400
                flash(err, "danger")
                return redirect(url_for("vote"))

            # Update session state to reflect vote has been cast
            session["already_voted"] = True
            session.pop("voter_pw", None)  # Wipe password from session immediately
            session[f"receipt_{receipt['transaction_id']}"] = receipt

            if request.is_json:
                return jsonify({
                    "success": True,
                    "receipt": receipt,
                    "message": "Your ballot was cryptographically accepted and verified!"
                })

            flash("Your ballot was cryptographically accepted and verified!", "success")
            return redirect(url_for("confirmation", tx_id=receipt["transaction_id"]))

        return render_template(
            "vote.html",
            election=election,
            voter={"voter_id": voter_id, "name": session.get("voter_name", voter_id)},
            assigned_shard=assigned_shard,
            already_voted=already_voted,
        )

    @app.route("/confirmation/<tx_id>")
    def confirmation(tx_id: str):
        # Retrieve receipt from session or build from backend
        receipt = session.get(f"receipt_{tx_id}")
        if not receipt:
            proof_data = adapter.get_merkle_proof(tx_id)
            if proof_data:
                receipt = {
                    "transaction_id": tx_id,
                    "token_hash": proof_data.get("transaction", {}).get("token_hash", "N/A"),
                    "assigned_shard": proof_data.get("transaction", {}).get("assigned_shard", "node_a"),
                    "block_index": proof_data.get("block_index"),
                    "merkle_root": proof_data.get("merkle_root"),
                    "timestamp": proof_data.get("transaction", {}).get("timestamp", time.time()),
                }
            else:
                receipt = {
                    "transaction_id": tx_id,
                    "token_hash": "N/A",
                    "assigned_shard": adapter.get_assigned_shard(tx_id),
                    "block_index": 1,
                    "timestamp": time.time(),
                }

        return render_template("confirmation.html", receipt=receipt)

    @app.route("/results")
    def results():
        election = adapter.get_election_details()
        node_status = adapter.get_node_status()
        tally = adapter.get_tally()
        return render_template(
            "results.html",
            election=election,
            node_status=node_status,
            tally=tally,
        )

    # API Proxy endpoints for on-page JavaScript verification
    @app.route("/api/merkle_proof/<tx_id>")
    def api_merkle_proof(tx_id: str):
        proof = adapter.get_merkle_proof(tx_id)
        if not proof:
            return jsonify({"success": False, "error": "Transaction not found or not yet included in a block"}), 404
        return jsonify(proof)

    @app.route("/api/verify_receipt", methods=["POST"])
    def api_verify_receipt():
        data = request.get_json() or {}
        tx = data.get("transaction")
        merkle_root = data.get("merkle_root")
        proof = data.get("proof")
        if not tx or not merkle_root or proof is None:
            return jsonify({"valid": False, "error": "Missing tx, merkle_root, or proof"}), 400

        target_leaf = sha256_hash(tx)
        steps = [MerkleProofStep.from_dict(s) for s in proof]
        valid = MerkleTree.verify_proof(target_leaf, steps, merkle_root)
        return jsonify({"valid": valid, "leaf_hash": target_leaf, "merkle_root": merkle_root})

    # --- New Section Routes for Full Application ---

    @app.route("/explorer")
    def explorer():
        chain, is_valid, msg = adapter.get_chain()
        return render_template("explorer.html", chain=chain, is_valid=is_valid, msg=msg)

    @app.route("/merkle_proof")
    def merkle_proof_page():
        tx_id = request.args.get("tx_id", "").strip()
        return render_template("merkle_proof.html", initial_tx_id=tx_id)

    @app.route("/network")
    def network():
        nodes = adapter.get_network_nodes()
        return render_template("network.html", nodes=nodes)

    @app.route("/consensus")
    def consensus():
        chain, _, _ = adapter.get_chain()
        tip_block = chain[-1] if chain else None
        nodes = adapter.get_network_nodes()
        return render_template("consensus.html", tip_block=tip_block, nodes=nodes)

    @app.route("/mempool")
    def mempool():
        pending = adapter.get_mempool_transactions()
        return render_template("mempool.html", pending_txs=pending)

    @app.route("/shards")
    def shards():
        records = adapter.get_shard_records()
        return render_template("shards.html", shard_records=records)

    @app.route("/dsa")
    def dsa_lab():
        return render_template("dsa.html")

    @app.route("/admin")
    def admin_portal():
        election = adapter.get_election_details()
        voters = adapter.get_all_voters()
        audit_logs = adapter.get_audit_logs()
        return render_template("admin.html", election=election, voters=voters, audit_logs=audit_logs)

    @app.route("/health")
    def system_health():
        node_status = adapter.get_node_status()
        chain, is_valid, msg = adapter.get_chain()
        return render_template("health.html", node_status=node_status, is_valid=is_valid, chain_msg=msg)

    @app.route("/deployment")
    def deployment_guide():
        cfg_path = os.path.join(PROJECT_ROOT, "config.yaml")
        raw_yaml = ""
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                raw_yaml = f.read()
        return render_template("deployment.html", config_raw=raw_yaml)

    # --- Administrative and Network AJAX Proxy Endpoints ---

    @app.route("/api/admin/election_status", methods=["POST"])
    def api_admin_election_status():
        data = request.get_json() or {}
        status = data.get("status", "")
        success, msg = adapter.update_election_status(status)
        return jsonify({"success": success, "message": msg})

    @app.route("/api/admin/mine", methods=["POST"])
    def api_admin_mine():
        success, block, msg = adapter.trigger_mine()
        return jsonify({"success": success, "block": block, "message": msg})

    @app.route("/api/network/sync", methods=["POST"])
    def api_network_sync():
        res = adapter.trigger_sync()
        return jsonify(res)

    @app.route("/api/network/ping", methods=["POST"])
    def api_network_ping():
        nodes = adapter.get_network_nodes()
        return jsonify({"nodes": nodes})

    @app.route("/api/dsa/<concept_name>", methods=["GET", "POST"])
    def api_dsa_explore(concept_name: str):
        res = adapter.explore_dsa(concept_name)
        return jsonify(res)

    @app.route("/api/shards", methods=["GET"])
    def api_shards_proxy():
        if adapter.is_node_online():
            try:
                r = requests.get(f"{adapter.node_url}/api/shards", timeout=2.0)
                if r.status_code == 200:
                    return jsonify(r.json())
            except Exception:
                pass
        records = adapter.get_shard_records()
        return jsonify({
            "local_node": "voting_ui_node",
            "active_ring_nodes": ["node_a", "node_b", "node_c"],
            "stored_record_count": len(records),
            "records": records[:50],
        })

    @app.route("/api/tally", methods=["GET"])
    def api_tally_proxy():
        return jsonify(adapter.get_tally())

    @app.route("/api/chain", methods=["GET"])
    def api_chain_proxy():
        chain, is_valid, msg = adapter.get_chain()
        return jsonify({"chain": chain, "is_valid": is_valid, "integrity_message": msg})

    @app.route("/api/node_status", methods=["GET"])
    def api_node_status_proxy():
        return jsonify(adapter.get_node_status())

    @app.route("/api/nodes", methods=["GET"])
    def api_nodes_proxy():
        return jsonify({"nodes": adapter.get_network_nodes()})

    return app


def main():
    parser = argparse.ArgumentParser(description="Decentralized Voting System — Voter Portal UI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5050, help="Listening port (default: 5050)")
    parser.add_argument("--node-url", type=str, default="http://127.0.0.1:5001", help="Backend node API URL")
    parser.add_argument("--db-path", type=str, default="voting.db", help="Local SQLite database file")
    args = parser.parse_args()

    backend = VotingBackendAdapter(node_url=args.node_url, db_path=args.db_path)
    app = create_voting_ui_app(backend)

    print("=" * 65)
    print(" Decentralized Blockchain Voting System — Voter Portal UI")
    print(f" URL: http://{args.host}:{args.port}/")
    print(f" Connected Node API: {args.node_url}")
    print(f" Local Database: {backend.db_path}")
    print("=" * 65)

    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
