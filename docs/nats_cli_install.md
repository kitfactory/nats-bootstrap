# nats CLI インストールガイド（Windows / macOS / Linux）

この文書は **nats-bootstrap の backup/restore 用**の `nats` CLI 導入手順をまとめたものです。  
（up/join/status/doctor には不要）

※ `nats.exe`（CLI）はサーバーではありません。サーバーは `nats-server.exe` です。

---

## 1. 共通の確認
インストール後にバージョン確認をします。

```powershell
nats --version
```

---

## 2. Windows
### 2.1 Scoop（推奨）
```powershell
scoop bucket add extras
scoop install extras/natscli
```

### 2.2 GitHub Releases から手動導入
- `nats-io/natscli` の Releases から Windows 用の Zip を取得
- 展開した `nats.exe` を PATH に追加

---

## 3. macOS
### 3.1 Homebrew（推奨）
```bash
brew tap nats-io/nats-tools
brew install nats-io/nats-tools/nats
```

### 3.2 GitHub Releases / go install
- Releases の Zip を展開し PATH に追加
- もしくは Go を使って導入（次項参照）

---

## 4. Linux
### 4.1 GitHub Releases（DEB/RPM）
- Debian/Ubuntu 系: `.deb` を取得して `dpkg -i nats-*.deb`
- RHEL/Fedora 系: `.rpm` を取得して `rpm -i nats-*.rpm`

### 4.2 Arch（AUR）
```bash
yay natscli
```

### 4.3 go install（全OS共通）
```bash
go install github.com/nats-io/natscli/nats@latest
```
※ `go env GOPATH` の `bin` が PATH に入っている必要があります。
