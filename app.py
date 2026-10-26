"""
Application Entry Point

Launches a decentralized node API server and Web Dashboard.
Supports loading settings from config.yaml or overriding with CLI flags.
"""

import argparse
import os
import sys
import yaml
from src.networking.api import create_api_app
from src.networking.node import Node


def load_config(config_path: str = "config.yaml") -> dict:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    parser = argparse.ArgumentParser(description="Start a Decentralized Blockchain Voting Node")
    parser.add_argument("--node-id", type=str, default="node_a", help="Unique Node ID (e.g., node_a, node_b, node_c)")
    parser.add_argument("--host", type=str, default=None, help="Host interface (e.g., 127.0.0.1 or 0.0.0.0 for LAN)")
    parser.add_argument("--port", type=int, default=None, help="Listening port (e.g., 5001, 5002, 5003)")
    parser.add_argument("--db-path", type=str, default=None, help="Path to local independent SQLite database")
    parser.add_argument("--peers", nargs="*", default=None, help="Space-separated list of peer URLs")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")

    args = parser.parse_args()
    config = load_config(args.config)

    node_cfg = config.get("network", {}).get("nodes", {}).get(args.node_id, {})
    host = args.host or node_cfg.get("host", "127.0.0.1")
    port = args.port or node_cfg.get("port", 5001)
    db_path = args.db_path or node_cfg.get("db_path", f"data/{args.node_id}/{args.node_id}.db")
    peer_endpoints = args.peers if args.peers is not None else node_cfg.get("peers", [])
    virtual_nodes = config.get("sharding", {}).get("virtual_nodes", 50)
    quorum_size = config.get("consensus", {}).get("quorum_size", 2)
    election_cfg = config.get("election", {})

    node_name = node_cfg.get("name", f"Node {args.node_id.upper()}")

    print(f"============================================================")
    print(f" Starting Decentralized Voting Node: {args.node_id} ({node_name})")
    print(f" Host: {host} | Port: {port} | DB: {db_path}")
    print(f" Configured Peers: {peer_endpoints}")
    print(f" Web Dashboard URL: http://{host}:{port}/")
    print(f"============================================================")

    node = Node(
        node_id=args.node_id,
        name=node_name,
        host=host,
        port=port,
        db_path=db_path,
        peer_endpoints=peer_endpoints,
        virtual_nodes=virtual_nodes,
        quorum_size=quorum_size,
        election_config=election_cfg,
    )

    app = create_api_app(node)
    # Run Flask server
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
