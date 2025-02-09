from cryptography.fernet import Fernet
import base64
import json

class Encryptor:
    def __init__(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')
            key = key.ljust(32, b'0')
            key = key[:32]
            key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(key)

    def encrypt_data(self, data):
        json_data = json.dumps(data)
        return self.fernet.encrypt(json_data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        decrypted_data = self.fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_data.decode())