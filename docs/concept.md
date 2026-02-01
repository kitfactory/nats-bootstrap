# concept.md

## 1. Overview
- What: NATS（JetStream/KV）クラスタを同一手順（対称運用）で構築・起動・変更できるCLI/ライブラリ。
- Why: Day-2運用（join/leave/backup/restore/TLS/サービス化）を型化し、手順差分による事故を減らす。
- Who: 複数ホストでNATSを使う開発者/QA、Windows中心の運用チーム、分散KV運用に疲れている層。
- When/Where: 複数ノードのNATSクラスタを長期運用する現場。
- Outputs: `nats-bootstrap` CLI、ライブラリAPI、運用ドキュメント（status/doctor）。
- Assumptions:
  - NATSクラスタ（JetStream/KV）を使用する。
  - sys.creds は管理端末（controller）にのみ置く。
  - 監査/閉域環境では外部導入の `nats-server` を使うことがある。

## 2. Main Pains
- ノードごとに設定や手順が微妙に違い、運用事故が起きる（非対称運用）。
- ノード追加/離脱が怖い（peer-remove相当の除名が難しい）。
- Windowsサービス化でvenv更新が壊れる。
- 「どのnats-serverを使っているか」が分からずトラブル対応が遅い。

## 3. ターゲットと前提
- ターゲット: 複数ホスト運用の開発/QA/運用チーム。
- 前提: 既存のNATS運用知識とNATS設定ファイルの管理がある。

## 4. 利用方針・非ゴール
- `up` は起動のみ。サービス登録は勝手に行わない。
- `leave`/`restore` など破壊的操作は安全側デフォルト。
- sys.creds をノードに配らない（controller代行）。
- `details/meta` への無制限拡張は許可しない（キー集合を定義）。

## 5. 主要機能（Features）
| ID | 機能 | 解決するPain | 対応UC | 優先度 |
|---|---|---|---|---|
| F-1 | 対称運用CLI（up/join/down/leave） | 手順差分事故 | UC-1, UC-2, UC-3 | P1 |
| F-2 | 5段階のバイナリ解決とバージョン取得 | どのnats-serverか不明 | UC-4 | P0 |
| F-3 | status/doctor の事実表示 | トラブル時の調査コスト | UC-4 | P0 |
| F-4 | controller による leave 代行 | sys.creds配布の禁止 | UC-3 | P1 |
| F-5 | Windowsサービス運用（固定パス） | venv更新で壊れる | UC-6 | P1 |
| F-6 | backup/restore（nats CLI） | 復旧手順の属人化 | UC-5 | P2 |

## 6. ユースケース（Use Cases）
| ID | 主体 | 目的 | 前提 | 主フロー（要約） | 成功条件 | 失敗条件 |
|---|---|---|---|---|---|---|
| UC-1 | 運用担当 | ノード起動/参加 | 設定ファイルがある | `up`/`join` 実行 | NATSが起動する | バイナリ未解決/設定不備 |
| UC-2 | 運用担当 | ノード停止 | ノードが稼働中 | `down` 実行 | プロセス停止 | PID/サービス不明 |
| UC-3 | 運用担当 | ノード除名 | controller が稼働 | `leave` → controller 依頼 | peer-remove完了 | controller不達 |
| UC-4 | 運用担当 | 状況確認 | なし | `status`/`doctor` 実行 | 事実が出る | バイナリ未解決 |
| UC-5 | 運用担当 | バックアップ/復元 | nats CLI利用可 | `backup`/`restore` 実行 | データ移行 | 競合/権限不足 |
| UC-6 | 運用担当 | サービス運用 | Windows環境 | `service install` → `up --service` | 安定起動 | 固定パス未配置 |

## 7. Goals
- G-1: 同一コマンドで全ノード運用できる。
- G-2: sys.creds をノードに配らず leave を完結できる。
- G-3: Windowsサービスでvenv更新の影響を排除する。
- G-4: status/doctor で事実が一発で出る。

## 8. Layering
| レイヤー | 責務 | 主要データ |
|---|---|---|
| CLI/Presentation | 入力I/F・表示 | CLI引数、表示モデル |
| Application | ユースケース実行 | UseCase入力/結果 |
| Domain | ルール（対称運用/解決順） | BinaryResolution、BootstrapConfig |
| Infrastructure | OS/外部ツール | nats-server、nats CLI、OSサービス |

## 9. 主要データ（Key Data Classes / Entities）
| データ | 主属性 | 対応機能 |
|---|---|---|
| BinaryResolution | path, source, version | F-2/F-3 |
| BootstrapConfig | nats_server_path | F-2 |
| ControllerRequest | node_id, request_id | F-4 |
| ServiceInstallSpec | install_dir, service_name | F-5 |
| BackupSpec | streams, output_dir | F-6 |

## 10. 実装優先順位
1. resolve_binary（5段階順）
2. status/doctor（バイナリパス+バージョン）
3. up/start（startは互換警告）
4. Windowsサービス（固定パス）
5. controller + leave
6. backup/restore

## 11. 用語集（Glossary）
- NATS: 軽量メッセージング/ストリーミングサーバ。
- JetStream: NATSのストリーミング機能。
- KV: JetStreamベースのKey-Value。
- controller: sys.creds を保持し peer-remove を代行する管理端末。
- 対称運用: 全ノード同一手順で運用できること。
