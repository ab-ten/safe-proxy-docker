import os
import sys
import base64
from cryptography.fernet import Fernet

def get_secret_key(secret_file_path=None):
  if secret_file_path is None:
    secret_file_path = os.getenv('SECRET_FILE', '/docker-volume/secret.key')
    
  if os.path.exists(secret_file_path):
    with open(secret_file_path, 'rb') as f:
      return f.read()
  else:
    secret_key = Fernet.generate_key()
    with open(secret_file_path, 'wb') as f:
      f.write(secret_key)
    return secret_key

def encrypt_key(api_key, secret_key):
  fernet = Fernet(secret_key)
  encrypted_key = fernet.encrypt(api_key.encode())
  return base64.urlsafe_b64encode(encrypted_key).decode()

def decrypt_key(encrypted_api_key, secret_key):
  fernet = Fernet(secret_key)
  decrypted_key = fernet.decrypt(base64.urlsafe_b64decode(encrypted_api_key.encode()))
  return decrypted_key.decode()

def main():
  if len(sys.argv) != 2:
    print("Usage: encrypt_key.py <api key string>")
    sys.exit(1)
  
  api_key = sys.argv[1]
  secret_key = get_secret_key()
  encrypted_api_key = encrypt_key(api_key, secret_key)
  print(encrypted_api_key)

if __name__ == "__main__":
  main()
