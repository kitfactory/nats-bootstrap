# nats-bootstrap 🌟

**設定ファイルいらずでクラスタ構築。**  
最初の1台→追加は `--seed` でOK。どの端末でも同じ操作でクラスタが組めます。

NATS（JetStream/KV）クラスタを**どの端末でも同じコマンドで作れる**CLI/ライブラリです。
「起動する」よりも**Day-2運用（join/leave/backup/restore/サービス化）を型にする**ことに価値があります。

English README: `README.md`

---

## これは何？
- **同じコマンド**で、どの端末でもクラスタを作れます。
- `status` / `doctor` で「今の事実」がすぐ見えます。
- Windowsサービス化で、venv更新による破壊を防げます（固定パス運用）。
- **bootstrap モード**: `--cluster` + `--seed` で、設定ファイル不要のクラスタ構築。

## インストール
```powershell
uv pip install nats-bootstrap
```

`nats-server` を同梱したい場合:
```powershell
uv pip install "nats-bootstrap[server]"
```

※ backup/restore には `nats` CLI が必要です。
インストール方法: `docs/nats_cli_install.md`
※ `nats.exe`（CLI）はサーバーではありません。サーバーは `nats-server.exe` です。

## 設定ファイル（優先順）
1. `--config` で指定されたファイル（最優先）
2. 実行ディレクトリの `nats-config.json`
3. `~/.nats-bootstrap/nats-config.json`

例:
```json
{
  "nats_server_path": "C:\\nats\\nats-server.exe"
}
```

## 使い方（MVP）
```powershell
nats-bootstrap status
nats-bootstrap doctor
nats-bootstrap up --cluster demo
nats-bootstrap join --cluster demo --seed pc-a:6222
nats-bootstrap start  # 非推奨（内部で up に委譲）
```

## バイナリ解決順
1. CLI `--nats-server-path`
2. 設定ファイル `nats_server_path`
3. 環境変数 `NATS_SERVER_PATH`（互換で `NATS_SERVER_BIN`）
4. `nats-server-bin`（extras: `server`）
5. PATH 上の `nats-server`

## bootstrap モード（設定ファイル不要）
`--cluster` 指定で設定ファイルを自動生成します。

```powershell
nats-bootstrap up --cluster demo --datafolder C:\nats\data
nats-bootstrap join --cluster demo --seed pc-a:6222 --datafolder C:\nats\data
```

- `--datafolder` 既定: `.\nats-bootstrap-data`
- 生成設定: `<datafolder>\nats-bootstrap.conf`
- 手動設定したい場合は `--nats-config` を使います（`--cluster` とは併用不可）
- `--seed` は `host` だけでもOK（`--cluster-port` 既定 6222 を補完）
- 追加オプション: `--cluster-port`, `--client-port`, `--http-port`, `--listen`（`host`/`host:port`）

## controller（MVP）
起動:
```powershell
nats-bootstrap controller start --listen 127.0.0.1:8222 --nats-url nats://127.0.0.1:4222 --sys-creds C:\path\sys.creds
```

leave（controller 依頼のみ）:
```powershell
nats-bootstrap leave --controller http://127.0.0.1:8222 --server-name node-1 --nats-url nats://127.0.0.1:4222 --confirm
```
※ MVPではローカル停止は `nats-server.pid` が無いと失敗します。

## Windowsサービス（MVP）
既定ではコピーせず、解決済みの `nats-server.exe` をそのまま参照します。
固定パスにコピーしたい場合は `--bin-dir` を指定します。
※ Windowsサービス操作には管理者権限が必要です。

インストール（コピーなし）:
```powershell
nats-bootstrap service install --service-name nats-bootstrap
```

インストール（固定パスへコピー）:
```powershell
nats-bootstrap service install --service-name nats-bootstrap --bin-dir C:\ProgramData\nats-bootstrap\bin
```

起動:
```powershell
nats-bootstrap up --service --service-name nats-bootstrap
```

状態確認:
```powershell
nats-bootstrap doctor --service-name nats-bootstrap
```

アンインストール:
```powershell
nats-bootstrap service uninstall --service-name nats-bootstrap
```

## backup/restore（MVP）
前提: `nats` CLI が PATH にあるか、`--nats-cli-path` または `NATS_CLI_PATH` を指定します。

バックアップ:
```powershell
nats-bootstrap backup --stream ORDERS --output C:\nats\backup
```

リストア（安全のため `--confirm` 必須）:
```powershell
nats-bootstrap restore --input C:\nats\backup --confirm
```

## テスト
```powershell
uv pip install pytest
pytest -q
```

## 詳細マニュアル
- 日本語: `manuals/manual_ja.md`
- English: `manuals/manual_en.md`

