"""
Decentralized Blockchain Voting System — Main Unified Launcher

Usage:
  python3 main.py              # Starts the full 3-node decentralized network (Nodes A, B, C)
  python3 main.py --network    # Starts the 3-node simulation network
  python3 main.py --node-id A  # Starts an individual node (Node A on port 5001)
  python3 main.py --single     # Starts only Node A (port 5001)
  python3 main.py --demo       # Runs the 20-step automated end-to-end demonstration
  python3 main.py --test       # Runs the automated test suite (pytest)
"""

import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Decentralized Blockchain Voting System - Unified Launcher",
        add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show help message")
    parser.add_argument("--network", action="store_true", help="Start the full 3-node simulation network (Default)")
    parser.add_argument("--demo", action="store_true", help="Execute the 20-step automated end-to-end demonstration")
    parser.add_argument("--test", action="store_true", help="Run the automated test suite (pytest)")
    parser.add_argument("--single", action="store_true", help="Start only a single node (Node A on port 5001)")
    parser.add_argument("--node-id", type=str, default=None, help="Start a specific node (node_a, node_b, node_c)")

    args, unknown = parser.parse_known_args()

    if args.help:
        print(__doc__)
        parser.print_help()
        sys.exit(0)

    if args.demo:
        from scripts.run_demo import main as demo_main
        demo_main()
        return

    if args.test:
        import pytest
        sys.exit(pytest.main(["tests/"]))

    if args.node_id or args.single or any(k in unknown for k in ["--port", "--db-path", "--peers", "--host"]):
        from app import main as app_main
        clean_argv = [sys.argv[0]] + unknown
        if args.node_id:
            clean_argv.extend(["--node-id", args.node_id])
        sys.argv = clean_argv
        app_main()
        return

    # Default action: Launch the full 3-node simulation network so all peers & consensus work
    from scripts.start_local_network import main as network_main
    network_main()


if __name__ == "__main__":
    main()