import os
import tempfile
import pytest
import yaml
import sqlite3
from db_setup import validate_config, convert_config_to_db
from encrypt_key import get_secret_key, encrypt_key

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def config_file(temp_dir):
    secret_key = get_secret_key()
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/',
                'authentication': {
                    'type': 'Bearer',
                    'keys': {
                        'dummy-key-1': encrypt_key('real-api-key-1', secret_key),
                        'dummy-key-2': encrypt_key('real-api-key-2', secret_key)
                    }
                }
            }
        }
    }
    config_file_path = os.path.join(temp_dir, 'config.yaml')
    with open(config_file_path, 'w') as f:
        yaml.dump(config, f)
    return config_file_path

@pytest.fixture
def db_file(temp_dir):
    return os.path.join(temp_dir, 'proxy.sqlite')

def test_validate_config_valid(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    validate_config(config)

def test_validate_config_invalid_missing_servers():
    config = {}
    with pytest.raises(ValueError, match="Invalid config: 'servers' section is missing"):
        validate_config(config)

def test_validate_config_invalid_missing_origin():
    config = {
        'servers': {
            'server1': {
                'authentication': {
                    'type': 'Bearer',
                    'keys': {
                        'dummy-key-1': 'real-api-key-1-encrypted'
                    }
                }
            }
        }
    }
    with pytest.raises(ValueError, match="Invalid config: 'origin' is missing for server server1"):
        validate_config(config)

def test_validate_config_invalid_missing_authentication():
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/'
            }
        }
    }
    with pytest.raises(ValueError, match="Invalid config: 'authentication/type' is missing for server server1"):
        validate_config(config)

def test_validate_config_invalid_unsupported_authentication_type():
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/',
                'authentication': {
                    'type': 'UnsupportedType',
                    'keys': {
                        'dummy-key-1': 'real-api-key-1-encrypted'
                    }
                }
            }
        }
    }
    with pytest.raises(ValueError, match="Invalid config: unsupported authentication type for server server1"):
        validate_config(config)

def test_validate_config_invalid_missing_keys():
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/',
                'authentication': {
                    'type': 'Bearer'
                }
            }
        }
    }
    with pytest.raises(ValueError, match="Invalid config: 'keys' are missing for server server1"):
        validate_config(config)

def test_convert_config_to_db(config_file, db_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    validate_config(config)
    convert_config_to_db(config, db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ORIGIN")
    origin_rows = cursor.fetchall()
    assert len(origin_rows) == 1
    assert origin_rows[0] == ('server1', 'https://api.server1.com/')

    cursor.execute("SELECT * FROM KEY_MAPPING")
    key_mapping_rows = cursor.fetchall()
    assert len(key_mapping_rows) == 2
    assert key_mapping_rows[0][0] == 'server1'
    assert key_mapping_rows[1][0] == 'server1'

    conn.close()

def test_convert_config_to_db_edge_cases(temp_dir):
    # Edge case: empty config
    config = {}
    db_file_path = os.path.join(temp_dir, 'proxy_empty.sqlite')
    with pytest.raises(ValueError, match="Invalid config: 'servers' section is missing"):
        validate_config(config)
        convert_config_to_db(config, db_file_path)

    # Edge case: missing keys
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/',
                'authentication': {
                    'type': 'Bearer'
                }
            }
        }
    }
    db_file_path = os.path.join(temp_dir, 'proxy_missing_keys.sqlite')
    with pytest.raises(ValueError, match="Invalid config: 'keys' are missing for server server1"):
        validate_config(config)
        convert_config_to_db(config, db_file_path)

    # Edge case: unsupported authentication type
    config = {
        'servers': {
            'server1': {
                'origin': 'https://api.server1.com/',
                'authentication': {
                    'type': 'UnsupportedType',
                    'keys': {
                        'dummy-key-1': 'real-api-key-1-encrypted'
                    }
                }
            }
        }
    }
    db_file_path = os.path.join(temp_dir, 'proxy_unsupported_auth.sqlite')
    with pytest.raises(ValueError, match="Invalid config: unsupported authentication type for server server1"):
        validate_config(config)
        convert_config_to_db(config, db_file_path)
