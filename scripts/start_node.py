"""
Script: Start a Single Node from CLI
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import main

if __name__ == "__main__":
    main()
