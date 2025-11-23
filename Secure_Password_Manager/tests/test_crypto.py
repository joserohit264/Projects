from crypto_utils import derive_key, encrypt, decrypt

def test_encryption_cycle():
    key = derive_key("test123", b"12345678")
    cipher = encrypt("hello", key)
    plain = decrypt(cipher, key).decode()
    assert plain == "hello"
