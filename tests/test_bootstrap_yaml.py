from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from nats_bootstrap.bootstrap_yaml import BootstrapYamlError, load_bootstrap_yaml
from nats_bootstrap.cli import _resolve_bootstrap_config


def _write_bootstrap_yaml(path: Path, datafolder: str = "data") -> Path:
    path.write_text(
        f"""
cluster: demo
datafolder: {datafolder}
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
  cluster: nats-route.example.test:6222
""".lstrip(),
        encoding="utf-8",
    )
    return path


def test_load_bootstrap_yaml_success(tmp_path: Path):
    path = _write_bootstrap_yaml(tmp_path / "bootstrap.yaml")

    config = load_bootstrap_yaml(path)

    assert config.cluster == "demo"
    assert config.data_dir == (tmp_path / "data").resolve()
    assert config.client_port == 4222
    assert config.system_account.name == "SYS"
    assert config.app_account.user == "app"
    assert config.advertise.client is None
    assert config.advertise.cluster == "nats-route.example.test:6222"


def test_load_bootstrap_yaml_rejects_unknown_root_key(tmp_path: Path):
    path = _write_bootstrap_yaml(tmp_path / "bootstrap.yaml")
    path.write_text(path.read_text(encoding="utf-8") + "unknown: true\n", encoding="utf-8")

    with pytest.raises(BootstrapYamlError, match="unknown keys"):
        load_bootstrap_yaml(path)


def test_resolve_bootstrap_config_from_yaml(tmp_path: Path):
    path = _write_bootstrap_yaml(tmp_path / "bootstrap.yaml")
    args = argparse.Namespace(
        bootstrap_config=str(path),
        cluster=None,
        nats_config=None,
        seed=None,
        datafolder=None,
        client_port=None,
        http_port=None,
        cluster_port=None,
        listen=None,
        command="up",
    )

    config_path, code = _resolve_bootstrap_config(args)

    assert code == 0
    assert config_path is not None
    text = Path(config_path).read_text(encoding="utf-8")
    assert 'name: "demo"' in text
    assert "system_account: SYS" in text
    assert "APP: {" in text
    assert 'advertise: "nats-route.example.test:6222"' in text


def test_resolve_bootstrap_config_rejects_manual_options(tmp_path: Path):
    path = _write_bootstrap_yaml(tmp_path / "bootstrap.yaml")
    args = argparse.Namespace(
        bootstrap_config=str(path),
        cluster="manual",
        nats_config=None,
        seed=None,
        datafolder=None,
        client_port=None,
        http_port=None,
        cluster_port=None,
        listen=None,
        command="up",
    )

    config_path, code = _resolve_bootstrap_config(args)

    assert code == 2
    assert config_path is None
