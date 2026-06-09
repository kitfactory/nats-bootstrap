from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .bootstrap_config import (
    AccountSpec,
    AdvertiseSpec,
    DEFAULT_CLIENT_PORT,
    DEFAULT_CLUSTER_PORT,
    DEFAULT_HTTP_PORT,
)


class BootstrapYamlError(ValueError):
    pass


@dataclass(frozen=True)
class BootstrapYamlConfig:
    cluster: str
    data_dir: Path
    client_port: int
    http_port: int
    cluster_port: int
    system_account: AccountSpec
    app_account: AccountSpec
    advertise: AdvertiseSpec


_ROOT_KEYS = {
    "cluster",
    "datafolder",
    "client_port",
    "http_port",
    "cluster_port",
    "system_account",
    "app_account",
    "advertise",
}
_ACCOUNT_KEYS = {"name", "user", "password_env"}
_ADVERTISE_KEYS = {"client", "cluster"}


def load_bootstrap_yaml(path: Path) -> BootstrapYamlConfig:
    data = _load_yaml(path)
    if not isinstance(data, dict):
        raise BootstrapYamlError("root must be a mapping")

    _reject_unknown_keys(data, _ROOT_KEYS, "root")
    cluster = _required_str(data, "cluster")
    data_dir = _resolve_data_dir(_required_str(data, "datafolder"), path)

    return BootstrapYamlConfig(
        cluster=cluster,
        data_dir=data_dir,
        client_port=_optional_port(data, "client_port", DEFAULT_CLIENT_PORT),
        http_port=_optional_port(data, "http_port", DEFAULT_HTTP_PORT),
        cluster_port=_optional_port(data, "cluster_port", DEFAULT_CLUSTER_PORT),
        system_account=_account(data.get("system_account"), "system_account"),
        app_account=_account(data.get("app_account"), "app_account"),
        advertise=_advertise(data.get("advertise")),
    )


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise BootstrapYamlError("PyYAML is not installed") from exc

    if not path.exists():
        raise BootstrapYamlError("file not found")
    try:
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as exc:
        raise BootstrapYamlError(f"yaml parse failed: {exc}") from exc


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(str(key) for key in data if key not in allowed)
    if unknown:
        joined = ", ".join(unknown)
        raise BootstrapYamlError(f"{label} has unknown keys: {joined}")


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BootstrapYamlError(f"{key} is required")
    return value.strip()


def _optional_port(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise BootstrapYamlError(f"{key} must be an integer")
    if value < 1 or value > 65535:
        raise BootstrapYamlError(f"{key} must be between 1 and 65535")
    return value


def _resolve_data_dir(value: str, source_path: Path) -> Path:
    raw_path = Path(value).expanduser()
    if not raw_path.is_absolute():
        raw_path = source_path.parent / raw_path
    return raw_path.resolve()


def _account(value: Any, label: str) -> AccountSpec:
    if not isinstance(value, dict):
        raise BootstrapYamlError(f"{label} is required")
    _reject_unknown_keys(value, _ACCOUNT_KEYS, label)
    return AccountSpec(
        name=_required_str(value, "name"),
        user=_required_str(value, "user"),
        password_env=_required_str(value, "password_env"),
    )


def _advertise(value: Any) -> AdvertiseSpec:
    if value is None:
        return AdvertiseSpec()
    if not isinstance(value, dict):
        raise BootstrapYamlError("advertise must be a mapping")
    _reject_unknown_keys(value, _ADVERTISE_KEYS, "advertise")
    return AdvertiseSpec(
        client=_optional_str_or_none(value, "client"),
        cluster=_optional_str_or_none(value, "cluster"),
    )


def _optional_str_or_none(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise BootstrapYamlError(f"advertise.{key} must be a string or null")
    return value.strip()
