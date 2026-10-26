"""
Script: Register Synthetic Demo Voters

Pre-registers realistic synthetic voters for demonstrations and testing.
"""

import os
import sys
import requests

DEMO_VOTERS = [
    {"voter_id": "voter_001", "name": "Nawin Kumar", "password": "password123"},
    {"voter_id": "voter_002", "name": "Alice Smith", "password": "password123"},
    {"voter_id": "voter_003", "name": "Bob Jones", "password": "password123"},
    {"voter_id": "voter_004", "name": "Carol Williams", "password": "password123"},
    {"voter_id": "voter_005", "name": "David Brown", "password": "password123"},
    {"voter_id": "voter_006", "name": "Emma Wilson", "password": "password123"},
    {"voter_id": "voter_007", "name": "Frank Garcia", "password": "password123"},
    {"voter_id": "voter_008", "name": "Grace Miller", "password": "password123"},
    {"voter_id": "voter_009", "name": "Henry Davis", "password": "password123"},
    {"voter_id": "voter_010", "name": "Isabella Rodriguez", "password": "password123"},
]


def register_voters(target_node_url: str = "http://127.0.0.1:5001"):
    print(f"[*] Registering demo synthetic voters on {target_node_url}...")
    success_count = 0

    for v in DEMO_VOTERS:
        try:
            resp = requests.post(
                f"{target_node_url.rstrip('/')}/api/voter/register",
                json=v,
                timeout=3.0,
            )
            if resp.status_code == 200:
                print(f"  [+] Registered: {v['voter_id']} ({v['name']})")
                success_count += 1
            else:
                data = resp.json()
                print(f"  [!] {v['voter_id']}: {data.get('error', data.get('message'))}")
        except Exception as e:
            print(f"  [-] Failed to connect to {target_node_url}: {e}")
            break

    print(f"[*] Completed registration: {success_count}/{len(DEMO_VOTERS)} registered.")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5001"
    register_voters(url)
