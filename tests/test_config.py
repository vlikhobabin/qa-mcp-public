from __future__ import annotations

import pytest

from qa_mcp.config import (
    ODATA_DEFAULT_PASSWORD,
    ODATA_DEFAULT_URL,
    ODATA_DEFAULT_USER,
    REGRESSION_ODATA_DEFAULT_USER,
    Settings,
    activate_application_settings,
    active_application_settings,
    env_flag,
)


def test_settings_from_explicit_env_mapping() -> None:
    settings = Settings.from_env({
        "QA_MCP_CLIENT_HOST": "client-host",
        "QA_MCP_CLIENT_PORT": "15444",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15381",
        "QA_MCP_REMOTE_CLIENT": "yes",
        "QA_MCP_LIST_POLL_ATTEMPTS": "7",
        "QA_MCP_LIST_POLL_SETTLE_SEC": "0.2",
        "QA_MCP_HOME": "/work/qa",
        "QA_MCP_MANAGER_TEMPLATES": "/tmp/manager.json",
        "QA_MCP_VALUE_READ_TEMPLATES": "/tmp/value.json",
        "QA_MCP_PLATFORM_VERSION": "8.3.27.2130",
    })

    assert settings.client_host == "client-host"
    assert settings.client_port == 15444
    assert settings.host_agent_client_port == 15381
    assert settings.remote_client is True
    assert settings.list_poll_attempts == 7
    assert settings.list_poll_settle_sec == 0.2
    assert settings.home == "/work/qa"
    assert settings.manager_templates == "/tmp/manager.json"
    assert settings.value_read_templates == "/tmp/value.json"
    assert settings.platform_version == "8.3.27.2130"


def test_remote_client_truth_values() -> None:
    for value in ("1", "true", "yes", "on", " TRUE "):
        assert env_flag(value)
        assert Settings.from_env({"QA_MCP_REMOTE_CLIENT": value}).remote_client is True
    for value in ("", "0", "false", "off", None):
        assert not env_flag(value)
        env = {} if value is None else {"QA_MCP_REMOTE_CLIENT": value}
        assert Settings.from_env(env).remote_client is False


def test_odata_defaults_preserve_client_and_regression_behavior() -> None:
    settings = Settings.from_env({})

    assert settings.odata_url == ODATA_DEFAULT_URL == ""
    assert settings.odata_user == ODATA_DEFAULT_USER == ""
    assert settings.odata_password == ODATA_DEFAULT_PASSWORD == ""
    assert settings.regression_odata_user == REGRESSION_ODATA_DEFAULT_USER == "Администратор"


def test_odata_env_overrides_both_client_and_regression_defaults() -> None:
    settings = Settings.from_env({
        "QA_MCP_ODATA_URL": "http://lab/odata",
        "QA_MCP_ODATA_USER": "reader",
        "QA_MCP_ODATA_PASSWORD": "secret",
    })

    assert settings.odata_url == "http://lab/odata"
    assert settings.odata_user == "reader"
    assert settings.regression_odata_user == "reader"
    assert settings.odata_password == "secret"


def test_target_env_file_supplies_runtime_settings_with_process_override(tmp_path) -> None:
    target = tmp_path / "qa-target.env"
    target.write_text(
        "QA_MCP_ODATA_URL=http://target/odata\n"
        "QA_MCP_ODATA_USER=target-reader\n"
        "QA_MCP_ODATA_PASSWORD=target-secret\n"
        "QA_MCP_CLIENT_PORT=15444\n",
        encoding="utf-8",
    )

    settings = Settings.from_env({
        "QA_MCP_TARGET_ENV_FILE": str(target),
        "QA_MCP_ODATA_USER": "process-reader",
    })

    assert settings.odata_url == "http://target/odata"
    assert settings.odata_user == "process-reader"
    assert settings.odata_password == "target-secret"
    assert settings.client_port == 15444


def test_host_agent_settings_ignore_legacy_product_license_environment() -> None:
    settings = Settings.from_env({
        "QA_MCP_HOST_AGENT": "host:8001",
        "QA_MCP_HOST_AGENT_TOKEN": "tok",
        "QA_MCP_HOST_AGENT_TIMEOUT": "2.5",
        "QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS": "90",
        "QA_MCP_LICENSE_GATE": "1",
        "QA_MCP_LICENSE_BROKER": "/bin/broker",
        "QA_MCP_LICENSE_TIMEOUT": "bad-float",
    })

    assert settings.host_agent == "host:8001"
    assert settings.host_agent_token == "tok"
    assert settings.host_agent_timeout == 2.5
    assert settings.doctor_com_timeout_sec == 90.0
    assert settings.host_agent_client_port == 0
    assert not hasattr(settings, "license_gate")
    assert not hasattr(settings, "license_broker")
    assert not hasattr(settings, "license_timeout")


def test_testclient_relay_settings_are_all_or_nothing() -> None:
    settings = Settings.from_env(
        {
            "QA_MCP_TESTCLIENT_RELAY_ENDPOINT": "station.example:15382",
            "QA_MCP_TESTCLIENT_RELAY_TOKEN": "secret",
        }
    )
    assert settings.testclient_relay_endpoint == "station.example:15382"
    assert settings.testclient_relay_token == "secret"

    with pytest.raises(ValueError, match="must be configured together"):
        Settings.from_env({"QA_MCP_TESTCLIENT_RELAY_ENDPOINT": "station.example:15382"})


def test_active_application_settings_restore_nested_bound_absence_after_failure() -> None:
    outer = Settings(
        manager_templates="outer-manager.json",
        value_read_templates="outer-value.json",
        testclient_relay_endpoint="outer.example:15382",
        testclient_relay_token="outer-synthetic-token",
    )
    absent = Settings(manager_templates="absent-manager.json", value_read_templates="absent-value.json")

    assert active_application_settings() is None
    with activate_application_settings(outer):
        assert active_application_settings() is outer
        with pytest.raises(RuntimeError, match="inner failure"):
            with activate_application_settings(absent):
                assert active_application_settings() is absent
                assert active_application_settings().testclient_relay_endpoint == ""
                raise RuntimeError("inner failure")
        assert active_application_settings() is outer
    assert active_application_settings() is None
