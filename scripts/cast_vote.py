"""
Interactive CLI Script: Cast a Ballot in the Decentralized Voting System

Guides the user through:
1. Registering or Authenticating a Voter
2. Generating a decoupled single-use authorization token
3. Selecting a candidate
4. Submitting the anonymous ballot
5. Mining the block across the peer network
6. Displaying the cryptographic receipt
"""

import argparse
import json
import sys
import requests

DEFAULT_NODE = "http://127.0.0.1:5001"


def main():
    parser = argparse.ArgumentParser(description="Cast a ballot on the Decentralized Voting System")
    parser.add_argument("--node", type=str, default=DEFAULT_NODE, help="Node URL (default: http://127.0.0.1:5001)")
    parser.add_argument("--voter-id", type=str, default=None, help="Voter ID (e.g. voter_001)")
    parser.add_argument("--password", type=str, default="password123", help="Voter password (default: password123)")
    parser.add_argument("--candidate-id", type=str, default=None, help="Candidate ID (cand_01, cand_02, cand_03)")
    parser.add_argument("--auto-mine", action="store_true", help="Automatically trigger block mining after voting")

    args = parser.parse_args()
    node_url = args.node.rstrip("/")

    print("=" * 65)
    print(" Decentralized Blockchain Voting - Cast Ballot CLI")
    print(f" Target Node: {node_url}")
    print("=" * 65)

    # 1. Fetch Election Info & Candidate List
    try:
        resp = requests.get(f"{node_url}/api/node_info", timeout=3.0)
        if resp.status_code != 200:
            print(f"[!] Error connecting to {node_url}: HTTP {resp.status_code}")
            return
        node_info = resp.json()
    except Exception as e:
        print(f"[!] Cannot reach node at {node_url}: {e}")
        print("    Make sure the node or local network is running (`python3 main.py`).")
        return

    election = node_info.get("election", {})
    candidates = election.get("candidates", [])
    print(f"\n[*] Election: {election.get('title', 'Election')}")
    print(f"    Status: {election.get('status', 'OPEN')}")
    print("\nCandidates:")
    for c in candidates:
        print(f"  [{c['id']}] {c['name']} — {c.get('party', '')}")

    # 2. Get Voter ID
    voter_id = args.voter_id
    if not voter_id:
        voter_id = input("\nEnter Voter ID (e.g., voter_001): ").strip()
    password = args.password
    if not args.voter_id and not args.password:
        pw_input = input("Enter Password [default: password123]: ").strip()
        if pw_input:
            password = pw_input

    # 3. Authenticate and obtain single-use authorization token
    print(f"\n[1/3] Authenticating {voter_id} and issuing single-use voting token...")
    auth_resp = requests.post(
        f"{node_url}/api/voter/auth_token",
        json={"voter_id": voter_id, "password": password},
        timeout=3.0
    )

    if auth_resp.status_code != 200:
        error_msg = auth_resp.json().get("error", "Authentication failed")
        print(f"[!] FAILED: {error_msg}")
        return

    auth_data = auth_resp.json()
    token = auth_data["token"]
    print(f"[+] Authentication successful!")
    print(f"    Issued Token: {token[:16]}... (Decoupled from voter ID)")

    # 4. Candidate Selection
    candidate_id = args.candidate_id
    valid_ids = [c["id"] for c in candidates]
    if not candidate_id or candidate_id not in valid_ids:
        print("\nChoose Candidate:")
        for idx, c in enumerate(candidates, 1):
            print(f"  {idx}. {c['name']} ({c['id']})")
        choice = input(f"Select candidate [1-{len(candidates)}] or type ID: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            candidate_id = candidates[int(choice) - 1]["id"]
        elif choice in valid_ids:
            candidate_id = choice
        else:
            print("[!] Invalid candidate choice.")
            return

    # 5. Submit Ballot
    print(f"\n[2/3] Submitting anonymous ballot for candidate '{candidate_id}'...")
    ballot_resp = requests.post(
        f"{node_url}/api/submit_ballot",
        json={"candidate_id": candidate_id, "authorization_token": token},
        timeout=3.0
    )

    if ballot_resp.status_code != 200:
        error_msg = ballot_resp.json().get("error", "Ballot submission failed")
        print(f"[!] FAILED: {error_msg}")
        return

    ballot_data = ballot_resp.json()
    receipt = ballot_data.get("receipt", {})
    tx_id = receipt.get("transaction_id")
    print(f"[+] Ballot accepted and queued into mempool!")
    print(f"    Transaction ID: {tx_id}")
    print(f"    Assigned Shard: {receipt.get('assigned_shard')}")

    # 6. Mine Block (Consensus)
    mine_choice = "y" if args.auto_mine else input("\n[3/3] Mine block now to commit ballot to the blockchain? [Y/n]: ").strip().lower()
    if mine_choice in ["", "y", "yes"]:
        print("[*] Broadcasting candidate block for quorum consensus across peers...")
        mine_resp = requests.post(f"{node_url}/api/mine", timeout=5.0)
        if mine_resp.status_code == 200:
            mine_data = mine_resp.json()
            block = mine_data.get("block", {})
            print(f"[+] Block #{block.get('index')} successfully committed via quorum!")
            print(f"    Block Hash:  {block.get('hash')}")
            print(f"    Merkle Root: {block.get('merkle_root')}")
            print(f"    Transactions in Block: {len(block.get('transactions', []))}")
        else:
            print(f"[!] Mining note: {mine_resp.json().get('error', 'Pending in mempool')}")

    print("\n" + "=" * 65)
    print(" Vote successfully recorded!")
    print(f" Check your ballot on the Web Dashboard: {node_url}/")
    print("=" * 65)


if __name__ == "__main__":
    main()
