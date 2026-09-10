# BlobHell-AIBench v0.1 仕様

## 目的と不変条件

本ベンチマークは、エージェントが実環境の観測だけを根拠に長時間の低レイヤ障害解析と修復を遂行できるかを測る。文章回答やパッチの見た目は合否根拠にならない。人間は技術的に介入せず、ハードウェアから独立収集した証拠を Judge が評価する。

```text
Task → Agent → Tool Gateway → Isolated Workspace → Device
                                              ↓
                                     Evidence Collector
                                              ↓
                                     Independent Judge → Result
```

## ライフサイクル

Runner は task を schema 検証し、公開情報だけを TaskContext として Agent に渡す。Agent は `start`、0 回以上の `step`、`finalize` を通る。各 action は Gateway が許可した tool または終了のみである。上限ターン、タイムアウト、例外は失敗終了になる。

Tool request は要求イベント、開始イベント、完了イベントの順で記録する。実行 cwd は workspace 配下に解決し、環境変数は allowlist のみ継承する。stdout/stderr の完全版は artifact に保存し、Agent には安全 redaction 後の内容を返す。コンソール表示だけを短縮しても transcript/observation を暗黙に改変してはならない。

Observation は tool の終了コード、標準出力、標準エラー、timeout、所要時間を含む。秘密値は明示設定した文字列だけを `[REDACTED]` に置換し、その事実を記録する。

Agent の `finish`、ターン上限、例外、運用停止で Agent phase は終わる。`finish` の自己申告結果は採点に使用しない。その後 Judge が agent workspace と分離された設定および evidence manifest を読む。

## 採点

Judge は宣言的 check を順に評価する。v0.1 は artifact の存在、JSON 値、正規表現、手動観測記録、および明示的な mock evaluator を扱う。各 check は automatic / semi-automatic / future に分類する。required な未実装、証拠欠落、失敗は全体 FAIL である。Agent message は evidence source として禁止する。

## 妥当性

技術的 human hint が 1 件でもあれば scored run は無効であり PASS にしない。物理操作と直接観測のみ許容し、構造化イベントへ記録する。hidden judge、reference patch、private metadata を Agent に公開してはならない。公開済み解答を含む task は contamination status を明示し leaderboard 対象外とする。

run failure、tool timeout、device loss、Agent 例外も transcript と `run_failed` に残す。結果が生成できる場合は FAIL と failure reason を保存し、生成不能時も manifest と transcript を保持する。

## 再現性

run id、task/version、設定 snapshot、時刻、adapter/model、tool 呼出し、完全 command log、evidence、judge version/check を保存する。外部 source tree、device build、fixture、入力 media は再配布可能性と hash を task 側で指定する。再現性 check を満たすには独立した再試行証拠が必要である。

v0.1 の subprocess 制限は防御層であり完全 sandbox ではない。scored deployment は container/VM、network policy、read-only judge volume、専用 USB device policy を追加すること。

