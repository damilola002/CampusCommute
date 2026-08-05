import base64
import hashlib
from django.conf import settings
from cryptography.fernet import Fernet

def get_fernet_cipher():
    # Derive a 32-byte key deterministically from Django's SECRET_KEY
    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

def encrypt_message(plain_text):
    if not plain_text:
        return ""
    cipher = get_fernet_cipher()
    return cipher.encrypt(plain_text.encode('utf-8')).decode('utf-8')

def decrypt_message(cipher_text):
    if not cipher_text:
        return ""
    cipher = get_fernet_cipher()
    return cipher.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
