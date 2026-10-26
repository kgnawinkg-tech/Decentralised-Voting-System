"""
DSA Module 23: Digital Signatures (ECDSA SECP256R1)

Complexity:
- Key Generation: O(1)
- Sign Message: O(1) (~milliseconds, ECC curve scalar multiplication)
- Verify Signature: O(1) (~milliseconds)
- Key Size: 256 bits (SECP256R1)

Integration:
- Authenticates inter-node messages, block proposal envelopes, and voter transaction envelopes.
- Rejects tampered messages, unauthorized block proposals, and forged endorsements.
"""

import base64
from typing import Any, Dict, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from src.security.hashing import canonical_json_bytes


class KeyPair:
    """Manages an ECDSA (SECP256R1) private and public key pair."""

    def __init__(self, private_key: Optional[ec.EllipticCurvePrivateKey] = None):
        self._private_key: ec.EllipticCurvePrivateKey = (
            private_key if private_key else ec.generate_private_key(ec.SECP256R1())
        )
        self._public_key: ec.EllipticCurvePublicKey = self._private_key.public_key()

    @classmethod
    def generate(cls) -> "KeyPair":
        """Generate a fresh ECDSA keypair."""
        return cls()

    def get_public_pem(self) -> str:
        """Export public key in PEM format string."""
        pem_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem_bytes.decode("utf-8")

    def get_private_pem(self) -> str:
        """Export private key in PEM format string."""
        pem_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pem_bytes.decode("utf-8")

    @classmethod
    def from_private_pem(cls, pem_str: str) -> "KeyPair":
        """Load KeyPair from private key PEM string."""
        private_key = serialization.load_pem_private_key(
            pem_str.encode("utf-8"), password=None
        )
        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            raise TypeError("Loaded key is not an EllipticCurvePrivateKey")
        return cls(private_key=private_key)

    def sign(self, data: Any) -> str:
        """
        Sign arbitrary string, bytes, or structured data dict.
        Returns base64-encoded signature string.
        """
        if isinstance(data, bytes):
            payload_bytes = data
        elif isinstance(data, str):
            payload_bytes = data.encode("utf-8")
        else:
            payload_bytes = canonical_json_bytes(data)

        signature_bytes = self._private_key.sign(payload_bytes, ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature_bytes).decode("utf-8")


def verify_signature(public_pem: str, data: Any, signature_b64: str) -> bool:
    """
    Verify ECDSA signature against public key PEM and data.
    Returns True if valid, False if tampered or invalid.
    """
    try:
        public_key = serialization.load_pem_public_key(public_pem.encode("utf-8"))
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            return False

        if isinstance(data, bytes):
            payload_bytes = data
        elif isinstance(data, str):
            payload_bytes = data.encode("utf-8")
        else:
            payload_bytes = canonical_json_bytes(data)

        sig_bytes = base64.b64decode(signature_b64.encode("utf-8"))
        public_key.verify(sig_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def create_signed_envelope(keypair: KeyPair, payload: Dict[str, Any], sender_id: str) -> Dict[str, Any]:
    """Create a verifiable transmission envelope with attached signature."""
    sig = keypair.sign(payload)
    return {
        "sender_id": sender_id,
        "public_key": keypair.get_public_pem(),
        "payload": payload,
        "signature": sig,
    }


def verify_signed_envelope(envelope: Dict[str, Any]) -> bool:
    """Verify an incoming transmission envelope's signature."""
    try:
        pub_key = envelope["public_key"]
        payload = envelope["payload"]
        sig = envelope["signature"]
        return verify_signature(pub_key, payload, sig)
    except (KeyError, TypeError):
        return False
