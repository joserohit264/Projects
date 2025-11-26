import os
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Configuration
SALT_SIZE = 32
IV_SIZE = 16
KEY_SIZE = 32  # AES-256
ITERATIONS = 100000

def generate_salt():
    """Generates a random 32-byte salt."""
    return get_random_bytes(SALT_SIZE)

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 32-byte key from the password and salt using PBKDF2-HMAC-SHA256."""
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS, hmac_hash_module=SHA256)

def encrypt_password(password: str, key: bytes) -> bytes:
    """
    Encrypts a password using AES-256-CBC.
    Returns the IV prepended to the ciphertext.
    """
    iv = get_random_bytes(IV_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    return iv + ciphertext

def decrypt_password(encrypted_data: bytes, key: bytes) -> str:
    """
    Decrypts the encrypted data (IV + ciphertext) using the provided key.
    """
    iv = encrypted_data[:IV_SIZE]
    ciphertext = encrypted_data[IV_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode('utf-8')

def hash_master_password(password: str, salt: bytes) -> bytes:
    """
    Hashes the master password for storage/verification (separate from encryption key derivation).
    We can use the same KDF but maybe with a different salt or context if we wanted, 
    but typically we store the hash of the MP for auth.
    
    To avoid reusing the encryption key as the auth hash (which is bad practice),
    we can derive a master key, then hash that master key for auth, or derive two keys.
    
    For this implementation, we will derive a key for encryption, and a SEPARATE hash for authentication.
    Actually, the prompt says: "derive user-specific encryption keys from the master password combined with the user salt".
    And "PBKDF2-HMAC-SHA256 for password hashing".
    
    Standard practice:
    Auth Hash = PBKDF2(password, salt, iter=100000)
    Encryption Key = PBKDF2(password, salt, iter=100000) -> This would be the same.
    
    Better:
    Auth Hash = PBKDF2(password, salt, iter=100000)
    Encryption Key = PBKDF2(password, salt + b'enc', iter=100000)
    
    Let's stick to the prompt's requirements.
    "PBKDF2-HMAC-SHA256 for password hashing" -> This implies the stored password hash for login.
    "derive user-specific encryption keys from the master password combined with the user salt" -> This is for the vault.
    
    I will use the same salt but different 'info' or just different iterations or simple separation.
    Let's just use the same derivation for simplicity unless specified otherwise, but strictly speaking, 
    if the DB is leaked, and the hash is cracked, the key is known.
    
    To be safe:
    Auth Hash = PBKDF2(password, salt, 100000)
    Enc Key = PBKDF2(password, salt, 100001) (or just a different salt mix).
    
    Let's do:
    Auth Hash: PBKDF2(password, salt)
    Enc Key: PBKDF2(password, salt + b'encryption_key')
    """
    # For authentication
    return PBKDF2(password, salt, dkLen=32, count=ITERATIONS, hmac_hash_module=SHA256)

def derive_encryption_key(password: str, salt: bytes) -> bytes:
    # For encryption (different derivation to separate auth from encryption)
    # Using a modified salt effectively
    return PBKDF2(password, salt + b'encryption', dkLen=KEY_SIZE, count=ITERATIONS, hmac_hash_module=SHA256)
