"""
Input Validation & Sanitization Module

Enforces strict schemas, character validation, and length constraints on all incoming requests
to prevent injection, buffer overruns, and malformed transactions.
"""

import re
from typing import Any, Dict, List, Optional


class ValidationError(ValueError):
    """Raised when request payload or transaction fails validation."""
    pass


# Strict alphanumeric regex with underscores and hyphens
SAFE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")
HEX_64_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


def validate_id(identifier: str, field_name: str = "id") -> str:
    """Validate that identifier contains only safe alphanumeric, dash, and underscore characters."""
    if not isinstance(identifier, str):
        raise ValidationError(f"{field_name} must be a string")
    ident = identifier.strip()
    if not SAFE_ID_REGEX.match(ident):
        raise ValidationError(f"Invalid {field_name}: '{identifier}'. Must be 1-64 alphanumeric chars, dash, dot, or underscore.")
    return ident


def validate_hash(hex_string: str, field_name: str = "hash") -> str:
    """Validate 64-char SHA-256 hex string."""
    if not isinstance(hex_string, str) or not HEX_64_REGEX.match(hex_string):
        raise ValidationError(f"Invalid {field_name}: '{hex_string}'. Expected 64-character SHA-256 hex string.")
    return hex_string.lower()


def sanitize_text(text: str, max_length: int = 256) -> str:
    """Sanitize arbitrary user text string."""
    if not isinstance(text, str):
        return ""
    # Strip dangerous HTML/script tags
    clean = re.sub(r"[<>]", "", text).strip()
    return clean[:max_length]


def validate_ballot_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate incoming ballot transaction payload."""
    required = ["candidate_id", "authorization_token"]
    for field in required:
        if field not in data:
            raise ValidationError(f"Missing required ballot field: '{field}'")

    candidate_id = validate_id(data["candidate_id"], "candidate_id")
    auth_token = str(data["authorization_token"]).strip()
    if len(auth_token) < 16 or len(auth_token) > 128:
        raise ValidationError("Invalid authorization token length (must be 16-128 chars)")

    return {
        "candidate_id": candidate_id,
        "authorization_token": auth_token,
    }
