# kafka-python-getting-started

Python で Kafka の Producer / Consumer を試すサンプルプロジェクトです。

## 構成

```
.
├── compose.yaml    # Kafka (KRaft モード) を起動する Docker Compose
├── producer.py     # orders トピックへ注文データを送信
├── consumer.py     # orders トピックからメッセージを受信して表示
└── pyproject.toml
```

## 前提条件

- Docker / Docker Compose
- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

## セットアップ

### 1. Kafka を起動する

```bash
docker compose up -d
```

KRaft モードで動作するため ZooKeeper は不要です。起動確認は `healthcheck` が通るまでお待ちください（約 30 秒）。

### 2. 依存パッケージをインストールする

```bash
uv sync
```

## 使い方

### Consumer を起動する（別ターミナルで）

```bash
uv run python consumer.py
```

`orders` トピックを購読し、メッセージが届くと内容を標準出力に表示します。

### Producer を実行する

```bash
uv run python producer.py
```

`orders` トピックへ 10 件の注文データ（`order_id`, `item`, `quantity`, `price`, `timestamp`）を 0.5 秒間隔で送信します。

### 停止する

```bash
docker compose down
```

データを削除したい場合:

```bash
docker compose down -v
```

## トピック設定

| 項目 | 値 |
|------|----|
| トピック名 | `orders` |
| Bootstrap サーバー | `localhost:9092` |
| Consumer グループ ID | `orders-consumer-group` |
