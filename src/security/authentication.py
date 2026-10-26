"""
Authentication & Credential Security Module

Protects voter credentials using PBKDF2-HMAC-SHA256 with cryptographically random salts.
Never stores passwords or unhashed voter secrets in plain-text.
"""

import hashlib
import os
import secrets
from typing import Tuple


def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Returns (hashed_hex, salt_hex).
    """
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
    else:
        salt_bytes = bytes.fromhex(salt)
        salt_hex = salt

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        100000,
    )
    return key.hex(), salt_hex


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify an input password against stored hash and salt in constant time."""
    computed_hash, _ = hash_password(password, salt=salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def generate_auth_token(length: int = 32) -> str:
    """Generate cryptographically secure random token."""
    return secrets.token_urlsafe(length)
