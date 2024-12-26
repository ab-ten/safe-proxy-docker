#!/usr/bin/env python3
import os
import yaml
import sqlite3
from encrypt_key import get_secret_key, decrypt_key

def get_config_file_path():
  return os.getenv('CONFIG_FILE', '/app/config.yaml')

def get_db_file_path():
  return os.getenv('PROXY_DB_FILE', '/tmpfs/proxy.sqlite')

def validate_config(config):
  if 'servers' not in config:
    raise ValueError("Invalid config: 'servers' section is missing")
  for server_name, server_data in config['servers'].items():
    if 'origin' not in server_data:
      raise ValueError(f"Invalid config: 'origin' is missing for server {server_name}")
    if 'authentication' not in server_data or 'type' not in server_data['authentication']:
      raise ValueError(f"Invalid config: 'authentication/type' is missing for server {server_name}")
    if server_data['authentication']['type'] != 'Bearer':
      raise ValueError(f"Invalid config: unsupported authentication type for server {server_name}")
    if 'keys' not in server_data['authentication']:
      raise ValueError(f"Invalid config: 'keys' are missing for server {server_name}")

def convert_config_to_db(config, db_file_path):
  conn = sqlite3.connect(db_file_path)
  cursor = conn.cursor()

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS ORIGIN (
      server_name TEXT PRIMARY KEY,
      origin TEXT NOT NULL
    )
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS KEY_MAPPING (
      server_name TEXT,
      client_dummy_key TEXT,
      plain_real_api_key TEXT,
      UNIQUE(server_name, client_dummy_key)
    )
  ''')

  secret_key = get_secret_key()

  for server_name, server_data in config['servers'].items():
    cursor.execute('INSERT OR IGNORE INTO ORIGIN (server_name, origin) VALUES (?, ?)',
                   (server_name, server_data['origin']))

    for dummy_key, encrypted_real_key in server_data['authentication']['keys'].items():
      real_key = decrypt_key(encrypted_real_key, secret_key)
      cursor.execute('''
        INSERT OR IGNORE INTO KEY_MAPPING (server_name, client_dummy_key, plain_real_api_key)
        VALUES (?, ?, ?)
      ''', (server_name, dummy_key, real_key))

  conn.commit()
  conn.close()

def main():
  config_file_path = get_config_file_path()
  db_file_path = get_db_file_path()

  if not os.path.exists(config_file_path):
    raise FileNotFoundError(f"Config file not found: {config_file_path}")

  with open(config_file_path, 'r') as f:
    config = yaml.safe_load(f)

  try:
    validate_config(config)
  except ValueError as e:
    print(f"Error validating config: {e}")
    return

  try:
    convert_config_to_db(config, db_file_path)
    print(f"Successfully converted config to database at {db_file_path}")
  except Exception as e:
    print(f"Error converting config to database: {e}")

if __name__ == "__main__":
  main()
