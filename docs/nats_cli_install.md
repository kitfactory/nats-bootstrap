# nats CLI Install Guide (Windows / macOS / Linux)

Language: [日本語](nats_cli_install_ja.md)

This guide explains how to install the `nats` CLI used by **nats-bootstrap backup/restore**.
It is not required for `up`, `join`, `status`, or `doctor`.

Note: `nats.exe` is the CLI, not the server. The server binary is `nats-server.exe`.

---

## 1. Verify Installation
After installation, check the version:

```powershell
nats --version
```

---

## 2. Windows
### 2.1 Scoop (Recommended)
```powershell
scoop bucket add extras
scoop install extras/natscli
```

### 2.2 Manual Install From GitHub Releases
- Download the Windows zip from `nats-io/natscli` Releases.
- Extract `nats.exe`.
- Add the directory containing `nats.exe` to `PATH`.

---

## 3. macOS
### 3.1 Homebrew (Recommended)
```bash
brew tap nats-io/nats-tools
brew install nats-io/nats-tools/nats
```

### 3.2 GitHub Releases / go install
- Extract the release zip and add it to `PATH`.
- Or install with Go as shown below.

---

## 4. Linux
### 4.1 GitHub Releases (DEB/RPM)
- Debian/Ubuntu: download the `.deb` and run `dpkg -i nats-*.deb`.
- RHEL/Fedora: download the `.rpm` and run `rpm -i nats-*.rpm`.

### 4.2 Arch (AUR)
```bash
yay natscli
```

### 4.3 go install (All OSes)
```bash
go install github.com/nats-io/natscli/nats@latest
```

Make sure the `bin` directory from `go env GOPATH` is in `PATH`.

---

Back to: [English README](../README.md) | [Detailed manual](../manuals/manual_en.md) | [日本語](nats_cli_install_ja.md)
