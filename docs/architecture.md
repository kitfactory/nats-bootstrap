# architecture.md

## 1. 目的 / 範囲
nats-bootstrap のCLIと controller を中心に、運用の対称性・安全性・冪等性を担保するための構成を定義する。
MVPでは controller の最小I/F（leave代行）と、バイナリ解決・status/doctor の動作が対象。

## 2. レイヤ構成
```
CLI (Presentation)
  -> UseCase (Application)
    -> Domain (Rules/Policy)
      -> Infra (OS/HTTP/External)
```
- CLI: 引数・入出力、エラー表示
- UseCase: コマンド毎の手続き（status/doctor/leave等）
- Domain: 解決順・安全デフォルト・冪等性方針
- Infra: nats-server 実行、HTTPサーバ、ファイルI/O

## 3. 主要コンポーネント
### 3.1 CLI
- `nats-bootstrap` のコマンドを提供
- `--config` はサブコマンドの前後どちらでも受け付ける
- `start` は `up` へ委譲（互換警告）

### 3.2 Binary Resolver
- 解決順: CLI -> config -> env -> nats-server-bin -> PATH
- 返却値: 絶対パス + version（取得できる場合）
- doctor で解決経路と優先順を表示

### 3.3 Controller
- 役割: sys.creds を保持し、leave の peer-remove を代行
- HTTPサーバとして起動し、`/v1/leave` を提供

## 4. Controller 設計メモ（MVP）
### 4.1 I/F
- 起動: `controller start --listen <host:port> --nats-url <url> --sys-creds <path> [--state-dir <path>]`
- API: `POST /v1/leave`
  - `GET /health`

### 4.2 データ
- request_id をキーに、処理結果を `controller_state.json` に保存
- 保存場所は `--state-dir` 指定（未指定の既定は `~/.nats-bootstrap/controller`）

### 4.3 冪等性
- 同一 request_id への再要求は再実行せず `already_done` を返す
- 単一プロセス運用を前提（同時書き込みは最小）

### 4.4 依存
- controller は sys.creds をローカルに保持
- ノード側は controller へ leave を依頼（sys.creds 非配布）
- MVPでは NATS peer-remove の実行は今後追加（HTTP/I/Fの骨組み優先）

## 5. エラー方針
- ERR/MSG は `docs/spec.md` の ID に従う
- controller 接続失敗は ERR-CTRL-0001
- 不正リクエストは ERR-CTRL-0002

## 6. セキュリティ（MVP前提）
- controller は管理ネットワーク内で運用する前提
- 認証/認可は将来拡張で追加（MVPでは対象外）
