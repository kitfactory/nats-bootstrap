# nats-bootstrap CLI MVP 仕様

## 概要
- 目的: 対称運用を前提に、nats-server バイナリ解決と status/doctor を最短で提供する。
- I/F: CLIのみ（ライブラリは内部利用）。

## 設定ファイル（既定）
- `--config` で指定されたファイルを最優先で使用する。
- `--config` で指定したファイルが存在しない場合はエラーとする。
- それ以外は実行ディレクトリの `nats-config.json` を優先する。
- 見つからない場合は `~/.nats-bootstrap/nats-config.json` を使用する。
- `--config` はサブコマンドの前後いずれでも指定できる。

## bootstrap モード（自動設定生成）
- `--cluster` 指定時は `nats-server` の設定ファイルを自動生成する。
- `--cluster` と `--nats-config` は同時に指定できない。
- `join` で `--cluster` を使う場合は `--seed` が必須。
- `--datafolder` 未指定時の既定: `./nats-bootstrap-data`
- 生成される設定ファイルの保存先: `<datafolder>/nats-bootstrap.conf`
- `jetstream.store_dir` は `<datafolder>` を使用する。
- 生成設定は毎回上書きしてよい（MVP）。
- `--seed` の省略時ポートは `--cluster-port`（既定: 6222）。
- `--listen` は cluster の listen を指定する（`host` または `host:port`）。
- `--cluster-port` は cluster listen の既定ポート（既定: 6222）。
- `--client-port` はクライアント接続ポート（既定: 4222）。
- `--http-port` は監視用 HTTP ポート（既定: 8222）。

## コマンドI/F（MVP）
- `nats-bootstrap up [--service] [--cluster <name>] [--datafolder <path>] [--listen <host[:port]>] [--cluster-port <port>] [--client-port <port>] [--http-port <port>] [--nats-config <path>] [-- <nats args...>]`
- `nats-bootstrap join [--seed <seed>] [--cluster <name>] [--datafolder <path>] [--listen <host[:port]>] [--cluster-port <port>] [--client-port <port>] [--http-port <port>] [--nats-config <path>] [-- <nats args...>]`
- `nats-bootstrap down --confirm`
- `nats-bootstrap leave --controller <url> [--controller <url> ...] [--request-id <id>] [--server-name <name>] [--nats-url <url>] [--stop-anyway] --confirm`
- `nats-bootstrap service install`
- `nats-bootstrap service uninstall`
- `nats-bootstrap controller start --listen <host:port> --nats-url <url> --sys-creds <path> [--state-dir <path>]`
- `nats-bootstrap backup`
- `nats-bootstrap restore`
- `nats-bootstrap status`
- `nats-bootstrap doctor [--service-name <name>]`
- `nats-bootstrap start`（deprecated: `up` に委譲）

## controller 仕様（MVP案）
### CLI
- `nats-bootstrap controller start --listen <host:port> --nats-url <url> --sys-creds <path> [--state-dir <path>]`
  - `--listen` 既定: `127.0.0.1:8222`
  - `--state-dir` 未指定時: `~/.nats-bootstrap/controller`

### HTTP API
- `GET /health`
- `POST /v1/leave`

リクエスト:
```json
{
  "request_id": "uuid-or-unique-string",
  "server_name": "node-1",
  "nats_url": "nats://host:4222"
}
```

レスポンス（成功）:
```json
{
  "request_id": "uuid-or-unique-string",
  "result": "ok"
}
```

レスポンス（冪等）:
```json
{
  "request_id": "uuid-or-unique-string",
  "result": "already_done"
}
```

### 冪等性
- `request_id` をキーに結果を保存し、同一IDは再実行しない。
- 保存先は `--state-dir` 配下の `controller_state.json` とする。

## leave（controller呼び出し）
- `--controller` は複数指定でき、順に試行する。
- controller 不達時は失敗（`--stop-anyway` 指定時は警告で継続）。
- MVPではローカル停止は行わない（controller 呼び出しのみ）。
 - `--confirm` を必須とする。

## down/leave の安全方針
- down は停止のみ（設定変更・除名は行わない）。
- leave は controller による除名が完了してから停止する。
- controller 不達時は停止しない（`--stop-anyway` 指定時のみ停止）。
- 破壊的操作には明示フラグを要求する（`--confirm`）。

## テスト方針（MVP）
- テストは `pytest` を使用する。
- 主要対象: resolve_binary / config / doctor 出力 / CLI 引数位置。
- 外部依存（nats-server 実行）はモック/スタブで代替する。

## Windowsサービス方針（MVP）
- サービス登録は `service install` のみで行い、`up --service` は起動のみ。
- 既定ではコピーせず、解決済みの `nats-server.exe` をそのまま参照する。
- `--bin-dir` 指定時のみ固定パスへコピーし、サービスはそのパスを参照する。
- 固定パス例: `C:\ProgramData\nats-bootstrap\bin\nats-server.exe`
- venv 更新で壊れる可能性があるため、長期運用は固定パス配置を推奨する。
- Windowsサービス操作は管理者権限が必要。

## Windowsサービス I/F（MVP）
- `nats-bootstrap service install --service-name <name> [--bin-dir <path>] [--nats-config <path>]`
- `nats-bootstrap service uninstall --service-name <name>`
- `nats-bootstrap up --service [--service-name <name>]`

### 既定値
- `service-name` 既定: `nats-bootstrap`

## backup/restore（MVP）
### 前提
- `nats` CLI が必要（`--nats-cli-path` → `NATS_CLI_PATH` → PATH）。

### CLI
- `nats-bootstrap backup --stream <name> --output <dir> [--nats-url <url>] [--creds <path>] [--context <ctx>] [--nats-cli-path <path>]`
- `nats-bootstrap restore --input <dir> --confirm [--nats-url <url>] [--creds <path>] [--context <ctx>] [--nats-cli-path <path>]`

### 仕様
- backup は `nats stream backup <stream> <dir>` を実行する。
- restore は `nats stream restore <dir>` を実行する。
- restore は `--confirm` 必須（安全側）。

### 固定パス配置
- 既定の bin ディレクトリは `C:\ProgramData\nats-bootstrap\bin`
- `--bin-dir` 指定時はその配下に `nats-server.exe` を配置する
- 既存ファイルがある場合は上書きする（MVPは警告のみ）

## down（停止）
- 停止対象は PID ファイル（`nats-server.pid`）がある場合はそれを優先する。
- PID がない場合は実装保留（MVPでは停止できない）。

## leave（除名 + 停止）
- controller 呼び出し後、`--confirm` 指定時に停止する。
- 停止は down と同じ方法で実行する。

## バイナリ解決順（必須）
1. CLI `--nats-server-path`
2. 設定ファイル `nats_server_path`
3. 環境変数 `NATS_SERVER_PATH`（互換で `NATS_SERVER_BIN`）
4. `nats-server-bin`（extras: `server`）
5. PATH 上の `nats-server`

## 要件一覧（Requirements）
| ID | 要件 | UC-ID |
|---|---|---|
| REQ-0001 | CLIのコマンド体系を提供する | UC-1, UC-2, UC-3, UC-4, UC-5, UC-6 |
| REQ-0002 | resolve_binary は5段階解決順で絶対パスを返す | UC-4 |
| REQ-0003 | resolve_binary は可能な限り `nats-server -v` を取得する | UC-4 |
| REQ-0004 | status はバイナリパス/バージョン/解決経路を表示する | UC-4 |
| REQ-0005 | doctor は優先順と解決経路の試行履歴を表示する | UC-4 |
| REQ-0006 | config は既知キーのみ許可し未知キーを拒否する | UC-4 |
| REQ-0009 | `--config` 指定時、ファイルが存在しない場合はエラーとする | UC-4 |
| REQ-0007 | start は up に委譲し警告を出す | UC-1 |
| REQ-0008 | MVP未実装コマンドは明示的なエラーで終了する | UC-2, UC-3, UC-5, UC-6 |
| REQ-0100 | controller start はHTTPサーバを起動し、/v1/leave を提供する | UC-3 |
| REQ-0101 | /v1/leave は request_id の冪等性を保証する | UC-3 |
| REQ-0102 | leave は controller へリクエストを送信し結果を表示する | UC-3 |
| REQ-0103 | doctor は controller の疎通チェックを表示できる | UC-4 |
| REQ-0200 | down は `--confirm` 指定時のみ停止する | UC-2 |
| REQ-0201 | leave は `--confirm` 指定時のみ停止に進む | UC-3 |
| REQ-0202 | down は pid ファイル未検出時に失敗する | UC-2 |
| REQ-0300 | service install はWindowsサービスを登録する | UC-6 |
| REQ-0301 | service uninstall はWindowsサービスを削除する | UC-6 |
| REQ-0302 | up --service はサービスを起動する | UC-6 |
| REQ-0303 | doctor --service-name はサービス状態を表示する | UC-4 |
| REQ-0400 | backup は nats CLI で stream backup を実行する | UC-5 |
| REQ-0401 | restore は nats CLI で stream restore を実行する | UC-5 |
| REQ-0402 | doctor は nats CLI の有無を表示する | UC-4 |
| REQ-0500 | `--cluster` 指定時は自動設定を生成して起動する | UC-1 |
| REQ-0501 | `--cluster` と `--nats-config` は同時指定不可 | UC-1 |
| REQ-0502 | `join` で `--cluster` を使う場合は `--seed` 必須 | UC-1 |
| REQ-0503 | `--datafolder` 未指定時は `./nats-bootstrap-data` を使用する | UC-1 |
| REQ-0504 | 生成設定の保存先/`jetstream.store_dir` は `<datafolder>` | UC-1 |
| REQ-0505 | `--seed` の省略時ポートは `--cluster-port` を使う | UC-1 |
| REQ-0506 | `--listen`/`--cluster-port`/`--client-port`/`--http-port` を設定に反映する | UC-1 |

### [REQ-0001] CLIのコマンド体系を提供する
Given: `nats-bootstrap --help` が実行された状態
When: ヘルプを表示する
Done: 仕様のコマンド体系が表示される
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-CORE-0003 | 未実装コマンド実行 | MSG-CORE-0003 |

### [REQ-0002] resolve_binary は5段階解決順で絶対パスを返す
Given: 解決候補が複数ある状態
When: resolve_binary を実行する
Done: 優先順に従い最初に見つかった候補の絶対パスを返す
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-CORE-0001 | バイナリが見つからない | MSG-CORE-0001 |

### [REQ-0003] resolve_binary は可能な限り `nats-server -v` を取得する
Given: バイナリが解決されている状態
When: resolve_binary を実行する
Done: `-v` 実行が成功すればバージョンを保持する
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-CORE-0004 | バージョン取得失敗 | MSG-CORE-0004 |

### [REQ-0004] status はバイナリパス/バージョン/解決経路を表示する
Given: status を実行した状態
When: バイナリが解決される
Done: パス・バージョン・解決経路を表示する
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-CORE-0001 | バイナリが見つからない | MSG-CORE-0001 |
| ERR-CORE-0002 | 設定ファイル不正 | MSG-CORE-0002 |

### [REQ-0005] doctor は優先順と解決経路の試行履歴を表示する
Given: doctor を実行した状態
When: 解決が成功または失敗する
Done: 優先順と、どの段で決まったか/失敗理由を表示する
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-CORE-0002 | 設定ファイル不正 | MSG-CORE-0002 |

### [REQ-0006] config は既知キーのみ許可し未知キーを拒否する
Given: config を読み込む
When: 未知キーが存在する
Done: 失敗として ERR-CORE-0002 を返す

### [REQ-0009] `--config` 指定時、ファイルが存在しない場合はエラーとする
Given: `--config` が指定されている
When: 指定されたファイルが存在しない
Done: 失敗として ERR-CORE-0002 を返す

### [REQ-0007] start は up に委譲し警告を出す
Given: start を実行する
When: 内部で up を実行する
Done: 警告を表示し、up 相当の処理に移譲する

### [REQ-0008] MVP未実装コマンドは明示的なエラーで終了する
Given: 未実装コマンドを実行する
When: 実装未完了
Done: ERR-CORE-0003 を返し、安全に終了する

### [REQ-0100] controller start はHTTPサーバを起動し、/v1/leave を提供する
Given: `controller start` が実行される
When: 指定された listen でHTTPサーバを起動する
Done: `/v1/leave` が利用可能になる

### [REQ-0101] /v1/leave は request_id の冪等性を保証する
Given: 同一の request_id が複数回送信される
When: 最初の処理が完了している
Done: 2回目以降は `result: already_done` を返す

### [REQ-0102] leave は controller へリクエストを送信し結果を表示する
Given: `leave` が実行される
When: controller が応答する
Done: `ok` / `already_done` を表示する

### [REQ-0103] doctor は controller の疎通チェックを表示できる
Given: `doctor --controller <url>` が指定される
When: controller が応答する
Done: `ok` / `ng` を表示する

### [REQ-0200] down は `--confirm` 指定時のみ停止する
Given: `down` が実行される
When: `--confirm` が指定されていない
Done: ERR-CORE-0005 を返す

### [REQ-0201] leave は `--confirm` 指定時のみ停止に進む
Given: `leave` が実行される
When: `--confirm` が指定されていない
Done: ERR-CORE-0005 を返す

### [REQ-0202] down は pid ファイル未検出時に失敗する
Given: `down` が実行される
When: `nats-server.pid` が存在しない
Done: ERR-CORE-0001 を返す

### [REQ-0300] service install はWindowsサービスを登録する
Given: `service install` が実行される
When: 必要な権限がある
Done: サービスが登録される

### [REQ-0301] service uninstall はWindowsサービスを削除する
Given: `service uninstall` が実行される
When: サービスが存在する
Done: サービスが削除される

### [REQ-0302] up --service はサービスを起動する
Given: `up --service` が実行される
When: サービスが登録済みである
Done: サービスが起動される

### [REQ-0303] doctor --service-name はサービス状態を表示する
Given: `doctor --service-name <name>` が指定される
When: サービスが存在する
Done: 状態（RUNNING/STOPPED 等）を表示する

### [REQ-0400] backup は nats CLI で stream backup を実行する
Given: `backup` が実行される
When: nats CLI が利用可能
Done: `nats stream backup` が実行される

### [REQ-0401] restore は nats CLI で stream restore を実行する
Given: `restore` が実行される
When: nats CLI が利用可能、`--confirm` が指定される
Done: `nats stream restore` が実行される

### [REQ-0402] doctor は nats CLI の有無を表示する
Given: `doctor` が実行される
When: nats CLI が存在する/しない
Done: `nats-cli: <path>` または `nats-cli: not found` を表示する

### [REQ-0500] `--cluster` 指定時は自動設定を生成して起動する
Given: `up` または `join` が実行される
When: `--cluster` が指定され、`--nats-config` が指定されていない
Done: 自動生成された設定ファイルを `-c` で指定して起動する
#### エラー
| ERR-ID | 事象 | MSG-ID |
|---|---|---|
| ERR-BOOT-0003 | 生成対象のディレクトリが不正 | MSG-BOOT-0003 |
| ERR-BOOT-0004 | cluster 名が空 | MSG-BOOT-0004 |

### [REQ-0501] `--cluster` と `--nats-config` は同時指定不可
Given: `up` または `join` が実行される
When: `--cluster` と `--nats-config` が同時に指定される
Done: ERR-BOOT-0001 を返す

### [REQ-0502] `join` で `--cluster` を使う場合は `--seed` 必須
Given: `join` が実行される
When: `--cluster` が指定され、`--seed` が未指定
Done: ERR-BOOT-0002 を返す

### [REQ-0503] `--datafolder` 未指定時は `./nats-bootstrap-data` を使用する
Given: `--cluster` が指定される
When: `--datafolder` が未指定
Done: 既定パスとして `./nats-bootstrap-data` を使用する

### [REQ-0504] 生成設定の保存先/`jetstream.store_dir` は `<datafolder>`
Given: `--cluster` が指定される
When: 自動設定を生成する
Done: 設定ファイルは `<datafolder>/nats-bootstrap.conf` に保存し、`jetstream.store_dir` は `<datafolder>` を使用する

### [REQ-0505] `--seed` の省略時ポートは `--cluster-port` を使う
Given: `join` が実行される
When: `--seed` が `host` のみで指定される
Done: `--cluster-port`（既定: 6222）を補って `nats://<host>:<port>` を生成する

### [REQ-0506] `--listen`/`--cluster-port`/`--client-port`/`--http-port` を設定に反映する
Given: `--cluster` が指定される
When: 各オプションが指定される
Done: 生成設定に `cluster.listen` / `port` / `http` を反映する

## MSG-ID 一覧
| ID | メッセージ | 対応REQ/ERR |
|---|---|---|
| MSG-CORE-0001 | nats-server が見つかりません | ERR-CORE-0001 |
| MSG-CORE-0002 | 設定ファイルが不正です | ERR-CORE-0002 |
| MSG-CORE-0003 | このコマンドはMVPでは未実装です | ERR-CORE-0003 |
| MSG-CORE-0004 | バージョン取得に失敗しました（継続） | ERR-CORE-0004 |
| MSG-CORE-0005 | `--confirm` が必要です | ERR-CORE-0005 |
| MSG-CTRL-0001 | controller への接続に失敗しました | ERR-CTRL-0001 |
| MSG-CTRL-0002 | controller リクエストが不正です | ERR-CTRL-0002 |
| MSG-SVC-0001 | Windows 以外では service をサポートしません | ERR-SVC-0001 |
| MSG-SVC-0002 | service が既に存在します | ERR-SVC-0002 |
| MSG-SVC-0003 | service が見つかりません | ERR-SVC-0003 |
| MSG-BKP-0001 | nats CLI が見つかりません | ERR-BKP-0001 |
| MSG-BOOT-0001 | `--cluster` と `--nats-config` は同時に指定できません | ERR-BOOT-0001 |
| MSG-BOOT-0002 | `join` で `--cluster` を使う場合は `--seed` が必要です | ERR-BOOT-0002 |
| MSG-BOOT-0003 | `--datafolder` はディレクトリを指定してください | ERR-BOOT-0003 |
| MSG-BOOT-0004 | `--cluster` は空にできません | ERR-BOOT-0004 |

## ERR-ID 一覧
| ID | 種別 | 説明 |
|---|---|---|
| ERR-CORE-0001 | NotFound | バイナリ解決失敗 |
| ERR-CORE-0002 | InvalidConfig | config の構造/型が不正 |
| ERR-CORE-0003 | NotImplemented | MVP未実装 |
| ERR-CORE-0004 | VersionCheck | `nats-server -v` が失敗（警告扱い） |
| ERR-CORE-0005 | ConfirmationRequired | `--confirm` が必要 |
| ERR-CTRL-0001 | ControllerUnavailable | controller に接続できない |
| ERR-CTRL-0002 | InvalidRequest | controller リクエストが不正 |
| ERR-SVC-0001 | UnsupportedPlatform | Windows 以外 |
| ERR-SVC-0002 | ServiceAlreadyExists | service が既に存在 |
| ERR-SVC-0003 | ServiceNotFound | service が見つからない |
| ERR-BKP-0001 | NatsCliNotFound | nats CLI が見つからない |
| ERR-BOOT-0001 | InvalidArgs | `--cluster` と `--nats-config` の同時指定 |
| ERR-BOOT-0002 | SeedRequired | `join` + `--cluster` 時の `--seed` 不足 |
| ERR-BOOT-0003 | InvalidDataFolder | `--datafolder` がディレクトリではない |
| ERR-BOOT-0004 | ClusterRequired | `--cluster` が空 |
