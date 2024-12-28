# safe-proxy-docker

[English README](README-en.md)

## 目的

このプロジェクトの主な目的は、Dockerを使用して複数のAPIサーバーのためのセキュアなリバースプロキシを作成することです。プロキシはクライアントのダミーキーをリアルAPIキーに置き換えて、セキュアな接続を確保します。このプロジェクトには、設定のセットアップ、APIキーの暗号化、Nginxを使用したプロキシ処理が含まれます。

## 機能の紹介

このプロジェクトの主な機能は以下の通りです：

- **セキュアなリバースプロキシ**：Dockerを使用して複数のAPIサーバーのためのセキュアなリバースプロキシを作成し、クライアントのダミーキーをリアルAPIキーに置き換えてセキュアな接続を確保します。
- **設定ベースのセットアップ**：プロキシは`config.yaml`ファイルを使用して設定され、APIエンドポイントや認証の詳細を定義します。
- **APIキーの暗号化**：リアルAPIキーは暗号化されて`config.yaml`ファイルに保存されます。プロジェクトはAPIキーの暗号化と環境のセットアップのためのユーティリティを提供します。
- **NginxとLuaモジュール**：プロジェクトはNginxとLuaモジュールを使用してプロキシリクエストと認証を処理し、効率的でセキュアなリクエスト処理を実現します。
- **SQLiteデータベース**：`config.yaml`の設定はSQLiteデータベースに変換され、ランタイム中の効率的なアクセスを実現します。
- **Docker統合**：プロジェクトはDockerコンテナ内で実行されるように設計されており、Docker環境のセットアップに関する具体的な指示が含まれています。
- **環境変数**：プロジェクトは環境変数を使用してファイルパスやその他の設定をカスタマイズでき、デプロイの柔軟性を提供します。
- **APIキーと設定のセキュアな取り扱い**：プロジェクトはDockerコンテナ内でAPIキーと設定をセキュアに取り扱い、暗号化されたキーをランタイム中に復号して一時的なSQLiteデータベースに保存します。
- **キー管理のためのユーティリティ**：プロジェクトには`encrypt_key.py`のようなAPIキーの暗号化と環境のセットアップのためのユーティリティが含まれており、APIキーをセキュアに管理しやすくします。

## 使い方

### セットアップ

1. Dockerがシステムにインストールされ、実行されていることを確認します。
2. 次のコマンドを実行して、`safe_proxy_docker`という名前のDockerネットワークを作成します：
   ```sh
   docker network create safe_proxy_docker
   ```
3. `docker compose build`を実行してプロジェクトをビルドします：
   ```sh
   docker compose build
   ```
4. 暗号化したいリアルAPIキーを準備します。
5. `encrypt_key.py`スクリプトを使用してリアルAPIキーを暗号化します。次のコマンドを実行します：
   ```sh
   docker compose run --rm --entrypoint /usr/local/bin/encrypt_key.py api_proxy YOUR_API_KEY
   ```
   `YOUR_API_KEY`を実際のAPIキーに置き換えます。このコマンドは暗号化されたAPIキーを出力します。
6. 暗号化されたAPIキーをコピーし、`config.yaml`ファイルに更新します。`config.yaml.sample`を参考にします。例えば：
   ```yaml
   servers:
     openai:
       origin: "https://api.openai.com/"
       authentication:
         type: "Bearer"
         keys:
           "sk-proj-1": "ENCRYPTED_API_KEY"
   ```
   `ENCRYPTED_API_KEY`を前のステップで取得した暗号化キーに置き換えます。
7. 更新された`config.yaml`ファイルをプロジェクトのルートディレクトリに保存します。
8. `.env.sample`ファイルを`.env`ファイルにコピーし、必要に応じて編集します。例えば、ホストマシンのポートを変更する場合は、`HOST_PORT`を設定します。
   ```sh
   cp .env.sample .env
   ```
   デフォルトのまま使用する場合は、`.env`ファイルを作成、編集する必要はありません。

### `docker compose`コマンドの使用

- `docker compose up -d`もしくは`docker compose up`で`safe-proxy-docker`を起動します。セットアップ完了後は、`docker compose up [-d]`のみで起動できます。

### 更新手順

- プロジェクトを更新するには、次のコマンドを実行します：
  ```sh
  git pull
  docker compose build
  ```

### `config.yaml`を変更した場合の手順

- `config.yaml`を変更した場合、Dockerコンテナを再起動する必要があります。次のコマンドを実行します：
  ```sh
  docker compose down
  docker compose up -d
  ```

### 他のDockerコンテナからの使い方

- `safe_proxy_docker`ネットワークを使用する設定を追加します。
- OpenAIのモジュール/ライブラリを使用しているプログラムの場合は次の環境変数を設定します：
  ```sh
  export OPENAI_API_BASE=http://api_proxy/openai/v1/
  export OPENAI_API_KEY=<DUMMY_KEY_AS_YOU_SET>
  ```
- `docker compose up -d`もしくは`docker compose up`で`safe-proxy-docker`を起動しておきます。

### ホスト環境からの使い方

- コンテナの場合と同様に次の環境変数を設定します：
  ```sh
  export OPENAI_API_BASE=http://127.0.0.1:8931/openai/v1/
  export OPENAI_API_KEY=<DUMMY_KEY_AS_YOU_SET>
  ```

### `HOST_PORT`のデフォルト値と設定の効果

- `HOST_PORT`のデフォルト値は`8931`です。`HOST_PORT`を設定することで、ホストマシンの任意のポートをコンテナのポート`80`にマッピングできます。例えば、`HOST_PORT=8080`と設定すると、ホストマシンのポート`8080`がコンテナのポート`80`にマッピングされます。

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下でライセンスされています。
