# nats-bootstrap 🌟

**Bootstraps NATS clusters with almost zero config.**  
Start one node, add others with `--seed`, and use the same commands on every machine.

A CLI/library to run NATS (JetStream/KV) clusters with **the same commands everywhere**.
The real value is **Day‑2 ops** (join/leave/backup/restore/service) made safe and repeatable.

Docs: [日本語 README](README_ja.md) | [Detailed manual](manuals/manual_en.md) | [日本語マニュアル](manuals/manual_ja.md) | [NATS CLI install](docs/nats_cli_install.md)

---

## What is it?
- **Same commands** on any machine; no per-node differences.
- `status` / `doctor` show facts fast.
- Windows service support avoids venv breakage (fixed path option).
- **Bootstrap mode**: auto-generate config from `--cluster` or `bootstrap.yaml`.

## Install
```powershell
uv pip install nats-bootstrap
```

Include `nats-server` binary:
```powershell
uv pip install "nats-bootstrap[server]"
```

Note: `nats` CLI is required for backup/restore.
Install guide: [docs/nats_cli_install.md](docs/nats_cli_install.md)
Note: `nats.exe` (CLI) is **not** the server. The server binary is `nats-server.exe`.

## Config types
| File / option | Read by | Purpose |
|---|---|---|
| `nats-config.json` / `--config` | `nats-bootstrap` | Tool config, such as `nats_server_path` |
| `bootstrap.yaml` / `--bootstrap-config` | `nats-bootstrap` | Input used to generate NATS config |
| `<datafolder>\nats-bootstrap.conf` | `nats-server` | Auto-generated raw NATS config |
| `--nats-config <path>` | `nats-server` | User-managed raw NATS config |

`nats-config.json` and `bootstrap.yaml` are not raw NATS server config files.

## nats-bootstrap config priority
1. File passed by `--config`
2. `nats-config.json` in the working directory
3. `~/.nats-bootstrap/nats-config.json`

## Quick usage
```powershell
nats-bootstrap status
nats-bootstrap doctor
nats-bootstrap up --cluster demo
nats-bootstrap join --cluster demo --seed pc-a:6222
nats-bootstrap up --bootstrap-config bootstrap.yaml
```

## Binary resolution order
1. CLI `--nats-server-path`
2. Config `nats_server_path`
3. Env `NATS_SERVER_PATH` (compat: `NATS_SERVER_BIN`)
4. `nats-server-bin` (extras: `server`)
5. `nats-server` in PATH

## Bootstrap mode (no config file)
`--cluster` auto-generates a config file for you.

```powershell
nats-bootstrap up --cluster demo --datafolder C:\nats\data
nats-bootstrap join --cluster demo --seed pc-a:6222 --datafolder C:\nats\data
```

- Default `--datafolder`: `.\nats-bootstrap-data`
- Generated config: `<datafolder>\nats-bootstrap.conf`
- If you want to manage config yourself, use `--nats-config` (cannot be combined with `--cluster`)
- `--seed` can be `host` only; it uses `--cluster-port` (default 6222)
- Optional: `--cluster-port`, `--client-port`, `--http-port`, `--listen` (`host` or `host:port`)

Use `bootstrap.yaml` when you also want accounts and advertise settings:

```yaml
cluster: demo
datafolder: /data/nats
client_port: 4222
http_port: 8222
cluster_port: 6222

system_account:
  name: SYS
  user: sys
  password_env: NATS_SYS_PASSWORD

app_account:
  name: APP
  user: app
  password_env: NATS_APP_PASSWORD

advertise:
  client: null
  cluster: null
```

```powershell
nats-bootstrap up --bootstrap-config bootstrap.yaml
nats-bootstrap join --bootstrap-config bootstrap.yaml --seed pc-a:6222
```

- `password_env` stores only the environment variable name, not the secret value.
- `--bootstrap-config` cannot be combined with `--nats-config` or manual bootstrap options such as `--cluster`.

## controller (MVP)
```powershell
nats-bootstrap controller start --listen 127.0.0.1:8222 --nats-url nats://127.0.0.1:4222 --sys-creds C:\path\sys.creds
nats-bootstrap leave --controller http://127.0.0.1:8222 --server-name node-1 --nats-url nats://127.0.0.1:4222 --confirm
```

## Windows service (MVP)
Default is **no copy** (use resolved `nats-server.exe`). Use `--bin-dir` to copy to a fixed path.
Admin privileges are required.

```powershell
nats-bootstrap service install --service-name nats-bootstrap
nats-bootstrap up --service --service-name nats-bootstrap
nats-bootstrap doctor --service-name nats-bootstrap
nats-bootstrap service uninstall --service-name nats-bootstrap
```

## backup/restore (MVP)
Requires `nats` CLI in PATH or `--nats-cli-path` / `NATS_CLI_PATH`.

```powershell
nats-bootstrap backup --stream ORDERS --output C:\nats\backup
nats-bootstrap restore --input C:\nats\backup --confirm
```

## Tests
```powershell
uv pip install pytest
pytest -q
```

## Manuals
- [English detailed manual](manuals/manual_en.md)
- [日本語詳細マニュアル](manuals/manual_ja.md)
- [日本語 README](README_ja.md)
