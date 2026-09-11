"""Central runtime configuration for QA MCP environment variables."""

from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Mapping

from ._bundled import template as bundled_template
from .versioning import PLATFORM_VERSION_ENV, active_version_key

TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
TARGET_ENV_FILE_ENV = "QA_MCP_TARGET_ENV_FILE"

ODATA_URL_ENV = "QA_MCP_ODATA_URL"
ODATA_USER_ENV = "QA_MCP_ODATA_USER"
ODATA_PASSWORD_ENV = "QA_MCP_ODATA_PASSWORD"
ODATA_DEFAULT_URL = ""
ODATA_DEFAULT_USER = ""
ODATA_DEFAULT_PASSWORD = ""
REGRESSION_ODATA_DEFAULT_USER = "Администратор"

CLIENT_HOST_ENV = "QA_MCP_CLIENT_HOST"
CLIENT_PORT_ENV = "QA_MCP_CLIENT_PORT"
REMOTE_CLIENT_ENV = "QA_MCP_REMOTE_CLIENT"
MANAGER_TEMPLATES_ENV = "QA_MCP_MANAGER_TEMPLATES"
VALUE_READ_TEMPLATES_ENV = "QA_MCP_VALUE_READ_TEMPLATES"
LIST_POLL_ATTEMPTS_ENV = "QA_MCP_LIST_POLL_ATTEMPTS"
LIST_POLL_SETTLE_SEC_ENV = "QA_MCP_LIST_POLL_SETTLE_SEC"
DESCRIPTOR_WARMUP_ATTEMPTS_ENV = "QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS"
DESCRIPTOR_WARMUP_DELAY_SEC_ENV = "QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC"
HOME_ENV = "QA_MCP_HOME"

HOST_AGENT_ENV = "QA_MCP_HOST_AGENT"
HOST_AGENT_TOKEN_ENV = "QA_MCP_HOST_AGENT_TOKEN"
HOST_AGENT_EXPECTED_VERSION_ENV = "QA_MCP_HOST_AGENT_EXPECTED_VERSION"
HOST_AGENT_EXPECTED_SHA256_ENV = "QA_MCP_HOST_AGENT_EXPECTED_SHA256"
HOST_AGENT_WINDOW_ENV = "QA_MCP_HOST_AGENT_WINDOW"
HOST_AGENT_CLIENT_PORT_ENV = "QA_MCP_HOST_AGENT_CLIENT_PORT"
HOST_AGENT_TIMEOUT_ENV = "QA_MCP_HOST_AGENT_TIMEOUT"

HTTP_TRANSPORT_ENV = "QA_MCP_TRANSPORT"
HTTP_HOST_ENV = "QA_MCP_HTTP_HOST"
HTTP_PORT_ENV = "QA_MCP_HTTP_PORT"
BEARER_TOKEN_ENV = "QA_MCP_BEARER_TOKEN"
DOCTOR_COM_INFOBASE_ENV = "QA_MCP_DOCTOR_COM_INFOBASE"
DOCTOR_COM_USER_ENV = "QA_MCP_DOCTOR_COM_USER"
DOCTOR_COM_PASSWORD_ENV = "QA_MCP_DOCTOR_COM_PASSWORD"
DOCTOR_COM_QUERY_ENV = "QA_MCP_DOCTOR_COM_QUERY"
DOCTOR_COM_TIMEOUT_ENV = "QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS"

TESTCLIENT_LIBGCC_PRELOAD_ENV = "QA_MCP_TESTCLIENT_LIBGCC_PRELOAD"
TESTCLIENT_OWNERSHIP_ROOT_ENV = "QA_MCP_TESTCLIENT_OWNERSHIP_ROOT"
TESTCLIENT_RELAY_ENDPOINT_ENV = "QA_MCP_TESTCLIENT_RELAY_ENDPOINT"
TESTCLIENT_RELAY_TOKEN_ENV = "QA_MCP_TESTCLIENT_RELAY_TOKEN"


def env_flag(value: str | None) -> bool:
    return (value or "").strip().lower() in TRUE_VALUES


def _int_value(values: Mapping[str, str], name: str, default: int) -> int:
    raw = values.get(name)
    return default if raw is None or raw == "" else int(raw)


def _float_value(values: Mapping[str, str], name: str, default: float) -> float:
    raw = values.get(name)
    return default if raw is None or raw == "" else float(raw)


def _float_value_or_default(values: Mapping[str, str], name: str, default: float) -> float:
    try:
        return _float_value(values, name, default)
    except ValueError:
        return default


def _load_target_env(path: str) -> dict[str, str]:
    target = Path(path)
    if not target.is_file():
        return {}
    loaded: dict[str, str] = {}
    for raw in target.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        loaded[key.strip()] = value
    return loaded


def effective_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    """Return target-profile settings overlaid by the explicit process environment."""
    explicit = os.environ if env is None else env
    target_env_file = explicit.get(TARGET_ENV_FILE_ENV, "").strip()
    if not target_env_file:
        return explicit
    merged = _load_target_env(target_env_file)
    merged.update(explicit)
    return merged


@dataclass(frozen=True)
class Settings:
    """Parsed QA MCP environment settings.

    Supported variables:
    `QA_MCP_PLATFORM_VERSION`, `QA_MCP_MANAGER_TEMPLATES`, `QA_MCP_VALUE_READ_TEMPLATES`,
    `QA_MCP_CLIENT_HOST`, `QA_MCP_CLIENT_PORT`, `QA_MCP_REMOTE_CLIENT`, `QA_MCP_LIST_POLL_ATTEMPTS`,
    `QA_MCP_LIST_POLL_SETTLE_SEC`, `QA_MCP_HOME`, `QA_MCP_ODATA_URL`, `QA_MCP_ODATA_USER`,
    `QA_MCP_ODATA_PASSWORD`, `QA_MCP_HOST_AGENT`, `QA_MCP_HOST_AGENT_TOKEN`,
    `QA_MCP_HOST_AGENT_EXPECTED_VERSION`, `QA_MCP_HOST_AGENT_EXPECTED_SHA256`,
    `QA_MCP_HOST_AGENT_WINDOW`, `QA_MCP_HOST_AGENT_CLIENT_PORT`,
    `QA_MCP_HOST_AGENT_TIMEOUT`, `QA_MCP_TRANSPORT`,
    `QA_MCP_HTTP_HOST`, `QA_MCP_HTTP_PORT`,
    `QA_MCP_BEARER_TOKEN`, `QA_MCP_DOCTOR_COM_INFOBASE`,
    `QA_MCP_DOCTOR_COM_USER`, `QA_MCP_DOCTOR_COM_PASSWORD`,
    `QA_MCP_DOCTOR_COM_QUERY`, `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS`,
    `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD`, `QA_MCP_TESTCLIENT_OWNERSHIP_ROOT`,
    `QA_MCP_TESTCLIENT_RELAY_ENDPOINT`, and `QA_MCP_TESTCLIENT_RELAY_TOKEN`.
    """

    manager_templates: str
    value_read_templates: str
    platform_version: str = ""
    client_host: str = "127.0.0.1"
    client_port: int = 15381
    remote_client: bool = False
    list_poll_attempts: int = 3
    list_poll_settle_sec: float = 0.6
    # Cold-client first-read hardening: a heavy configuration (e.g. [redacted third-party configuration] / Бухгалтерия 3.0)
    # can return an empty live form descriptor (opened=None, 0 elements) on the first read right
    # after client launch — the managed form is not ready yet over the protocol. Retry the live
    # descriptor read a bounded number of times before failing, so a cold client self-heals.
    descriptor_warmup_attempts: int = 3
    descriptor_warmup_delay_sec: float = 1.5
    home: str = ""
    odata_url: str = ODATA_DEFAULT_URL
    odata_user: str = ODATA_DEFAULT_USER
    odata_password: str = ODATA_DEFAULT_PASSWORD
    regression_odata_user: str = REGRESSION_ODATA_DEFAULT_USER
    host_agent: str = ""
    host_agent_token: str = ""
    host_agent_expected_version: str = ""
    host_agent_expected_sha256: str = ""
    host_agent_window: str = ""
    host_agent_client_port: int = 0
    host_agent_timeout: float = 10.0
    http_transport: str = "stdio"
    http_host: str = "127.0.0.1"
    http_port: int = 8000
    bearer_token_present: bool = False
    doctor_com_infobase_path: str = ""
    doctor_com_user: str = ""
    doctor_com_password: str = ""
    doctor_com_query: str = ""
    doctor_com_timeout_sec: float = 3.0
    testclient_libgcc_preload: str = ""
    testclient_ownership_root: str = ""
    testclient_relay_endpoint: str = ""
    testclient_relay_token: str = ""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        values = effective_env(env)
        relay_endpoint = values.get(TESTCLIENT_RELAY_ENDPOINT_ENV, "").strip()
        relay_token = values.get(TESTCLIENT_RELAY_TOKEN_ENV, "").strip()
        if bool(relay_endpoint) != bool(relay_token):
            raise ValueError(
                "QA_MCP_TESTCLIENT_RELAY_ENDPOINT and QA_MCP_TESTCLIENT_RELAY_TOKEN must be configured together"
            )
        version = active_version_key(env=values)
        return cls(
            manager_templates=values.get(MANAGER_TEMPLATES_ENV)
            or str(bundled_template("manager_frame_templates.json", version)),
            value_read_templates=values.get(VALUE_READ_TEMPLATES_ENV)
            or str(bundled_template("value_read_templates.json", version)),
            platform_version=values.get(PLATFORM_VERSION_ENV, "").strip(),
            client_host=values.get(CLIENT_HOST_ENV, "127.0.0.1"),
            client_port=_int_value(values, CLIENT_PORT_ENV, 15381),
            remote_client=env_flag(values.get(REMOTE_CLIENT_ENV)),
            list_poll_attempts=_int_value(values, LIST_POLL_ATTEMPTS_ENV, 3),
            list_poll_settle_sec=_float_value(values, LIST_POLL_SETTLE_SEC_ENV, 0.6),
            descriptor_warmup_attempts=_int_value(values, DESCRIPTOR_WARMUP_ATTEMPTS_ENV, 3),
            descriptor_warmup_delay_sec=_float_value(values, DESCRIPTOR_WARMUP_DELAY_SEC_ENV, 1.5),
            home=values.get(HOME_ENV, ""),
            odata_url=values.get(ODATA_URL_ENV, ODATA_DEFAULT_URL),
            odata_user=values.get(ODATA_USER_ENV, ODATA_DEFAULT_USER),
            odata_password=values.get(ODATA_PASSWORD_ENV, ODATA_DEFAULT_PASSWORD),
            regression_odata_user=values.get(ODATA_USER_ENV, REGRESSION_ODATA_DEFAULT_USER),
            host_agent=values.get(HOST_AGENT_ENV, "").strip(),
            host_agent_token=values.get(HOST_AGENT_TOKEN_ENV, "").strip(),
            host_agent_expected_version=values.get(HOST_AGENT_EXPECTED_VERSION_ENV, "").strip(),
            host_agent_expected_sha256=values.get(HOST_AGENT_EXPECTED_SHA256_ENV, "").strip().lower(),
            host_agent_window=values.get(HOST_AGENT_WINDOW_ENV, "").strip(),
            host_agent_client_port=_int_value(values, HOST_AGENT_CLIENT_PORT_ENV, 0),
            host_agent_timeout=_float_value(values, HOST_AGENT_TIMEOUT_ENV, 10.0),
            http_transport=values.get(HTTP_TRANSPORT_ENV, "stdio").strip().lower(),
            http_host=values.get(HTTP_HOST_ENV, "127.0.0.1").strip() or "127.0.0.1",
            http_port=_int_value(values, HTTP_PORT_ENV, 8000),
            bearer_token_present=bool(values.get(BEARER_TOKEN_ENV, "").strip()),
            doctor_com_infobase_path=values.get(DOCTOR_COM_INFOBASE_ENV, "").strip(),
            doctor_com_user=values.get(DOCTOR_COM_USER_ENV, "").strip(),
            doctor_com_password=values.get(DOCTOR_COM_PASSWORD_ENV, ""),
            doctor_com_query=values.get(DOCTOR_COM_QUERY_ENV, "").strip(),
            doctor_com_timeout_sec=_float_value_or_default(values, DOCTOR_COM_TIMEOUT_ENV, 3.0),
            testclient_libgcc_preload=values.get(TESTCLIENT_LIBGCC_PRELOAD_ENV, "").strip(),
            testclient_ownership_root=values.get(TESTCLIENT_OWNERSHIP_ROOT_ENV, "").strip(),
            testclient_relay_endpoint=relay_endpoint,
            testclient_relay_token=relay_token,
        )


# A bound Settings instance with empty relay fields is deliberately distinct
# from the unbound state.  Transport resolution will use that distinction to
# avoid falling back to process configuration inside a composed application.
_ACTIVE_APPLICATION_SETTINGS: ContextVar[Settings | None] = ContextVar(
    "qa_mcp_application_settings",
    default=None,
)


def active_application_settings() -> Settings | None:
    """Return the Settings bound by application activation, if any."""

    return _ACTIVE_APPLICATION_SETTINGS.get()


@contextmanager
def activate_application_settings(settings: Settings) -> Iterator[Settings]:
    """Bind immutable application Settings for the lifetime of a composed call."""

    token = _ACTIVE_APPLICATION_SETTINGS.set(settings)
    try:
        yield settings
    finally:
        _ACTIVE_APPLICATION_SETTINGS.reset(token)
