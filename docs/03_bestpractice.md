# Kafka ベストプラクティス

## ZooKeeper ではなく KRaft を使うべし

[./04_kraft](./04_kraft.md) を参照。

## Topic の命名規則

命名規則: `<env>.<domain>.<entity>.<event>`

例:

- `prod.order.payment.completed`
- `dev.user.account.created`
- `staging.inventory.item.updated`

本番環境では、Topic の自動作成機能を無効化する（`auto.create.topics.enable=false`）。

## Partition 数の決め方

- **スループットの観点**
  - `目標スループット ÷ Producer（or Consumer）の単体スループット`
    - 目標スループット: ピーク時に処理したい時間あたりのデータ量
    - 単体スループット: 1インスタンスが Kafka に書き込める（or 読み込める）時間あたりのデータ量。事前に計測が必要。
    - 例: `(100M events/s) ÷ (20M events/s) = 5 partitions`
- **並列処理の観点**
  - 制約: 1つの Partition は同時に 1つの Consumer インスタンスからしか読めない
  - Consumer 1台あたりの処理速度がボトルネックであれば Partition を増やして並列化する
- **注意点**
  - Partition 数は後から増やせるが、同一キーのメッセージの順序保証に影響が出る
  - 将来のピーク時スループットを見越した数を最初から設定しておくのが望ましい

## Replication 数の決め方

データの耐久性と可用性のバランスを考慮する。

| 設定項目 | 推奨値 | 説明 |
| --- | --- | --- |
| `replication.factor` | 3 | レプリカ数。Broker 障害時のデータ消失を防ぐ |
| `min.insync.replicas` | 2 | 書き込みを承認する最小の同期済みレプリカ数 |

`min.insync.replicas` を下回ると書き込みが停止する。`replication.factor - 1` を目安に設定することで、1台の Broker 障害時でも書き込みを継続できる。

## Producer の設定

データの耐久性・順序の整合性・スループットのバランスを調整する。

| 設定項目 | 推奨値 | 説明 |
| --- | --- | --- |
| `acks` | `all`（`-1`） | 全 ISR（In-Sync Replicas）への書き込み完了を確認してから応答。データ消失リスクを最小化 |
| `enable.idempotence` | `true` | Producer の冪等性を有効化。重複送信を防ぐ（`acks=all` と組み合わせて使用） |
| `retries` | 十分大きい値 | 一時的な障害時の再送回数。冪等性が有効な場合は自動的に大きな値が設定される |
| `max.in.flight.requests.per.connection` | `5`（冪等性有効時） | 同時に送信中のリクエスト数の上限。順序保証が必要なら `1` にする |
| `compression.type` | `lz4` or `snappy` | メッセージ圧縮。スループット向上とストレージ削減に有効 |
| `linger.ms` | `5`〜`20` | バッチ送信の待機時間。値を大きくするとスループットが向上するがレイテンシが増加 |
| `batch.size` | `65536`（64KB） | バッチサイズの上限。大きくするとスループットが向上する |

## Consumer の設定

処理の保証レベル・耐障害性・システム全体のパフォーマンスのバランスを調整する。

| 設定項目 | 推奨値 | 説明 |
| --- | --- | --- |
| `enable.auto.commit` | `false` | オフセットの自動コミットを無効化。処理完了後に手動コミットすることで at-least-once を保証する |
| `auto.offset.reset` | `earliest` or `latest` | 初回読み込み時や offset が無効な場合の挙動。`earliest` は先頭から、`latest` は最新から読み込む |
| `partition.assignment.strategy` | `CooperativeStickyAssignor` | リバランス時の Partition 再割り当て戦略。段階的な再割り当てにより処理の停止時間を最小化できる |
| `max.poll.interval.ms` | 処理時間に合わせて設定 | `poll()` 呼び出し間隔の最大値。超過すると Consumer がグループから離脱とみなされリバランスが発生する |
| `session.timeout.ms` | `30000`〜`45000` | Broker が Consumer の死活を判断するタイムアウト。小さいほど障害検知が早いが誤検知が増える |

オフセットのコミットタイミング:

```
1. メッセージを poll() で取得
2. ビジネスロジックを処理
3. 処理成功後に consumer.commit() を呼ぶ
```

## Dead Letter Queue (DLQ)

処理できないメッセージによって Partition 全体の処理が停止することを防ぐ仕組み。

- 一定回数リトライしても処理できないメッセージを専用の DLQ Topic（例: `prod.order.payment.completed.dlq`）に転送する
- DLQ には元のメッセージ本体に加え、エラー理由・発生時刻・元の Topic などのメタ情報をヘッダーに付与する
- DLQ に溜まったメッセージは監視・アラートの対象にし、原因調査後に再処理できるようにする

## Delivery Semantics

| 種類 | 説明 | ユースケース |
| --- | --- | --- |
| At-most-once | 最大1回だけ配信。障害時にメッセージが失われる可能性がある | ログ収集など、多少のデータ欠損が許容されるケース |
| At-least-once | 必ず1回以上配信。障害時に再送されるため重複が発生する可能性がある | 冪等性のある処理（重複しても問題ない処理） |
| Exactly-once | 重複せず、紛失もせず、確実に1回だけ処理されることを保証する | 決済処理など、重複・欠損が許されないケース |

Exactly-once を実現するには、Producer の `enable.idempotence=true` と Kafka Transactions（`transactional.id` の設定）を組み合わせる。Consumer 側でも `isolation.level=read_committed` を設定する必要がある。

## Schema Registry

メッセージのスキーマ（構造定義）を一元管理する仕組み。

- **目的**: Producer と Consumer 間でメッセージフォーマットの互換性を保証する
- **フォーマット**: Avro・Protobuf・JSON Schema などをサポート
- **互換性ポリシー**: スキーマの変更時に後方互換性（`BACKWARD`）・前方互換性（`FORWARD`）・完全互換性（`FULL`）を設定できる
- **運用**: スキーマ変更は Schema Registry 経由で行い、破壊的変更（フィールドの削除など）は互換性チェックで検出する

## 参考リンク

- https://zenn.dev/suwash/articles/kafka_best_practice_20250929
