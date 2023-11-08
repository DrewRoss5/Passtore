import os
import re
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
        self.passwords['example.com - JohnDoe123'] =  {'password': 'password123!', 'salt': os.urandom(self.SALT_SIZE)}
        self.save_file()

    # generates a new password of a specified size from system entropy
    @classmethod
    def generate_password(self, size: int):
        return base64.b64encode(os.urandom(size)).decode()[:size]
    
    # returns the name of each site that there's a password for
    def get_password_names(self):
        return self.passwords.keys()

    # returns the password for a given name
    def get_password(self, password_name: str):
        return self.passwords[password_name]['password']

    # adds a new password to the file
    def add_password(self, password_name: str, username: str, password: str):
        self.passwords[f'{password_name} - {username}'] = {'password': password, 'salt': os.urandom(self.SALT_SIZE)}

    # deletes a password
    def delete_password(self, password_name: str):
        del self.passwords[password_name]

    # changes the password for a given site, but keeps the same salt
    def update_password(self, password_name: str, new_pass: str):
        self.passwords[password_name]['password'] = new_pass

    # recreates a password with a different name
    def rename_password(self, password_name: str, new_name: str):
        if new_name in self.passwords.keys():
            raise ValueError(f'A password name "{new_name}" already exists')
        password = self.passwords[password_name]
        self.passwords[new_name] = password
        del self.passwords[password_name]

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
                # decrypt the username and password
                key = SHA256.new(self.master_password.encode()+salt).digest()
                password = AESCipher(key).decrypt_and_verify(ciphertext_password)
                if password == None:
                    raise ValueError('Password file is corrupt or the key is invalid')
                self.passwords[name.decode()] = {'password': password.decode(), 'salt': salt}
            
    # encrypts and saves the file
    def save_file(self):
        # create a hash of the key to be used for verification purposes
        key_hash = bcrypt.hashpw(self.master_cipher.key, bcrypt.gensalt())
        # encrypt each password name, password salt, and password
        self.encrypted_passwords = []
        for i in self.passwords:
            password = self.passwords[i]
            # encrypt the site name, username  and salt
            ciphertext_salt_name = self.master_cipher.encrypt(password['salt'] + i.encode())
            # create the password's key by hashing the master password with it's salt
            key = SHA256.new(self.master_password.encode()+password['salt']).digest()
            password_cipher = AESCipher(key)
            # encrypt the password
            ciphertext_password = password_cipher.encrypt(password['password'])
            self.encrypted_passwords.append(b'!'.join((ciphertext_salt_name, ciphertext_password)))
        # write the key hash and the encrypted passwords to the file
        with open(self.file_path, 'wb') as f:
            f.write(b'\n'.join((key_hash, b'\n'.join(self.encrypted_passwords))))
         
    # creates a numeric grade for passwords, with 0-20 being poor, 20-29 being acceptable and 30+ being good 
    @classmethod
    def grade_password(self, password: str):
        # create a "modifier" for the password to be multiplied by, based on if it has uppercase letters, lowercase letters, numbers, and special symbols
        multiplier = 0
        for i in (r'[a-z]', r'[A-z]', r'[\d]', r'[!@#$%^&*()-=`~,.?\":{}|<>]'):
            if re.search(i, password):
                multiplier += 0.5
        # get the number of non repeating characters in the password
        char_count = 0
        previous_char = ''
        for i in password: 
            if i != previous_char:
                char_count += 1
            previous_char = i
        # get the final score by weighting the number of non_repeating characters by the multiplier
        return round(char_count * multiplier)
