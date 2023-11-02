import os
import json 
import bcrypt
import base64


from Crypto.Hash import SHA256

from crypto.aes import AESCipher

class PasswordDatabase:
    SALT_SIZE = 16
    def __init__(self, file_path: str, password: str):
        self.file_path = file_path
        self.master_password = password
        self.passwords = {}
        self.master_cipher = None

    # creates a new password database file, given a password and file path
    def create_file(self):
        # create an AES-256 key from the provided password
        key = SHA256.new(self.master_password.encode()).digest()
        self.master_cipher = AESCipher(key)
        # create a placeholder password then encrypt and save he file
        self.passwords['example.com'] =  {'password': 'password123!', 'salt': os.urandom(self.SALT_SIZE)}
        self.save_file()

    # generates a new password of a specified size from system entropy
    @classmethod
    def generate_password(self, size: int):
        return base64.b64encode(os.urandom(size)).decode()[:size]
    
    # returns the name of each site that there's a password for
    def get_site_names(self):
        return self.passwords.keys()

    # returns the password for a given name
    def get_password(self, site_name: str):
        return self.passwords[site_name]['password']

    # adds a new password to the file
    def add_password(self, site_name: str, password: str):
        self.passwords[site_name] = {'salt': os.urandom(self.SALT_SIZE), 'password': password}

    # deletes a password
    def delete_password(self, site_name: str):
        del self.passwords[site_name]

    # changes the password for a given site, but keeps the same salt
    def update_password(self, site_name: str, new_pass: str):
        self.passwords[site_name]['password'] = new_pass

    # recreates a password with a different name
    def rename_password(self, site_name: str, new_name: str):
        if new_name in self.passwords.keys():
            raise ValueError(f'A password name "{new_name}" already exists')
        password = self.passwords[site_name]
        self.passwords[new_name] = password
        del self.passwords[site_name]

    # decrypts the file's contents
    def load_file(self):
        # read the file's content
        with open(self.file_path, 'rb') as f:
            lines = f.read().split(b'\n')
            key_hash = lines[0]
            encrypted_passwords = lines[1:]
        # create a key from the provided password and verify it
        key = SHA256.new(self.master_password.encode()).digest()
        self.master_cipher = AESCipher(key)
        if not bcrypt.checkpw(key, key_hash):
            raise ValueError('Incorrect Password')
        # decrypt each password 
        for i in encrypted_passwords:
            # ensure the password is not an empty line before attempting to decrypt it
            if i:
                ciphertext_salt_name, ciphertext_password = i.split(b'!')
                # decrypt the password's name and salt
                salt_name = self.master_cipher.decrypt_and_verify(ciphertext_salt_name)
                if not salt_name:
                    raise ValueError('Password file is corrupt or the key is invalid')
                salt = salt_name[:self.SALT_SIZE]
                name = salt_name[self.SALT_SIZE:]
                # decrypt the password's content
                key = SHA256.new(self.master_password.encode()+salt).digest()
                password = AESCipher(key).decrypt_and_verify(ciphertext_password).decode()
                if password == None:
                    raise ValueError('Password file is corrupt or the key is invalid')
                self.passwords[name.decode()] = {'password': password, 'salt': salt}
            
    # encrypts and saves the file
    def save_file(self):
        # create a hash of the key to be used for verification purposes
        key_hash = bcrypt.hashpw(self.master_cipher.key, bcrypt.gensalt())
        # encrypt each password name, password salt, and password
        self.encrypted_passwords = []
        for i in self.passwords:
            password = self.passwords[i]
            # create the password's key by hashing the master password with it's salt
            key = SHA256.new(self.master_password.encode()+password['salt']).digest()
            # encrypt the password
            ciphertext_password = AESCipher(key).encrypt(password['password'])
            # encrypt the password's name and salt
            ciphertext_salt_name = self.master_cipher.encrypt(password['salt']+i.encode())
            self.encrypted_passwords.append(b'!'.join((ciphertext_salt_name, ciphertext_password)))
        # write the key hash and the encrypted passwords to the file
        with open(self.file_path, 'wb') as f:
            f.write(b'\n'.join((key_hash, b'\n'.join(self.encrypted_passwords))))
         
