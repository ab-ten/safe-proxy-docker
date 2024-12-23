import os
import tempfile
import pytest
from encrypt_key import get_secret_key, encrypt_key, decrypt_key

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def secret_file(temp_dir):
    return os.path.join(temp_dir, 'secret.key')

def test_get_secret_key(secret_file):
    secret_key = get_secret_key(secret_file)
    assert os.path.exists(secret_file)
    assert secret_key == get_secret_key(secret_file)

def test_encrypt_decrypt_key(secret_file):
    secret_key = get_secret_key(secret_file)
    api_key = "test-api-key"
    encrypted_key = encrypt_key(api_key, secret_key)
    decrypted_key = decrypt_key(encrypted_key, secret_key)
    assert api_key == decrypted_key

def test_encrypt_key_with_different_secret_keys(temp_dir):
    secret_file_1 = os.path.join(temp_dir, 'secret1.key')
    secret_file_2 = os.path.join(temp_dir, 'secret2.key')
    secret_key_1 = get_secret_key(secret_file_1)
    secret_key_2 = get_secret_key(secret_file_2)
    api_key = "test-api-key"
    encrypted_key_1 = encrypt_key(api_key, secret_key_1)
    encrypted_key_2 = encrypt_key(api_key, secret_key_2)
    assert encrypted_key_1 != encrypted_key_2
    assert decrypt_key(encrypted_key_1, secret_key_1) == api_key
    assert decrypt_key(encrypted_key_2, secret_key_2) == api_key

def test_get_secret_key_default_path(monkeypatch, temp_dir):
    default_secret_file = os.path.join(temp_dir, 'default_secret.key')
    monkeypatch.setenv('SECRET_FILE', default_secret_file)
    secret_key = get_secret_key()
    assert os.path.exists(default_secret_file)
    assert secret_key == get_secret_key(default_secret_file)

def test_encrypt_decrypt_key_with_default_secret_file(monkeypatch, temp_dir):
    default_secret_file = os.path.join(temp_dir, 'default_secret.key')
    monkeypatch.setenv('SECRET_FILE', default_secret_file)
    secret_key = get_secret_key()
    api_key = "test-api-key"
    encrypted_key = encrypt_key(api_key, secret_key)
    decrypted_key = decrypt_key(encrypted_key, secret_key)
    assert api_key == decrypted_key
