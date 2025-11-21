# crypto_utils.py
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Key generation / serialization
def generate_private_key(curve_name="SECP256R1"):
    curve = {"SECP256R1": ec.SECP256R1(), "SECP256K1": ec.SECP256K1()}[curve_name]
    return ec.generate_private_key(curve)

def serialize_public_key(pubkey) -> str:
    pem = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode()

def load_public_key(pem_str):
    return serialization.load_pem_public_key(pem_str.encode())

def serialize_private_key(privkey, password: bytes = None) -> str:
    alg = serialization.NoEncryption() if password is None else serialization.BestAvailableEncryption(password)
    pem = privkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=alg
    )
    return pem.decode()

def load_private_key(pem_str, password: bytes = None):
    return serialization.load_pem_private_key(pem_str.encode(), password=password)

# Derive symmetric key from ECDH shared secret
def derive_shared_key(privkey, peer_pubkey, length=32) -> bytes:
    shared = privkey.exchange(ec.ECDH(), peer_pubkey)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=b"ecdh-aes-key",
    )
    return hkdf.derive(shared)

# AES-GCM encrypt/decrypt helpers (base64 encode for transport)
def encrypt_message(aes_key: bytes, plaintext: bytes) -> str:
    aesgcm = AESGCM(aes_key)
    iv = os.urandom(12)
    ct = aesgcm.encrypt(iv, plaintext, associated_data=None)
    return base64.b64encode(iv + ct).decode()

def decrypt_message(aes_key: bytes, token_b64: str) -> bytes:
    data = base64.b64decode(token_b64)
    iv = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(iv, ct, associated_data=None)
