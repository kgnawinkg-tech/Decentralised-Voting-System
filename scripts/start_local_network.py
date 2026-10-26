"""
Script: Start 3-Node Local Simulation Network

Launches three independent nodes on separate ports (5001, 5002, 5003)
with separate SQLite databases and isolated storage directories.
Handles graceful shutdown of all nodes on SIGINT / Ctrl+C.
"""

import os
import signal
import subprocess
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

NODES = [
    {"id": "node_a", "port": 5001},
    {"id": "node_b", "port": 5002},
    {"id": "node_c", "port": 5003},
]

processes = []


def signal_handler(sig, frame):
    print("\n[!] Shutting down local 3-node simulation network...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            p.kill()
    print("[*] All node processes stopped.")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=================================================================")
    print(" Starting 3-Node Decentralized Simulation Network on Localhost")
    print(" - Node A: http://127.0.0.1:5001")
    print(" - Node B: http://127.0.0.1:5002")
    print(" - Node C: http://127.0.0.1:5003")
    print(" Press Ctrl+C at any time to gracefully terminate all nodes.")
    print("=================================================================\n")

    python_executable = sys.executable

    for n in NODES:
        cmd = [
            python_executable,
            os.path.join(PROJECT_ROOT, "app.py"),
            "--node-id", n["id"],
            "--port", str(n["port"]),
        ]
        log_file = open(os.path.join(PROJECT_ROOT, f"logs_{n['id']}.log"), "w")
        p = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STLOG if hasattr(subprocess, "STLOG") else log_file,
        )
        processes.append(p)
        print(f"[+] Started {n['id']} (PID {p.pid}) on port {n['port']}")
        time.sleep(0.5)

    print("\n[*] All nodes are running! Waiting for user interrupt (Ctrl+C)...")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
