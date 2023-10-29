import base64
import bcrypt
import os

from Crypto.Cipher import AES

# a simple class representing an AES256-GCM cipher
class AESCipher:
    def __init__(self, key):
        self.key = key
    
    # encrypts a plaintext, provided as either a string or raw bytes and returns the base64-encoded ciphertext, auth tag and nonce, seperated with a special character
    def encrypt(self, plaintext: [str | bytes]) -> tuple:
        # convert the plaintext to bytes if need-be
        if type(plaintext) == str:
            plaintext = plaintext.encode()
        # encrypt the plaintext
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext)
        return b':'.join(map(base64.b64encode, (ciphertext, auth_tag, cipher.nonce)))

    # decrypts ciphertext with a nonce, and verifies it's authenticity with an auth tag, returns None if the key is incorrect or the message cannot be verified
    def decrypt_and_verify(self, ciphertext: bytes) -> bytes:
        ciphertext, auth_tag, nonce = map(base64.b64decode, ciphertext.split(b':'))
        try:
            cipher = AES.new(self.key, AES.MODE_GCM, nonce)
            return cipher.decrypt_and_verify(ciphertext, auth_tag)
        except ValueError:
            return None

    # generates a random 256-bit key
    @classmethod
    def generate_random_key(self):
        return os.urandom(32)