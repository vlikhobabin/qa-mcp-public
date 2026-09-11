"""Display primitive backends for local X11 and model-B host-agent routing."""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import Settings
from .screenshot import PNG_MAGIC

HOST_AGENT_VERSION = "1.0.0-standalone"
HOST_AGENT_DISPLAY_PROTOCOL = "qa-mcp.windows-host-bridge.v1"
HOST_BRIDGE_API = "qa-mcp.windows-host-bridge"
HOST_BRIDGE_API_MAJOR = 1
HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_CAPABILITY = "testclient-lifecycle-handle-stop"
HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY = "testclient-window-target"
HOST_BRIDGE_REQUIRED_CAPABILITIES = frozenset({
    "bounded-input",
    "health",
    "screenshot",
    "testclient-lifecycle",
    "testclient-relay",
    "uia-visible-list-cells",
    "window-list",
    HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_CAPABILITY,
    HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY,
})
HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_VERSIONS = frozenset({
    HOST_AGENT_VERSION,
})
HOST_AGENT_CAPABILITIES_LIMIT = 64
COMPATIBLE_HOST_AGENT_VERSIONS = frozenset({
    HOST_AGENT_VERSION,
})
DEFAULT_HOST_AGENT = "host.docker.internal:8001"
# The host-agent `/testclient/launch` endpoint now blocks synchronously until it
# has classified TestClient readiness (up to its own `timeout_seconds` launch
# wait). The HTTP request timeout for that one call must therefore cover the
# readiness wait plus a margin, instead of the short default `host_agent_timeout`
# used for fire-and-forget primitives — otherwise a real launch times out on the
# client before the host-agent can answer.
LAUNCH_HTTP_TIMEOUT_MARGIN = 15.0

# Public codes are local protocol vocabulary, never arbitrary remote text.
# Unknown codes (including plausible future identifiers) use a fixed fallback.
_PUBLIC_HOST_AGENT_ERROR_CODES = frozenset({
    "active-testclient-client-target-invalid",
    "active-testclient-client-target-missing",
    "host-agent-api-major-incompatible",
    "host-agent-capability-document-invalid",
    "host-agent-capability-missing",
    "host-agent-configuration-invalid",
    "host-agent-error",
    "host-agent-hash-mismatch",
    "host-agent-http-error",
    "host-agent-invalid-json",
    "host-agent-invalid-png",
    "host-agent-invalid-window-list",
    "host-agent-not-configured",
    "host-agent-screenshot-missing-png",
    "host-agent-screenshot-error",
    "host-agent-testclient-lifecycle-unsupported",
    "host-agent-testclient-window-target-unsupported",
    "host-agent-unreachable",
    "host-agent-version-mismatch",
    "execution-capacity-exhausted",
    "token-not-configured",
    "origin-not-allowed",
    "rate-limited",
    "auth-failed",
    "method-not-allowed",
    "empty-keys",
    "invalid-json",
    "unsupported-platform",
    "window-not-found",
    "foreground-denied",
    "missing-client-target",
    "invalid-client-target",
    "stale-client-target",
    "client-target-mismatch",
    "desktop-session-locked",
    "desktop-session-disconnected",
    "desktop-session-noninteractive",
    "primitive-failed",
    "invalid-port",
    "invalid-pid",
    "invalid-lifecycle-handle",
    "invalid-field",
    "missing-target",
    "invalid-platform-version",
    "executable-not-allowed",
    "platform-version-not-found",
    "platform-executable-not-found",
    "testclient-interactive-session-unavailable",
    "testclient-launch-start-failed",
    "testclient-exited-early",
    "testclient-launch-canceled",
    "testclient-not-listening",
    "testclient-pid-handoff-failed",
    "testclient-launch-cleanup-failed",
})


class DisplayBackendError(RuntimeError):
    """Structured display backend failure suitable for MCP result payloads."""

    def __init__(
        self,
        code: str,
        detail: str,
        *,
        status: int | None = None,
        install_command: str | None = None,
        cause: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status = status
        self.install_command = install_command
        self.cause = cause
        self.payload = dict(payload or {})

    def to_result(self, tool: str, *, remote_client: bool | None = None) -> dict[str, Any]:
        # Backend responses and transport causes are untrusted.  They can echo
        # the agent token or local host configuration, so composed MCP results
        # deliberately preserve only the typed code/status and a bounded,
        # source-independent diagnostic.
        code = self.code if self.code in _PUBLIC_HOST_AGENT_ERROR_CODES else "host-agent-error"
        detail = {
            "host-agent-not-configured": "host agent configuration is missing",
            "host-agent-unreachable": "Windows host display agent is unreachable from the container.",
        }.get(code, "host agent request failed")
        result: dict[str, Any] = {
            "ok": False,
            "error": code,
            "tool": tool,
            "detail": detail,
            "mode": "remote-client" if (remote_client if remote_client is not None else remote_client_enabled()) else "local",
        }
        if type(self.status) is int and 100 <= self.status <= 599:
            result["status"] = self.status
        if self.install_command:
            result["install_command"] = self.install_command
        return result


def remote_client_enabled(env: dict[str, str] | None = None) -> bool:
    return Settings.from_env(env).remote_client


def host_agent_address(env: dict[str, str] | None = None) -> str:
    return Settings.from_env(env).host_agent


def remote_agent_configured(
    env: dict[str, str] | None = None,
    *,
    settings: Settings | None = None,
) -> bool:
    return bool(settings.host_agent if settings is not None else host_agent_address(env))


def host_agent_version_relationship(
    version: str,
    expected_version: str,
    *,
    display_protocol: str = "",
    version_pinned: bool = False,
) -> str:
    """Classify build compatibility without treating a build label as a protocol."""
    if version_pinned or expected_version != HOST_AGENT_VERSION:
        return "pinned" if version == expected_version else "incompatible"
    if display_protocol:
        if display_protocol != HOST_AGENT_DISPLAY_PROTOCOL:
            return "protocol-incompatible"
        return "current" if version == HOST_AGENT_VERSION else "protocol-compatible"
    if version in COMPATIBLE_HOST_AGENT_VERSIONS:
        return "current" if version == HOST_AGENT_VERSION else "legacy-compatible"
    return "incompatible"


def host_agent_version_compatible(
    version: str,
    expected_version: str,
    *,
    display_protocol: str = "",
    version_pinned: bool = False,
) -> bool:
    return host_agent_version_relationship(
        version,
        expected_version,
        display_protocol=display_protocol,
        version_pinned=version_pinned,
    ) in {"current", "protocol-compatible", "legacy-compatible", "pinned"}


def host_agent_testclient_lifecycle_stop_supported(handshake: dict[str, Any]) -> bool:
    version = str(handshake.get("version") or "")
    if version in HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_VERSIONS:
        return True
    capabilities = handshake.get("capabilities")
    if isinstance(capabilities, dict):
        return capabilities.get(HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_CAPABILITY) is True
    if isinstance(capabilities, list):
        return HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_CAPABILITY in capabilities
    return False


def host_agent_testclient_window_target_supported(handshake: dict[str, Any] | None) -> bool:
    if not isinstance(handshake, dict):
        return False
    capabilities = handshake.get("capabilities")
    if isinstance(capabilities, dict):
        return capabilities.get(HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY) is True
    if isinstance(capabilities, list):
        return HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY in capabilities
    return False


def _explicit_window_selector(value: str | None) -> str:
    selector = str(value or "").strip()
    return "" if selector in {"", "*"} else selector


def _validated_client_target(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    pid = value.get("pid")
    port = value.get("port")
    if (
        not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 0
        or not isinstance(port, int)
        or isinstance(port, bool)
        or not 0 < port <= 65535
    ):
        return None
    kind = str(value.get("kind") or "host-agent-testclient").strip()
    if kind != "host-agent-testclient":
        return None
    target: dict[str, Any] = {"kind": kind, "pid": pid, "port": port}
    lifecycle_id = str(value.get("lifecycle_id") or "").strip()
    if lifecycle_id:
        target["lifecycle_id"] = lifecycle_id
    return target


def _normalize_host_agent_capabilities(capabilities: Any) -> list[str] | dict[str, bool] | None:
    if isinstance(capabilities, list):
        names: list[str] = []
        for item in capabilities:
            if not isinstance(item, str) or not item:
                continue
            names.append(item)
            if len(names) >= HOST_AGENT_CAPABILITIES_LIMIT:
                break
        return names or None

    if isinstance(capabilities, dict):
        flags: dict[str, bool] = {}
        for name, enabled in capabilities.items():
            if not isinstance(name, str) or not name or not isinstance(enabled, bool):
                continue
            flags[name] = enabled
            if len(flags) >= HOST_AGENT_CAPABILITIES_LIMIT:
                break
        return flags or None

    return None


def host_agent_install_command(
    env: dict[str, str] | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    settings = settings or Settings.from_env(env)
    address = settings.host_agent or DEFAULT_HOST_AGENT
    _, _, port = address.rpartition(":")
    port_arg = port if port.isdigit() else "8001"
    return (
        "powershell -ExecutionPolicy Bypass -File "
        ".\\host-agent\\install-windows-host-agent.ps1 "
        f"-Port {port_arg} -BindAddress 0.0.0.0 -RemoteAddress 192.168.65.0/24"
    )


def _base_url(address: str, *, install_command: str | None = None) -> str:
    if not address:
        raise DisplayBackendError(
            "host-agent-not-configured",
            "QA_MCP_HOST_AGENT is not set; install and configure the Windows host-side input/screenshot agent.",
            install_command=install_command or host_agent_install_command(),
        )
    if "://" not in address:
        address = f"http://{address}"
    return address.rstrip("/")


@dataclass
class LocalXTestBackend:
    """Local Linux display backend delegating to the existing XTEST/X11 helpers."""

    name: str = "local-xtest"

    def send_keys(self, keys: str | list[str], *, display: str = ":89", settle_sec: float = 0.15) -> dict[str, Any]:
        from . import native_xtest

        result = native_xtest.send_keys(keys, display=display, settle_sec=settle_sec)
        result["backend"] = self.name
        return result

    def type_text(self, text: str, *, display: str = ":89", delay_ms: int = 20, unicode: bool = True) -> dict[str, Any]:
        from . import native_xtest

        if unicode:
            native_xtest.xtest_type_unicode(display, text, delay_ms=delay_ms)
        else:
            native_xtest.xtest_type(display, text, delay_ms=delay_ms)
        return {"text_length": len(text), "display": display, "typed": True, "backend": self.name}

    def click(self, x: int, y: int, *, display: str = ":89", button: int = 1) -> dict[str, Any]:
        from . import native_xtest

        native_xtest.xtest_click(display, x, y, button=button)
        return {"x": int(x), "y": int(y), "button": int(button), "display": display, "clicked": True,
                "backend": self.name}

    def double_click(
        self, x: int, y: int, *, display: str = ":89", button: int = 1, gap_ms: int = 120
    ) -> dict[str, Any]:
        from . import native_xtest

        native_xtest.xtest_double_click(display, x, y, button=button, gap_ms=gap_ms)
        return {"x": int(x), "y": int(y), "button": int(button), "display": display, "double_clicked": True,
                "backend": self.name}

    def capture_screenshot(
        self,
        display: str,
        out_path: str | os.PathLike[str],
        *,
        window: str | None = None,
    ) -> dict[str, Any]:
        from . import screenshot

        result = screenshot.capture_screenshot(display, out_path, window=window)
        result["backend"] = self.name
        return result

    def list_windows(self, display: str, *, geometry: bool = True) -> list[dict[str, Any]]:
        from . import windows

        return windows.list_windows(display, geometry=geometry)


@dataclass
class RemoteAgentBackend:
    """HTTP client for the Windows host-side display agent."""

    address: str
    token: str = ""
    expected_version: str = HOST_AGENT_VERSION
    version_pinned: bool = False
    expected_sha256: str = ""
    target_window: str = ""
    client_port: int = 0
    client_target: dict[str, Any] | None = None
    client_target_required: bool = False
    timeout: float = 10.0
    install_command: str = ""

    name: str = "remote-agent"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "RemoteAgentBackend":
        return cls.from_settings(Settings.from_env(env))

    @classmethod
    def from_settings(cls, settings: Settings) -> "RemoteAgentBackend":
        return cls(
            address=settings.host_agent,
            token=settings.host_agent_token,
            expected_version=settings.host_agent_expected_version or HOST_AGENT_VERSION,
            version_pinned=bool(settings.host_agent_expected_version),
            expected_sha256=settings.host_agent_expected_sha256,
            target_window=settings.host_agent_window,
            client_port=settings.host_agent_client_port or settings.client_port,
            timeout=settings.host_agent_timeout,
            install_command=host_agent_install_command(settings=settings),
        )

    def _installation_command(self) -> str:
        return self.install_command or host_agent_install_command()

    def _window_fields(
        self,
        window: str | None = None,
        *,
        handshake: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Window-targeting fields for a display primitive.

        The driven-client TPort is sent alongside as ``client_port``. When an
        active ``client_target`` exists, it is capability-gated and always sent
        for host-side lifecycle revalidation, including when ``window`` is an
        explicit selector hint. Active targeting never downgrades to a raw
        foreground/window selector.
        """
        selected = _explicit_window_selector(window if window is not None else self.target_window)
        fields: dict[str, Any] = {"window": selected}
        target = _validated_client_target(self.client_target)
        if self.client_target is not None and target is None:
            raise DisplayBackendError(
                "active-testclient-client-target-invalid",
                "active TestClient context has an invalid lifecycle/client display target",
            )
        if self.client_target_required:
            if target is None:
                raise DisplayBackendError(
                    "active-testclient-client-target-missing",
                    "active TestClient context has no lifecycle/client display target; refusing explicit, port or foreground fallback",
                )
            if not str(target.get("lifecycle_id") or "").strip():
                raise DisplayBackendError(
                    "active-testclient-client-target-invalid",
                    "active TestClient context has no immutable lifecycle id",
                )
        if target is not None:
            if not host_agent_testclient_window_target_supported(handshake):
                raise DisplayBackendError(
                    "host-agent-testclient-window-target-unsupported",
                    "host agent does not advertise lifecycle-bound TestClient window targeting support",
                    install_command=self._installation_command(),
                    payload=dict(handshake or {}),
                )
            fields["client_target"] = target
        if self.client_port > 0:
            fields["client_port"] = int(self.client_port)
        return fields

    @property
    def url(self) -> str:
        return _base_url(self.address, install_command=self._installation_command())

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        token: bool = True,
        accept: str = "application/json",
        timeout: float | None = None,
    ) -> tuple[bytes, str]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": accept}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if token and self.token:
            headers["X-QA-MCP-Agent-Token"] = self.token
        req = urllib.request.Request(f"{self.url}{path}", data=data, headers=headers, method=method)
        request_timeout = self.timeout if timeout is None else max(self.timeout, float(timeout))
        try:
            with urllib.request.urlopen(req, timeout=request_timeout) as resp:  # noqa: S310 - local lab agent URL.
                return resp.read(), resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            try:
                error_payload = json.loads(body)
            except json.JSONDecodeError:
                error_payload = None
            if isinstance(error_payload, dict) and error_payload.get("ok") is False:
                raise DisplayBackendError(
                    str(error_payload.get("error") or "host-agent-http-error"),
                    str(error_payload.get("detail") or error_payload.get("message") or body),
                    status=error_payload.get("status") if isinstance(error_payload.get("status"), int) else exc.code,
                    payload=error_payload,
                ) from exc
            detail = body or f"host agent returned HTTP {exc.code}"
            raise DisplayBackendError("host-agent-http-error", detail, status=exc.code) from exc
        except urllib.error.URLError as exc:
            raise DisplayBackendError(
                "host-agent-unreachable",
                "Windows host display agent is unreachable from the container.",
                install_command=self._installation_command(),
                cause=str(exc.reason),
            ) from exc

    def _json(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        token: bool = True,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        raw, _content_type = self._request(method, path, payload=payload, token=token, timeout=timeout)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise DisplayBackendError("host-agent-invalid-json", f"invalid host-agent JSON from {path}") from exc
        if isinstance(data, dict) and data.get("ok") is False:
            raise DisplayBackendError(
                str(data.get("error") or "host-agent-error"),
                str(data.get("detail") or data.get("message") or "host agent primitive failed"),
                status=data.get("status") if isinstance(data.get("status"), int) else None,
                payload=data,
            )
        return data if isinstance(data, dict) else {"value": data}

    def handshake(self) -> dict[str, Any]:
        data = self._json("GET", "/v1/capabilities", token=True)
        api = str(data.get("api") or "")
        api_major = data.get("api_major")
        api_major_is_int = type(api_major) is int
        if api != HOST_BRIDGE_API or not api_major_is_int or api_major != HOST_BRIDGE_API_MAJOR:
            code = (
                "host-agent-api-major-incompatible"
                if api_major_is_int
                else "host-agent-capability-document-invalid"
            )
            raise DisplayBackendError(
                code,
                f"host bridge API {api or '<missing>'} major {api_major!r} is not compatible "
                f"with {HOST_BRIDGE_API} major {HOST_BRIDGE_API_MAJOR}",
                install_command=self._installation_command(),
            )
        version = str(data.get("version") or "")
        display_protocol = str(data.get("display_protocol") or "")
        sha256 = str(data.get("sha256") or data.get("hash") or "").lower()
        capabilities = _normalize_host_agent_capabilities(data.get("capabilities"))
        advertised = set(capabilities or ()) if isinstance(capabilities, list) else {
            name for name, enabled in (capabilities or {}).items() if enabled
        }
        missing = sorted(HOST_BRIDGE_REQUIRED_CAPABILITIES - advertised)
        if missing:
            raise DisplayBackendError(
                "host-agent-capability-missing",
                "host bridge omits required standalone capabilities: " + ", ".join(missing),
                install_command=self._installation_command(),
            )
        relationship = host_agent_version_relationship(
            version,
            self.expected_version,
            display_protocol=display_protocol,
            version_pinned=self.version_pinned,
        )
        if relationship in {"incompatible", "protocol-incompatible"}:
            raise DisplayBackendError(
                "host-agent-version-mismatch",
                f"host agent version {version or '<missing>'} and display protocol "
                f"{display_protocol or '<missing>'} are not compatible with expected "
                f"{self.expected_version}",
                install_command=self._installation_command(),
            )
        if self.expected_sha256 and sha256 != self.expected_sha256:
            raise DisplayBackendError(
                "host-agent-hash-mismatch",
                f"host agent hash {sha256 or '<missing>'} does not match expected {self.expected_sha256}",
                install_command=self._installation_command(),
            )
        result: dict[str, Any] = {
            "ok": True,
            "api": api,
            "api_major": api_major,
            "version": version,
            "sha256": sha256,
            "display_protocol": display_protocol or None,
            "version_relationship": relationship,
            "backend": self.name,
        }
        if capabilities is not None:
            result["capabilities"] = capabilities
        return result

    def health(self) -> dict[str, Any]:
        data = self._json("GET", "/health", token=True)
        data["backend"] = self.name
        return data

    def _ensure_ready(self) -> dict[str, Any]:
        return self.handshake()

    def send_keys(
        self,
        keys: str | list[str],
        *,
        display: str = "",
        settle_sec: float = 0.15,
        window: str | None = None,
    ) -> dict[str, Any]:
        handshake = self._ensure_ready()
        seq = [keys] if isinstance(keys, str) else list(keys)
        result = self._json(
            "POST", "/send_keys",
            payload={"keys": seq, "settle_sec": settle_sec, **self._window_fields(window, handshake=handshake)},
        )
        result.setdefault("keys", seq)
        result["backend"] = self.name
        return result

    def type_text(
        self,
        text: str,
        *,
        display: str = "",
        delay_ms: int = 20,
        unicode: bool = True,
        window: str | None = None,
    ) -> dict[str, Any]:
        handshake = self._ensure_ready()
        result = self._json(
            "POST", "/type",
            payload={
                "text": text,
                "delay_ms": delay_ms,
                "unicode": unicode,
                **self._window_fields(window, handshake=handshake),
            },
        )
        result.setdefault("text_length", len(text))
        result["backend"] = self.name
        return result

    def click(
        self,
        x: int,
        y: int,
        *,
        display: str = "",
        button: int = 1,
        window: str | None = None,
    ) -> dict[str, Any]:
        handshake = self._ensure_ready()
        result = self._json(
            "POST", "/click",
            payload={
                "x": int(x),
                "y": int(y),
                "button": int(button),
                **self._window_fields(window, handshake=handshake),
            },
        )
        result["backend"] = self.name
        return result

    def double_click(
        self, x: int, y: int, *, display: str = "", button: int = 1, gap_ms: int = 120
    ) -> dict[str, Any]:
        first = self.click(x, y, display=display, button=button)
        if gap_ms:
            time.sleep(gap_ms / 1000)
        second = self.click(x, y, display=display, button=button)
        return {"first": first, "second": second, "double_clicked": True, "backend": self.name}

    def capture_screenshot(
        self,
        display: str,
        out_path: str | os.PathLike[str],
        *,
        window: str | None = None,
    ) -> dict[str, Any]:
        handshake = self._ensure_ready()
        raw, content_type = self._request(
            "POST",
            "/screenshot",
            payload={**self._window_fields(window, handshake=handshake), "display": display or ""},
            accept="image/png, application/json",
        )
        meta: dict[str, Any] = {}
        png = raw
        if "json" in content_type.lower() or not raw.startswith(PNG_MAGIC):
            data = json.loads(raw.decode("utf-8"))
            if data.get("ok") is False:
                raise DisplayBackendError(str(data.get("error") or "host-agent-screenshot-error"),
                                          str(data.get("detail") or "host agent screenshot failed"))
            meta = data
            encoded = data.get("png_base64") or data.get("png")
            if not encoded:
                raise DisplayBackendError("host-agent-screenshot-missing-png", "host agent returned no PNG data")
            png = base64.b64decode(encoded)
        if not png.startswith(PNG_MAGIC):
            raise DisplayBackendError("host-agent-invalid-png", "host agent screenshot response is not a PNG")
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png)
        return {
            "path": str(out),
            "display": display,
            "window": window,
            "size_bytes": len(png),
            "backend": self.name,
            **{k: v for k, v in meta.items() if k not in {"png", "png_base64"}},
        }

    def list_windows(self, display: str, *, geometry: bool = True) -> list[dict[str, Any]]:
        handshake = self._ensure_ready()
        data = self._json(
            "POST", "/window_list",
            payload={**self._window_fields(handshake=handshake), "geometry": bool(geometry)},
        )
        windows = data.get("windows", [])
        if not isinstance(windows, list):
            raise DisplayBackendError("host-agent-invalid-window-list", "host agent returned an invalid window list")
        return windows

    def visible_list_cells(self, *, window: str | None = None, limit: int = 120) -> dict[str, Any]:
        handshake = self._ensure_ready()
        result = self._json(
            "POST",
            "/uia/visible_list_cells",
            payload={**self._window_fields(window, handshake=handshake), "limit": int(limit)},
        )
        result["backend"] = self.name
        return result

    def launch_test_client(
        self,
        *,
        infobase_path: str | None = None,
        connection_string: str | None = None,
        user: str = "",
        password: str = "",
        platform_version: str = "",
        use_hardware_licenses: bool = False,
        port: int,
        timeout_seconds: float = 30.0,
    ) -> dict[str, Any]:
        self._ensure_ready()
        payload = {
            "infobase_path": infobase_path or "",
            "connection_string": connection_string or "",
            "user": user or "",
            "password": password or "",
            "platform_version": platform_version or "",
            "use_hardware_licenses": bool(use_hardware_licenses),
            "port": int(port),
            "timeout_seconds": float(timeout_seconds),
        }
        result = self._json(
            "POST",
            "/testclient/launch",
            payload=payload,
            timeout=float(timeout_seconds) + LAUNCH_HTTP_TIMEOUT_MARGIN,
        )
        result["backend"] = self.name
        return result

    def test_client_status(self, *, pid: int | None = None, port: int | None = None) -> dict[str, Any]:
        self._ensure_ready()
        result = self._json("POST", "/testclient/status", payload={
            "pid": int(pid) if pid is not None else 0,
            "port": int(port) if port is not None else 0,
        })
        result["backend"] = self.name
        return result

    def stop_test_client(
        self,
        *,
        pid: int,
        port: int | None = None,
        lifecycle_id: str | None = None,
        lifecycle_handle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        handshake = self.handshake()
        if not host_agent_testclient_lifecycle_stop_supported(handshake):
            version = str(handshake.get("version") or "")
            raise DisplayBackendError(
                "host-agent-testclient-lifecycle-unsupported",
                f"host agent version {version or '<missing>'} does not advertise lifecycle-handle TestClient stop support",
                install_command=self._installation_command(),
                payload=handshake,
            )
        payload: dict[str, Any] = {"pid": int(pid)}
        if port is not None:
            payload["port"] = int(port)
        if lifecycle_id:
            payload["lifecycle_id"] = str(lifecycle_id)
        if isinstance(lifecycle_handle, dict):
            payload["lifecycle_handle"] = dict(lifecycle_handle)
        result = self._json("POST", "/testclient/stop", payload=payload)
        result["backend"] = self.name
        return result


def get_display_backend(
    env: dict[str, str] | None = None,
    *,
    settings: Settings | None = None,
) -> LocalXTestBackend | RemoteAgentBackend:
    """Construct a backend from explicit Settings or the legacy environment adapter."""
    resolved = settings or Settings.from_env(env)
    if resolved.remote_client:
        return RemoteAgentBackend.from_settings(resolved)
    return LocalXTestBackend()


def unavailable_remote_result(
    tool: str,
    *,
    alt: str | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    detail = (
        f"{tool} is a display-bound tool; in model-B remote-client mode the client runs on the Windows host, "
        "not in this container's X server. Configure QA_MCP_HOST_AGENT to route the display primitive to the "
        "host-side input/screenshot agent."
    )
    if alt:
        detail += f" Protocol-surface alternative that works over TCP: {alt}."
    return {
        "ok": False,
        "error": "display-backend-unavailable-remote-client",
        "mode": "remote-client",
        "tool": tool,
        "detail": detail,
        "install_command": host_agent_install_command(settings=settings),
    }
