from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from nats_bootstrap.bootstrap_config import (
    AccountSpec,
    AdvertiseSpec,
    BootstrapConfigError,
    DEFAULT_CONFIG_NAME,
    generate_bootstrap_config,
    normalize_seed,
    resolve_cluster_listen,
)
from nats_bootstrap.cli import _resolve_bootstrap_config


def test_normalize_seed():
    assert normalize_seed("pc-a") == "nats://pc-a:6222"
    assert normalize_seed("pc-a", 7333) == "nats://pc-a:7333"
    assert normalize_seed("pc-a:9000") == "nats://pc-a:9000"
    assert normalize_seed("nats://pc-a:6222") == "nats://pc-a:6222"


def test_generate_bootstrap_config_without_seed(tmp_path: Path):
    result = generate_bootstrap_config("demo", tmp_path, seed=None, server_name="node-1")
    assert result.path == tmp_path / DEFAULT_CONFIG_NAME
    text = result.path.read_text(encoding="utf-8")
    escaped = str(tmp_path).replace("\\", "\\\\")
    assert f'store_dir: "{escaped}"' in text
    assert 'name: "demo"' in text
    assert "routes" not in text


def test_generate_bootstrap_config_with_seed(tmp_path: Path):
    result = generate_bootstrap_config("demo", tmp_path, seed="pc-a", server_name="node-1")
    text = result.path.read_text(encoding="utf-8")
    assert 'routes = [' in text
    assert 'nats://pc-a:6222' in text


def test_generate_bootstrap_config_with_ports(tmp_path: Path):
    result = generate_bootstrap_config(
        "demo",
        tmp_path,
        seed="pc-a",
        server_name="node-1",
        client_port=4333,
        http_port=8333,
        cluster_port=7333,
        cluster_listen="0.0.0.0",
    )
    text = result.path.read_text(encoding="utf-8")
    assert "port: 4333" in text
    assert "http: 8333" in text
    assert 'listen: "0.0.0.0:7333"' in text
    assert "nats://pc-a:7333" in text


def test_generate_bootstrap_config_with_accounts_and_advertise(tmp_path: Path):
    result = generate_bootstrap_config(
        "demo",
        tmp_path,
        seed="pc-a",
        server_name="node-1",
        system_account=AccountSpec(
            name="SYS",
            user="sys",
            password_env="NATS_SYS_PASSWORD",
        ),
        app_account=AccountSpec(
            name="APP",
            user="app",
            password_env="NATS_APP_PASSWORD",
        ),
        advertise=AdvertiseSpec(
            client="nats.example.test:4222",
            cluster="nats-route.example.test:6222",
        ),
    )
    text = result.path.read_text(encoding="utf-8")
    assert 'client_advertise: "nats.example.test:4222"' in text
    assert "accounts: {" in text
    assert "SYS: {" in text
    assert '{user: "sys", password: $NATS_SYS_PASSWORD}' in text
    assert "APP: {" in text
    assert "jetstream: enabled" in text
    assert '{user: "app", password: $NATS_APP_PASSWORD}' in text
    assert "system_account: SYS" in text
    assert 'advertise: "nats-route.example.test:6222"' in text


def test_resolve_cluster_listen():
    assert resolve_cluster_listen("127.0.0.1", 6222) == "127.0.0.1:6222"
    assert resolve_cluster_listen("127.0.0.1:9000", 6222) == "127.0.0.1:9000"


def test_generate_bootstrap_config_invalid_data_dir(tmp_path: Path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(BootstrapConfigError):
        generate_bootstrap_config("demo", file_path, seed=None)


def test_resolve_bootstrap_config_conflict(tmp_path: Path):
    args = argparse.Namespace(
        cluster="demo",
        nats_config="C:\\nats\\nats.conf",
        seed=None,
        datafolder=str(tmp_path),
        client_port=None,
        http_port=None,
        cluster_port=None,
        listen=None,
        command="up",
    )
    path, code = _resolve_bootstrap_config(args)
    assert code == 2
    assert path is None


def test_resolve_bootstrap_config_join_requires_seed(tmp_path: Path):
    args = argparse.Namespace(
        cluster="demo",
        nats_config=None,
        seed=None,
        datafolder=str(tmp_path),
        client_port=None,
        http_port=None,
        cluster_port=None,
        listen=None,
        command="join",
    )
    path, code = _resolve_bootstrap_config(args)
    assert code == 2
    assert path is None


def test_resolve_bootstrap_config_success(tmp_path: Path):
    args = argparse.Namespace(
        cluster="demo",
        nats_config=None,
        seed=None,
        datafolder=str(tmp_path),
        client_port=None,
        http_port=None,
        cluster_port=None,
        listen=None,
        command="up",
    )
    path, code = _resolve_bootstrap_config(args)
    assert code == 0
    assert path is not None
    assert Path(path).exists()
