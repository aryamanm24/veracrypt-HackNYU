from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path

def generate_key():
    random_key = os.urandom(32)
    base64_key = base64.b64encode(random_key).decode()
    
    # Get the path to the root directory
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / '.env'
    
    with open(env_path, 'a') as f:
        f.write(f'ENCRYPTION_KEY={base64_key}\n')
    
    print("New encryption key has been generated and saved to .env file")

if __name__ == "__main__":
    generate_key()