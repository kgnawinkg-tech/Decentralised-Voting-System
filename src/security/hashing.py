"""
DSA Module 22: SHA-256 Cryptographic Hashing & Deterministic Serialization

Complexity:
- Time: O(M) where M is message length in bytes
- Space: O(1) fixed 256-bit (32-byte / 64-hex char) output digest

Integration:
- Calculates block hashes, transaction IDs, state commitments, and validates chain tampering.
- Employs canonical deterministic serialization so identical structured objects always yield
  identical cryptographic hashes across physical nodes.
"""

import hashlib
import json
from typing import Any, Dict


def canonical_json_bytes(data: Any) -> bytes:
    """
    Produce canonical, deterministic JSON bytes for cryptographic hashing.
    Enforces sorted keys, compact separators (',', ':'), and strict UTF-8 encoding.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hash(data: Any) -> str:
    """
    Compute SHA-256 hex digest of string, bytes, or structured dict/list.
    Structured objects are deterministically serialized.
    """
    if isinstance(data, bytes):
        raw_bytes = data
    elif isinstance(data, str):
        raw_bytes = data.encode("utf-8")
    else:
        raw_bytes = canonical_json_bytes(data)

    return hashlib.sha256(raw_bytes).hexdigest()


def double_sha256(data: Any) -> str:
    """Compute SHA-256(SHA-256(data)) for enhanced collision resistance."""
    first = sha256_hash(data)
    return sha256_hash(first)


def verify_content_integrity(data: Any, expected_hash: str) -> bool:
    """Verify that the computed hash of data matches the expected hash."""
    return sha256_hash(data) == expected_hash
