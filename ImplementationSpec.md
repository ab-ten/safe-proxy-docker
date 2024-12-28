# openai-safe-proxy-docker

## 概要

このプロジェクトは、`config.yaml`の設定を基に、複数のAPIサーバーにプロキシーを設定するDockerコンテナを構築することを目的とします。クライアントのダミーキーをリアルキーに置換し、セキュアな接続を実現します。

## config.yaml のデータ構造

config.yaml は以下のデータ構造を持ちます：

```yaml
servers:
  server_name_1:
    origin: "https://api.server1.com/"
    authentication:
      type: "Bearer"
      keys:
        "dummy-key-1": "real-api-key-1-encrypted"
        "dummy-key-2": "real-api-key-2-encrypted"
  server_name_2:
    origin: "http://api.server2.local/"
    authentication:
      type: "Bearer"
      keys:
        "dummy-key-A": "real-api-key-A-encrypted"
        "dummy-key-B": "real-api-key-B-encrypted"
```

- servers:
  - 複数のプロキシ対象サーバーを定義。
- origin:
  - プロキシ先のAPIサーバーのURL。
- authentication:
  - 認証方式とダミーキーからリアルキーへのマッピング。
- keys:
  - クライアントから渡されるダミーAPIキーと、それに対応するリアルAPIキーのペア。

## 実現したいこと

config.yaml 記述された設定を元に、Nginxで以下を実現する：

### プロキシ設定:

/server_name_1/ や /server_name_2/ にリクエストが来た場合、それぞれの origin に基づきプロキシ処理を行う。

### 認証ヘッダの変換:

クライアントから Authorization: Bearer <dummy-key> というヘッダでリクエストが来た場合に、その dummy-key を対応する real-api-key に置き換える。

### 認証方式のサポート:

authentication / type が Bearer の場合のみ対応し、それ以外はエラーとする。

### セキュリティ確保:

real-api-key は config.yaml には暗号化された形式で保存し、復号して使用する。

## 要求仕様

### 起動処理

Dockerfile の起動シェルスクリプトから呼び出され、以下の処理を行う

+ 秘密鍵ファイルが存在しない場合はランダムなバイト列を生成し、秘密鍵ファイルに保存する
+ config.yaml を読み込み、エラーチェックを行う
  - 必須項目が記述されているか
  - authentication / type が対応しているもの（現在は Bearer のみ）か
  - keys にダミーキーとリアルキーのペアが記述されているか
+ config.yaml の内容をデータベースに変換する
  - KEY_MAPPING テーブル
    - server_name, client-dummy-key, plain-real-api-key の3つのカラムを持つ。3つセットで unique
    - データベースに store する際は real api key は平文に復号する
  - ORIGIN テーブル
    - server_name, origin の2つのカラムを持つ
    - server_name は unique
+ nginx を lua module を有効化した状態で起動する
  - nginx 起動前の処理でエラーがあった場合はエラーメッセージを出力して終了する

### リクエストの処理フロー

+ リクエスト受信:
  - クライアントが Authorization: Bearer <dummy-key> を含むリクエストを送信。
+ リクエストURLから server_name を取得:
  - リクエストURLのパスから server_name を取得し、ORIGIN テーブルから origin を取得する。
  - server_name が未定義の場合は HTTP 401 Unauthorized を返す。
+ 認証ヘッダの検証と変換:
  - リクエスト内のダミーAPIキーを、データに基づいて対応するリアルAPIキーに置き換える。
  - リクエスト内にダミーAPIキーが含まれていない場合は HTTP 401 Unauthorized を返す。
  - リクエストのAPIキーがデータベースに存在しない場合は HTTP 401 Unauthorized を返す。
+ プロキシ処理:
  - プロキシ先のorigin にリクエストを転送し、レスポンスをクライアントに返却。

### パフォーマンス要件

- proxy 処理は nginx 内で処理が完結することが望ましい。

### セキュリティ要件

- real-api-key は暗号化された形式で config.yaml に記述されているが、lua での復号処理は外部ライブラリなどが必要なので避け、Dockerコンテナ起動時に復号して tmpfs に作成した sqlite データベースに平文で保存する
  - python 等書きやすい言語で復号処理と sqlite への書き込みを行う
  - server, client-dummy-key, plain-real-api-key の3つのカラムを持つテーブルになる
- 暗号化と復号処理の秘密鍵は docker volume 内に保存し、コンテナ外からアクセスできないようにする。起動時に秘密鍵が存在しない場合はランダムなバイト列として生成する。

### ユーティリティ

- 秘密鍵ファイルに基づいてAPIキーの暗号化を行うユーティリティ encrypt_key コマンドを提供する。
  - encrypt_key <plain-api-key> で暗号化されたAPIキーを標準出力に出力する。
  - 秘密鍵ファイルが存在しない場合はランダムバイト列で作成する。
  - 暗号化・復号処理には fernet を使用する。

### その他

- config.yaml を sqlite database に変換するスクリプトは python 3.12 で記述する。
- nginx lua module を使用するが、openresty は使用せずに済むなら使用しない。
- 以下のファイルパスはデフォルトが存在するが、環境変数で変更できるようにする。
  - config.yaml: CONFIG_FILE=/app/config.yaml
  - sqlite データベース: PROXY_DB_FILE=/tmpfs/proxy.sqlite (Dockerにtmpfsをマウントする)
  - 秘密鍵: SECRET_FILE=/docker-volume/secret.key (docker volume)
- docker container でのマウントポイントは以下の通り
  - /app: ホストのプロジェクトトップディレクトリ
  - /tmpfs: tmpfs マウントポイント
  - /docker-volume: docker volume マウントポイント

## VERSION ファイルについて

プロジェクトには `VERSION` ファイルが含まれており、現在のバージョン番号が記載されています。

### VERSION ファイルの構造

`VERSION` ファイルは以下のような構造を持ちます：

```
0.1.0
# This file contains the version number of the project.
# The first line represents the current version.
# Subsequent lines are comments explaining the purpose of the file.
```

- 最初の行には現在のバージョン番号が記載されています。
- 2行目以降には、ファイルの目的を説明するコメントが記載されています。

### VERSION ファイルの使用方法

- コンテナ起動時に `VERSION` ファイルの内容が読み込まれ、バージョン情報が表示されます。
- `entrypoint.sh` スクリプト内で `VERSION` ファイルの内容が読み込まれ、コンテナ起動時にバージョン情報が表示されます。
