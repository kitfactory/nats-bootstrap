# nats-bootstrap Detailed Manual 🇺🇸

A friendly, emoji-filled guide. Let’s make ops fun! 🎉
This manual walks through **one concrete clustering scenario**, plus **backup** and **Windows service** setup in detail.

---

## 1. What is this? 🤔
**nats-bootstrap** lets you build a NATS cluster with **the same commands on any machine**.
- Same commands on any machine; no per-node steps
- `doctor` shows the facts fast
- Windows service support for stable ops
- **Bootstrap mode** lets you form a cluster without config files

---

## 2. Prerequisites 🧰
1. Python 3.10+
2. nats-bootstrap
3. `nats-server`
4. `nats` CLI (required for backup/restore)
   Install guide: `docs/nats_cli_install.md`
   Note: `nats.exe` (CLI) is not the server. The server binary is `nats-server.exe`.
5. Admin privileges for Windows service operations

Install:
```powershell
uv pip install nats-bootstrap
```

Include `nats-server`:
```powershell
uv pip install "nats-bootstrap[server]"
```

---

## 3. Cluster Example (start 1st node → add others) 🧩
Scenario: PC-A / PC-B / PC-C

Config files are **auto-generated**. Just pass `--cluster`.

### 3.1 Start the first node (no config file) 🚀
```powershell
nats-bootstrap up --cluster demo --datafolder C:\nats\data
```
- `--datafolder` is **local storage per node**
- Default is `.\nats-bootstrap-data`
- Generated config is saved at `<datafolder>\nats-bootstrap.conf`

### 3.2 Add a node later (join) 🧩
```powershell
nats-bootstrap join --cluster demo --seed pc-a:6222 --datafolder C:\nats\data
```
- `--seed` is the first node location (`host` or `host:port`)
- If you pass only `host`, it uses `--cluster-port` (default 6222)
- **`join` is an alias of `up`** (same behavior)
- Use `join` to make “adding a node” explicit

node3 is the same: point `--seed` at node1.

Note: if you want to use an existing config file, use `--nats-config` (cannot be combined with `--cluster`).
Note: extra options are `--cluster-port`, `--client-port`, `--http-port`, `--listen` (`host` or `host:port`).

### 3.3 Check status ✅
```powershell
nats-bootstrap status
nats-bootstrap doctor
```
You’ll see **which binary**, **version**, and **resolution path**.

---

## 4. Windows Service (Detailed) 🪟
Service ops are critical for real-world stability.

### 4.1 Install (no copy)
```powershell
nats-bootstrap service install --service-name nats-bootstrap
```
- Uses the resolved `nats-server.exe` directly.
- Easiest option.

### 4.2 Install (copy to fixed path)
```powershell
nats-bootstrap service install --service-name nats-bootstrap \
  --bin-dir C:\ProgramData\nats-bootstrap\bin
```
- **Recommended for production**.
- Prevents breakage when venv updates.

### 4.3 Start
```powershell
nats-bootstrap up --service --service-name nats-bootstrap
```

### 4.4 Check state
```powershell
nats-bootstrap doctor --service-name nats-bootstrap
```
You’ll see `RUNNING` / `STOPPED`.

### 4.5 Uninstall
```powershell
nats-bootstrap service uninstall --service-name nats-bootstrap
```

**Note**: run service operations as **Administrator**.

---

## 5. Backup (Detailed) 💾
Backup uses the **nats CLI**.

### 5.1 Requirements
- `nats` in PATH, or
- `--nats-cli-path` / `NATS_CLI_PATH`

### 5.2 Run backup (easy)
```powershell
nats-bootstrap backup --stream ORDERS --output C:\nats\backup
```

---

## 6. Restore (Detailed) ♻️
Restore can overwrite data, so `--confirm` is required.

```powershell
nats-bootstrap restore --input C:\nats\backup --confirm
```

---

## 7. Quick Troubleshooting ❓
- `nats-server not found` → set `--nats-server-path` or install `[server]`
- `nats cli not found` → install `nats` CLI or set `--nats-cli-path`
- `--confirm is required` → safety flag for destructive ops

---

## Q. Is `nats.exe` the server?
- No. `nats.exe` is the **CLI tool**.
- The server binary is `nats-server.exe`.

## Wrap-up 🎯
Cluster setup, services, and backups are **simple and consistent** with nats-bootstrap.
Have fun running NATS the safe way! 🚀
