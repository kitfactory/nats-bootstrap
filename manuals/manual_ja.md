# nats-bootstrap 詳細マニュアル 🇯🇵

**やさしく・楽しく**説明します！🎉
NATSクラスタの構築から、バックアップ、Windowsサービス化まで、**「簡単にできる」**ことを体験できる内容です。

---

## 1. これって何？🤔
**nats-bootstrap** は、NATSクラスタを**どの端末でも同じコマンドで作れる**CLIです。
- どの端末でも**同じコマンド**でクラスタ構築OK
- 困ったら `doctor` で「今の事実」が一発表示
- Windowsサービス化で、**venv更新でも壊れにくい**
- **bootstrap モード**で設定ファイルなしでもクラスタ構築が可能

---

## 2. 準備するもの 🧰
1. Python（3.10+）
2. nats-bootstrap
3. NATSサーバ（`nats-server`）
4. NATS CLI（`nats`）※backup/restore必須
   インストール方法: `docs/nats_cli_install.md`
   ※ `nats.exe`（CLI）はサーバーではありません。サーバーは `nats-server.exe` です。
5. Windowsサービス操作は管理者権限

インストール:
```powershell
uv pip install nats-bootstrap
```

`nats-server` 同梱（推奨）:
```powershell
uv pip install "nats-bootstrap[server]"
```

---

## 3. クラスタ構築の例（最初の1台 → 追加）🧩
例: PC-A / PC-B / PC-C の3台でクラスタ

設定ファイルは **自動生成** できます。`--cluster` を付けるだけでOKです。

### 3.1 最初の1台を起動（設定ファイル不要）🚀
```powershell
nats-bootstrap up --cluster demo --datafolder C:\nats\data
```
- `--datafolder` は**各ノードのローカル保存先**
- 未指定なら `.\nats-bootstrap-data` を使います
- 設定ファイルは `<datafolder>\nats-bootstrap.conf` に自動保存

### 3.2 後からノードを追加（join）🧩
```powershell
nats-bootstrap join --cluster demo --seed pc-a:6222 --datafolder C:\nats\data
```
- `--seed` は最初の1台の場所（`host` / `host:port` でOK）
- `host` だけなら `--cluster-port`（既定 6222）を補完します
- **join は up のエイリアス**（処理は同じ）
- 追加ノードの意味を明確にできるので join を推奨

node3 も同様に、`--seed` を node1 に向ければOKです。

※ 既存の設定ファイルを使う場合は `--nats-config` を利用できます（`--cluster` とは併用不可）。
※ 追加オプション: `--cluster-port`, `--client-port`, `--http-port`, `--listen`（`host`/`host:port`）

### 3.3 状態確認 ✅
```powershell
nats-bootstrap status
nats-bootstrap doctor
```
- **どのバイナリを使っているか**
- **バージョン**
- **解決経路**
が全部わかります。

---

## 4. Windowsサービス化（詳細）🪟
サービス化は「本番運用の超重要ポイント」です。

### 4.1 インストール（コピーなし）
```powershell
nats-bootstrap service install --service-name nats-bootstrap
```
- これは **venv 内の nats-server.exe をそのまま使う** 方式です。
- いちばん簡単。

### 4.2 インストール（固定パスへコピー）
```powershell
nats-bootstrap service install --service-name nats-bootstrap \
  --bin-dir C:\ProgramData\nats-bootstrap\bin
```
- **venv更新でも壊れにくい**おすすめ方式。
- 企業運用ならこちらが安全。

### 4.3 起動
```powershell
nats-bootstrap up --service --service-name nats-bootstrap
```

### 4.4 状態確認
```powershell
nats-bootstrap doctor --service-name nats-bootstrap
```
RUNNING / STOPPED が見えます。

### 4.5 アンインストール
```powershell
nats-bootstrap service uninstall --service-name nats-bootstrap
```

**ポイント**: サービス操作は管理者権限で実行してください。

---

## 5. バックアップ（詳細）💾
バックアップは **nats CLI** を使います。

### 5.1 前提
- `nats` が PATH にある
  もしくは
- `--nats-cli-path` / `NATS_CLI_PATH` を指定

### 5.2 実行（簡単）
```powershell
nats-bootstrap backup --stream ORDERS --output C:\nats\backup
```
- `ORDERS` という Stream をバックアップします。
- 出力先フォルダは自動で作成されます。

---

## 6. リストア（詳細）♻️
リストアは **上書きがあり得る**ので `--confirm` が必須です。

```powershell
nats-bootstrap restore --input C:\nats\backup --confirm
```

---

## 7. よくある質問（超短）❓

### Q. `nats-server not found` が出る
- `--nats-server-path` を指定
- もしくは `nats-bootstrap[server]` を入れる

### Q. `nats cli not found` が出る
- `nats` CLI を入れる（公式配布）
- `--nats-cli-path` を使う

### Q. `nats.exe` はサーバー？
- いいえ。`nats.exe` は **CLI（操作ツール）** です。
- サーバーは `nats-server.exe` です。

### Q. `--confirm is required` が出る
- 破壊操作なので安全のため必須です

---

## まとめ 🎯
- **クラスタ構築**も
- **サービス運用**も
- **バックアップ**も

全部 **同じ感覚で簡単に**できるのが nats-bootstrap です！

次はあなたの環境で試してみましょう 🚀

