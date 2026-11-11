"""Password hashing and verification using PBKDF2-HMAC-SHA256."""

from __future__ import annotations

import hashlib
import hmac
import os

ITERATIONS = 200_000
ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    """Hash a plaintext password with a random salt using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac(ALGORITHM, password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2:{ALGORITHM}:{ITERATIONS}${salt.hex()}${key.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a plaintext password against a stored password hash."""
    if not password_hash or not password_hash.startswith(f"pbkdf2:{ALGORITHM}:"):
        return False
    try:
        header, salt_hex, key_hex = password_hash.split("$")
        _, _, iterations_str = header.split(":")
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac(ALGORITHM, password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False

