import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import config


def _get_key() -> bytes:
    raw = config.CIPHER_KEY
    if not raw:
        raise ValueError("CIPHER_KEY is not set in environment")
    b = base64.b64decode(raw)
    if len(b) not in (16, 24, 32):
        raise ValueError("CIPHER_KEY must decode to 16, 24, or 32 bytes")
    return b


def seal(plaintext: str) -> str:
    key = _get_key()
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def unseal(ciphertext: str) -> str:
    key = _get_key()
    raw = base64.b64decode(ciphertext)
    nonce, ct = raw[:12], raw[12:]
    plaintext = AESGCM(key).decrypt(nonce, ct, None)
    return plaintext.decode()
