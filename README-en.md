# safe-proxy-docker

[Japanese README](README.md)

## Purpose

The main purpose of this project is to create a secure reverse proxy for multiple API servers using Docker. The proxy replaces client dummy keys with real API keys to ensure secure connections. The project involves setting up configurations, encrypting API keys, and using Nginx for proxy handling.

## Feature Introduction

The key features of this project are:

- **Secure reverse proxy**: The project creates a secure reverse proxy for multiple API servers using Docker, ensuring secure connections by replacing client dummy keys with real API keys.
- **Configuration-based setup**: The proxy is configured using a `config.yaml` file, which defines the server configurations, including API endpoints and authentication details.
- **API key encryption**: Real API keys are encrypted and stored in the `config.yaml` file. The project provides utilities for encrypting API keys and setting up the environment.
- **Nginx with Lua module**: The project uses Nginx with the Lua module to handle proxy requests and authentication, ensuring efficient and secure processing of requests.
- **SQLite database**: The configurations from `config.yaml` are converted to a SQLite database for efficient access during runtime.
- **Docker integration**: The project is designed to run within a Docker container, with specific instructions for setting up the Docker environment, including creating a Docker network and using `docker compose` commands.
- **Environment variables**: The project allows customization of file paths and other settings using environment variables, providing flexibility in deployment.
- **Secure handling of API keys**: The project ensures secure handling of API keys and configurations within the Docker container, with encrypted keys being decrypted during runtime and stored in a temporary SQLite database.
- **Utilities for key management**: The project includes utilities like `encrypt_key.py` for encrypting API keys and setting up the environment, making it easier to manage API keys securely.

## Usage

### Step-by-step

1. Ensure you have Docker installed and running on your system.
2. Create a Docker network named `safe_proxy_docker` by running the command:
   ```sh
   docker network create safe_proxy_docker
   ```
3. Prepare your real API key that you want to encrypt.
4. Use the `encrypt_key.py` script to encrypt your real API key. You can do this by running the following command:
   ```sh
   docker compose run --rm --entrypoint /usr/local/bin/encrypt_key.py api_proxy YOUR_API_KEY
   ```
   Replace `YOUR_API_KEY` with your actual API key. This command will output the encrypted API key.
5. Copy the encrypted API key and update the `config.yaml` file with the encrypted key. You can use the `config.yaml.sample` as a reference. For example:
   ```yaml
   servers:
     openai:
       origin: "https://api.openai.com/"
       authentication:
         type: "Bearer"
         keys:
           "sk-proj-1": "ENCRYPTED_API_KEY"
   ```
   Replace `ENCRYPTED_API_KEY` with the encrypted key you obtained in the previous step.
6. Save the updated `config.yaml` file in the root directory of the project.
7. Copy the `.env.sample` file to `.env` and edit it if necessary. For example, to change the host machine port, set the `HOST_PORT`:
   ```sh
   cp .env.sample .env
   ```
   If using the default value, there is no need to create or edit the `.env` file.

### Use `docker compose` command

- Start `safe-proxy-docker` by running `docker compose up -d` or `docker compose up`.

### Usage from other docker containers

- Add a setting to use the `safe_proxy_docker` network.
- If your program uses OpenAI modules/libraries, set the following environment variables:
  ```sh
  export OPENAI_API_BASE=http://api_proxy/openai/v1/
  export OPENAI_API_KEY=<DUMMY_KEY_AS_YOU_SET>
  ```
- Ensure `safe-proxy-docker` is running by executing `docker compose up -d` or `docker compose up`.

### Usage from host environment

- Set the following environment variables, similar to the container case:
  ```sh
  export OPENAI_API_BASE=http://127.0.0.1:8931/openai/v1/
  export OPENAI_API_KEY=<DUMMY_KEY_AS_YOU_SET>
  ```

### Default value and effect of `HOST_PORT` setting

- The default value of `HOST_PORT` is `8931`. By setting `HOST_PORT`, you can map any port on the host machine to port `80` of the container. For example, if you set `HOST_PORT=8080`, port `8080` on the host machine will be mapped to port `80` of the container.

## License

This project is licensed under the [MIT License](LICENSE).
