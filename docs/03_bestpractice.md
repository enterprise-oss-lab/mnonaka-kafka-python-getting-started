# Kafka ベストプラクティス

## ZooKeeper ではなく KRaft を使うべし

[./04_kraft](./04_kraft.md) を参照。

## Topic の命名規則

命名規則: `<env>.<domain>.<entity>.<event>`

例:

- `prod.order.payment.completed`
- `dev.user.account.created`
- `staging.inventory.item.updated`

本番環境では、Topic の自動作成機能を無効化する(`auto.create.topics.enable=false`)。

## Partition 数の決め方

- スループットの観点
  - 目標スループット / Producer (or Consumer) のスループット
    - 目標スループットはアクセス数のピーク時に処理したい時間あたりのデータ量
    - Producer のスループットは、1インスタンスが Kafka に書き込める (or から読み込める) 時間あたりのデータ量。これは事前に計測する必要がある。
    - e.g. (100 M events / s) / (20 M events) = 5 partitions
- 並列処理の観点
  - 重大な制約: 1つの Partition は 同時に1つの Consumer からしか読めない
  - Consumer 1台あたりの処理速度がボトルネックなら Partition を増やして並列化
- Partition の数は増やせるが、同一キーの message の順序保証に影響が出る
  - →あらかじめ将来のピーク時のスループットを処理できる数に最初からしておくのが良い

## Replication 数の決め方

データの耐久性と可用性のバランスを見る。

Replication の数 (`Replication.factor`)と、最新状態と同期が取れている最小の数 (`min.insys.replicas`) を設定する。
`min.insys.replicas` を下回ると書き込みが停止する。

## Producer の設定

データの耐久性、順序の整合性、スループットのバランスを見る。

## Consumer の設定

処理の保証レベル、耐障害性、システム全体のパフォーマンスのバランスを見る。

`enable.auto.commit` を `false` にし、アプリケーションのロジック内で手動でコミットする。

`partition.assignment.strategy` に `CooperativeStickyAssignor` を使用することで、 Consumer のリバランスの影響が最小限に抑えられ、処理の停止時間が短縮される。

## Dead Letter Queue

処理できないメッセージによって Partition 全体の処理が停止することを防ぐ。

## Delivery Semantics

| 種類 | 説明 | ユースケース |
| ------------- | -------------- | -------------- |
| At-most-once | 最大1回だけ配信される。障害時にメッセージが失われる可能性がある。 | ログ収集など、多少のデータ欠損が許容されるケース |
| At-least-once | 必ず1回以上配信される。障害時に再送されるため重複が発生する可能性がある。 | 冪等性のある処理（重複しても問題ない処理） |
| Exactly-once | 重複せず、紛失もせず、確実に1回だけ処理されることを保証する。 | 決済処理など、重複・欠損が許されないケース |

## Schema-registry

メッセージの構造定義する。


## 参考リンク

以下のリンク先を参考にさせていただいた。

- https://zenn.dev/suwash/articles/kafka_best_practice_20250929
