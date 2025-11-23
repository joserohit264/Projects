import os
import hashlib
import base64
from typing import Tuple

# PBKDF2 parameters
KDF_ITERATIONS = 200_000
HASH_NAME = "sha256"
SALT_LEN = 16
DERIVED_LEN = 32

def hash_password(password: str, salt_b64: str = None) -> Tuple[str, str]:
    """
    If salt_b64 is None -> generate salt.
    Returns (password_hash_b64, salt_b64)
    """
    if salt_b64:
        salt = base64.b64decode(salt_b64)
    else:
        salt = os.urandom(SALT_LEN)

    pwd_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode(),
        salt,
        KDF_ITERATIONS,
        dklen=DERIVED_LEN
    )

    return base64.b64encode(pwd_hash).decode(), base64.b64encode(salt).decode()

def verify_password(password: str, stored_hash_b64: str, stored_salt_b64: str) -> bool:
    computed_hash_b64, _ = hash_password(password, stored_salt_b64)
    return computed_hash_b64 == stored_hash_b64
