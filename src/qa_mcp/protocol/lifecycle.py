"""TestClient process lifecycle — launch / connect / status / teardown (card 84).

Productizes the proven `run_*_test.sh` boot logic into a Python API (+ MCP surface) so an agent can stand
up a 1C `/TESTCLIENT` itself — headless under Xvfb on Linux — instead of only connecting to one that is
already listening. No Vanessa Automation manager in the loop.

Lab notes baked in (see memory linux-native-testclient-xvfb):
  * thick client `1cv8 ENTERPRISE /IBConnectionString File="...";  /N<user> /TESTCLIENT -TPort N`,
  * wrapped in `xvfb-run -a` for a headless display,
  * optional apache2 stop/restart for the `vanessa_client` infobase (platform-version contention),
  * stale `1Cv8*.1CL` lock removal when no client is running (file infobase).
Secrets (the infobase password) come from the local `.ai1c/*.env` profile and are NEVER logged: the
redacted summary and every status dict omit it.
"""

from __future__ import annotations

import glob
import json
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import (
    Settings,
    TARGET_ENV_FILE_ENV,
    TESTCLIENT_LIBGCC_PRELOAD_ENV,
    active_application_settings,
)
from ..versioning import DEFAULT_PLATFORM_ROOT
from .session import TestClientSession, timestamp_name
from .transport import connect_testclient, relay_configuration, relay_listener_reachable

DEFAULT_ENV_FILE = os.environ.get(TARGET_ENV_FILE_ENV, ".ai1c/vanessa-qa-mcp.env")
SYSTEM_LIBGCC_CANDIDATES = (
    "/lib/x86_64-linux-gnu/libgcc_s.so.1",
    "/usr/lib/x86_64-linux-gnu/libgcc_s.so.1",
)
SOFTWARE_RENDERING_DEFAULTS = {
    "LIBGL_ALWAYS_SOFTWARE": "1",
    "GALLIUM_DRIVER": "softpipe",
}
OWNERSHIP_MARKER_NAME = "qa-mcp-owned-process.json"
OWNERSHIP_MARKER_SCHEMA = "qa-mcp.testclient.ownership.v1"
DEFAULT_OWNERSHIP_ROOT = Path(__file__).resolve().parents[3] / "runtime/protocol-research/testclient-lifecycle"


def load_env_file(path: str | os.PathLike[str] | None) -> dict[str, str]:
    """Parse a ``KEY=VALUE`` .env profile as UTF-8 (Cyrillic-safe). Surrounding quotes are stripped;
    blank lines and ``#`` comments are ignored. Missing file -> empty dict (caller falls back to defaults)."""
    env: dict[str, str] = {}
    if not path:
        return env
    p = Path(path)
    if not p.is_file():
        return env
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[key.strip()] = value
    return env


def require_target_infobase(
    env_file: str | os.PathLike[str] | None,
    expected_substring: str,
    *,
    purpose: str = "operation",
) -> str:
    """Fail closed unless the infobase resolved from ``env_file`` matches ``expected_substring``.

    card 125: a mutating create/proof run must not silently default to the wrong infobase (the
    invalid predecessor proof ran on the retired ``/opt/1c-dev/vanessa_client`` because it used the
    stale ``DEFAULT_ENV_FILE``). Callers pass an explicit env and the expected target; a mismatch
    (or a missing ``INFOBASE_PATH``) raises instead of running on the wrong base. Returns the
    resolved ``INFOBASE_PATH`` on success."""
    env = load_env_file(env_file)
    infobase = env.get("INFOBASE_PATH", "").strip()
    if not infobase:
        raise ValueError(
            f"target guard: no INFOBASE_PATH resolved from env {str(env_file)!r} — refusing {purpose}")
    if expected_substring not in infobase:
        raise ValueError(
            f"target guard: resolved infobase {infobase!r} does not contain expected "
            f"{expected_substring!r} — refusing {purpose} on the wrong infobase")
    return infobase


@dataclass(frozen=True)
class TestClientLaunchEnvironment:
    """Child process environment plus bounded, non-secret metadata for status/diagnostics."""

    env: dict[str, str]
    libgcc_preload: str | None
    libgcc_preload_source: str
    software_rendering: dict[str, str]

    def status(self) -> dict[str, Any]:
        return {
            "libgcc_preload": self.libgcc_preload,
            "libgcc_preload_source": self.libgcc_preload_source,
            "software_rendering": dict(self.software_rendering),
        }


def _first_existing(paths: tuple[str, ...] | list[str]) -> str | None:
    for candidate in paths:
        if Path(candidate).exists():
            return str(candidate)
    return None


def resolve_testclient_launch_environment(
    *,
    base_env: dict[str, str] | None = None,
    display: str | None = None,
    candidate_paths: tuple[str, ...] | list[str] = SYSTEM_LIBGCC_CANDIDATES,
) -> TestClientLaunchEnvironment:
    """Return the child env for native TestClient launch without mutating ``os.environ``.

    ``QA_MCP_TESTCLIENT_LIBGCC_PRELOAD`` mirrors the suite platform-launcher knob:
    unset -> autodetect a system libgcc; empty -> opt out; non-empty -> explicit value.
    """
    env = dict(os.environ if base_env is None else base_env)
    preload_source = "not_found"
    preload = None
    if TESTCLIENT_LIBGCC_PRELOAD_ENV in env:
        configured = env.get(TESTCLIENT_LIBGCC_PRELOAD_ENV, "")
        if configured:
            preload = configured
            preload_source = "override"
        else:
            preload_source = "disabled"
    else:
        preload = _first_existing(candidate_paths)
        preload_source = "autodetected" if preload else "not_found"

    if preload:
        existing = env.get("LD_PRELOAD", "")
        env["LD_PRELOAD"] = f"{preload}:{existing}" if existing else preload
    # Headless 1C clients run under Xvfb in the Linux lab. Older 8.3.27 builds can
    # crash in Mesa's LLVM-backed renderer there; softpipe is slower but stable and
    # still operator-overridable through the process environment.
    for key, value in SOFTWARE_RENDERING_DEFAULTS.items():
        env.setdefault(key, value)
    if display is not None:
        env["DISPLAY"] = display
    return TestClientLaunchEnvironment(
        env=env,
        libgcc_preload=preload,
        libgcc_preload_source=preload_source,
        software_rendering={key: env.get(key, "") for key in SOFTWARE_RENDERING_DEFAULTS},
    )


@dataclass
class TestClientTarget:
    """Descriptor for a TestClient to launch. File infobase first (the lab pattern); ``connection_string``
    overrides for server infobases. ``password`` is sensitive and is never echoed back."""

    __test__ = False  # not a pytest test class

    infobase_path: str | None = None
    connection_string: str | None = None
    platform_root: str = DEFAULT_PLATFORM_ROOT
    client_bin: str | None = None  # explicit override; else derived from platform_root + kind
    kind: str = "thick"  # thick -> 1cv8, thin -> 1cv8c
    user: str = "Администратор"
    password: str = ""
    host: str = "127.0.0.1"
    port: int = 15381
    headless: bool = True  # wrap with `xvfb-run -a` (only when display is None)
    display: str | None = None  # ":N" -> OWN an Xvfb on this display (card 85: screenshot-capable, persists
    #                              independently of the client); "auto" -> pick a free one; None -> xvfb-run -a
    screen_geometry: str = "1280x1024x24"  # Xvfb -screen 0 <geometry> when owning the display
    manage_apache: bool = False  # stop apache2 before boot + restart on teardown (vanessa_client contention)
    clear_lock: bool = True  # remove stale 1Cv8*.1CL if no client is running (file infobase)
    extra_args: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None, **overrides: Any) -> "TestClientTarget":
        """Build a target from a loaded env profile (INFOBASE_PATH / CONNECTION_STRING / PLATFORM_ROOT /
        TEST_CLIENT_KIND / TEST_CLIENT_USER / TEST_CLIENT_PASSWORD), falling back to the process environment
        (so a Docker container can pass everything via ``-e`` with no env file), then apply explicit
        ``overrides`` (which win, but only when not None). Precedence: overrides > env profile > os.environ."""
        env = env or {}

        def pick(key: str) -> str | None:
            return env.get(key) or os.environ.get(key) or None

        kind = pick("TEST_CLIENT_KIND") or "thick"
        base = dict(
            infobase_path=pick("INFOBASE_PATH"),
            connection_string=pick("CONNECTION_STRING"),
            platform_root=pick("PLATFORM_ROOT") or DEFAULT_PLATFORM_ROOT,
            kind="thin" if str(kind).lower().startswith("thin") else "thick",
            user=pick("TEST_CLIENT_USER") or "Администратор",
            password=pick("TEST_CLIENT_PASSWORD") or "",
        )
        base.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**base)

    def resolved_client_bin(self) -> str:
        if self.client_bin:
            return self.client_bin
        binary = "1cv8c" if self.kind == "thin" else "1cv8"
        return str(Path(self.platform_root) / binary)

    def connection_string_value(self) -> str:
        if self.connection_string:
            return self.connection_string
        if self.infobase_path:
            # literal inner quotes around the path, matching the proven boot scripts
            return f'File="{self.infobase_path}";'
        raise ValueError("TestClientTarget needs infobase_path or connection_string")

    def build_argv(self, out_dir: Path | None = None) -> list[str]:
        argv: list[str] = [
            self.resolved_client_bin(), "ENTERPRISE",
            "/IBConnectionString", self.connection_string_value(),
        ]
        if self.user:
            argv.append(f"/N{self.user}")
        if self.password:
            argv.append(f"/P{self.password}")
        argv += ["/TESTCLIENT", "-TPort", str(self.port),
                 "/DisableStartupDialogs", "/DisableStartupMessages"]
        if out_dir is not None:
            argv += ["/Out", str(out_dir / "testclient.out"), "-NoTruncate"]
        argv += list(self.extra_args)
        # When we OWN the display (card 85) the client inherits DISPLAY=:N via env — no xvfb-run wrapper.
        # Only the legacy auto path wraps with xvfb-run -a.
        if self.display is None and self.headless:
            argv = ["xvfb-run", "-a"] + argv
        return argv

    def redacted_summary(self) -> dict[str, Any]:
        """Connection summary safe to return over MCP / log: target identity WITHOUT the password."""
        target = self.connection_string or (f'File="{self.infobase_path}"' if self.infobase_path else None)
        return {
            "host": self.host,
            "port": self.port,
            "kind": self.kind,
            "user": self.user or None,
            "target": target,
            "headless": self.headless,
            "display": self.display,
            "password_set": bool(self.password),
        }


def _port_open(host: str, port: int, timeout_sec: float = 0.5) -> bool:
    address = (host, port)
    relay = relay_configuration()
    if relay is not None and address == relay[0]:
        return relay_listener_reachable(address, timeout=timeout_sec)
    try:
        with connect_testclient(address, timeout=timeout_sec):
            return True
    except OSError:
        return False


def _wait_for_port(host: str, port: int, timeout_sec: float, interval_sec: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _port_open(host, port, timeout_sec=min(0.5, interval_sec)):
            return True
        time.sleep(interval_sec)
    return _port_open(host, port, timeout_sec=0.5)


def _wait_for_process_stability(
    proc: subprocess.Popen[Any],
    timeout_sec: float,
    interval_sec: float = 0.2,
) -> bool:
    """Require the owned launcher process to remain alive for a bounded stability window."""
    deadline = time.monotonic() + max(timeout_sec, 0.0)
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False
        time.sleep(min(interval_sec, max(deadline - time.monotonic(), 0.0)))
    return proc.poll() is None


DEFAULT_READINESS_STABILITY_SEC = 20.0


def port_is_listening(host: str, port: int, timeout_sec: float = 0.5) -> bool:
    """Public: is something accepting TCP connections at host:port (i.e. the TestClient TPort is up)?"""
    return _port_open(host, port, timeout_sec=timeout_sec)


def _x_socket(display: str) -> Path:
    return Path("/tmp/.X11-unix") / ("X" + display.lstrip(":"))


def display_in_use(display: str) -> bool:
    """A display number is taken if its X socket OR its server lock file exists."""
    num = display.lstrip(":")
    return _x_socket(display).exists() or Path(f"/tmp/.X{num}-lock").exists()


def pick_free_display(start: int = 101, limit: int = 64) -> str:
    """Return the first free ``:N`` display from ``start`` (skips numbers with an X socket / lock file)."""
    for num in range(start, start + limit):
        if not display_in_use(f":{num}"):
            return f":{num}"
    raise RuntimeError(f"no free X display in :{start}..:{start + limit}")


def _start_xvfb(display: str, geometry: str, out_dir: Path | None) -> int:
    """Launch our OWN Xvfb on ``display`` and wait for its socket. Returns the Xvfb pid (process-group
    leader). The display then persists independently of the TestClient — so a post-crash screenshot still
    works (card 85). Raises if the display is busy or Xvfb fails to come up."""
    if display_in_use(display):
        raise RuntimeError(f"display {display} is already in use (X socket / lock present)")
    argv = ["Xvfb", display, "-screen", "0", geometry, "-nolisten", "tcp"]
    log = open(out_dir / "xvfb.out", "w") if out_dir is not None else subprocess.DEVNULL
    try:
        proc = subprocess.Popen(  # noqa: S603 — argv is fixed except validated display/geometry
            argv, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True
        )
    finally:
        if out_dir is not None and hasattr(log, "close"):
            log.close()
    socket_path = _x_socket(display)
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        if socket_path.exists():
            return proc.pid
        if proc.poll() is not None:
            raise RuntimeError(f"Xvfb for {display} exited early (rc={proc.returncode})")
        time.sleep(0.1)
    _terminate_group(proc.pid, kill_after_sec=2.0)
    raise TimeoutError(f"Xvfb display {display} did not come up within 15s")


def _tail_text(path: Path, *, max_lines: int = 20, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lines = text.splitlines()[-max_lines:]
    tail = "\n".join(lines)
    if len(tail) > max_chars:
        tail = tail[-max_chars:]
    return tail


def _sanitize_diagnostic(text: str, target: TestClientTarget) -> str:
    if target.password:
        text = text.replace(target.password, "<redacted-password>")
    return text


def _launch_timeout_message(
    target: TestClientTarget,
    *,
    wait_sec: float,
    out_dir: Path | None,
    returncode: int | None,
) -> str:
    parts = [
        f"TestClient TPort {target.port} did not start listening within {wait_sec:.0f}s",
    ]
    if returncode is not None:
        parts.append(f"process return code: {returncode}")
    if out_dir is not None:
        parts.append(f"output directory: {out_dir}")
        for name in ("client.out", "testclient.out"):
            tail = _tail_text(out_dir / name)
            if tail:
                parts.append(f"{name} tail:\n{_sanitize_diagnostic(tail, target)}")
    return "\n".join(parts)


def _launch_readiness_message(
    target: TestClientTarget,
    *,
    phase: str,
    detail: str,
    out_dir: Path | None,
    returncode: int | None,
) -> str:
    parts = [
        f"TestClient TPort {target.port} did not remain ready after becoming connectable",
        f"readiness phase: {phase}",
        f"detail: {_sanitize_diagnostic(detail, target)}",
    ]
    if returncode is not None:
        parts.append(f"process return code: {returncode}")
    if out_dir is not None:
        parts.append(f"output directory: {out_dir}")
        for name in ("client.out", "testclient.out"):
            tail = _tail_text(out_dir / name)
            if tail:
                parts.append(f"{name} tail:\n{_sanitize_diagnostic(tail, target)}")
    return "\n".join(parts)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def pid_is_alive(pid: int) -> bool:
    """Public: is the process with this PID still alive?"""
    return _pid_alive(pid)


def _any_client_running() -> bool:
    try:
        return subprocess.run(["pgrep", "-x", "1cv8"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def _clear_locks(infobase_path: str) -> list[str]:
    removed: list[str] = []
    for lock in glob.glob(str(Path(infobase_path) / "1Cv8*.1CL")):
        try:
            os.remove(lock)
            removed.append(lock)
        except OSError:
            pass
    return removed


def _systemctl(action: str, unit: str = "apache2") -> bool:
    try:
        return subprocess.run(
            ["sudo", "-n", "systemctl", action, unit], capture_output=True
        ).returncode == 0
    except FileNotFoundError:
        return False


@dataclass
class TestClientProcess:
    """Handle for a launched TestClient. ``pid`` is the launcher (process-group leader); teardown signals
    the whole group, so Xvfb + 1cv8 go down together."""

    __test__ = False  # not a pytest test class

    target: TestClientTarget
    pid: int | None
    argv: list[str]
    listening: bool
    out_dir: Path | None = None
    apache_stopped: bool = False
    display: str | None = None  # owned-Xvfb display (card 85), if any
    xvfb_pid: int | None = None  # the Xvfb process we own for `display`, if any
    locks_cleared: list[str] = field(default_factory=list)
    owns_process: bool = True
    attached: bool = False
    launch_environment: TestClientLaunchEnvironment | None = None
    ownership_record_path: str | None = None

    def is_alive(self) -> bool:
        return _pid_alive(self.pid) if self.pid is not None else False

    def is_listening(self, timeout_sec: float = 0.5) -> bool:
        return _port_open(self.target.host, self.target.port, timeout_sec=timeout_sec)

    def status(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "alive": self.is_alive() if self.pid is not None else None,
            "listening": self.is_listening(),
            "display": self.display,
            "xvfb_pid": self.xvfb_pid,
            "owns_process": self.owns_process,
            "attached": self.attached,
            "launch_environment": self.launch_environment.status() if self.launch_environment else None,
            "connection": self.target.redacted_summary(),
            "out_dir": str(self.out_dir) if self.out_dir else None,
            "ownership_record_path": self.ownership_record_path,
            "apache_stopped": self.apache_stopped,
        }

    def connect(self, **session_kwargs: Any) -> TestClientSession:
        """Return a (not-yet-entered) TestClientSession bound to this client's host/port."""
        return TestClientSession(host=self.target.host, port=self.target.port, **session_kwargs)

    def stop(self, *, kill_after_sec: float = 5.0, restore_apache: bool | None = None) -> dict[str, Any]:
        if not self.owns_process:
            return {
                "stopped": False,
                "pid": self.pid,
                "xvfb_pid": self.xvfb_pid,
                "xvfb_stopped": False,
                "apache_restored": False,
                "still_listening": self.is_listening(),
                "attached": self.attached,
                "owns_process": self.owns_process,
                "reason": "external TestClient is not owned by qa-mcp",
            }
        return stop_test_client(self, kill_after_sec=kill_after_sec, restore_apache=restore_apache)

    def __enter__(self) -> "TestClientProcess":
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()


def launch_test_client(
    target: TestClientTarget,
    *,
    wait_sec: float = 90.0,
    settle_sec: float = DEFAULT_READINESS_STABILITY_SEC,
    out_dir: Path | None = None,
) -> TestClientProcess:
    """Launch a TestClient for ``target``, wait up to ``wait_sec`` for its TPort to listen, and return a
    handle. The child is started in a NEW SESSION (own process group) and OUTLIVES this call — connect/stop
    happen in later calls (the MCP-server stateless pattern). Raises TimeoutError if the port never opens."""
    if _port_open(target.host, target.port, timeout_sec=0.5):
        raise RuntimeError(
            f"TestClient TPort {target.host}:{target.port} is already listening; "
            "attach to the existing endpoint or stop its owned lifecycle before launching another client"
        )

    apache_stopped = False
    if target.manage_apache:
        apache_stopped = _systemctl("stop", "apache2")
    locks_cleared: list[str] = []
    if target.clear_lock and target.infobase_path and not target.connection_string and not _any_client_running():
        locks_cleared = _clear_locks(target.infobase_path)

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    # Card 85: if a display is requested, OWN an Xvfb on it and run the client with DISPLAY=:N (env), so the
    # display persists for screenshots independently of the client. "auto" -> pick the first free display.
    xvfb_pid: int | None = None
    if target.display is not None:
        if target.display == "auto":
            target.display = pick_free_display()
        try:
            xvfb_pid = _start_xvfb(target.display, target.screen_geometry, out_dir)
        except Exception:
            if apache_stopped:
                _systemctl("start", "apache2")
            raise

    argv = target.build_argv(out_dir=out_dir)
    launch_env = resolve_testclient_launch_environment(display=target.display)
    stdout = open(out_dir / "client.out", "w") if out_dir is not None else subprocess.DEVNULL
    try:
        proc = subprocess.Popen(  # noqa: S603 — argv is constructed from a validated target descriptor
            argv,
            stdout=stdout,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            env=launch_env.env,
        )
    finally:
        if out_dir is not None and hasattr(stdout, "close"):
            stdout.close()

    handle = TestClientProcess(
        target=target, pid=proc.pid, argv=argv, listening=False,
        out_dir=out_dir, apache_stopped=apache_stopped, display=target.display,
        xvfb_pid=xvfb_pid, locks_cleared=locks_cleared, launch_environment=launch_env,
    )
    try:
        # Persist process identity before the bounded wait. If the MCP caller disconnects
        # during startup, stateless cleanup can still prove ownership of the orphaned group.
        handle.ownership_record_path = _write_ownership_marker(handle)
    except Exception:
        stop_test_client(handle, restore_apache=apache_stopped)
        raise

    listening = _wait_for_port(target.host, target.port, timeout_sec=wait_sec)
    handle.listening = listening
    if not listening:
        returncode = proc.poll()
        # tear the half-started client (and our Xvfb) down before surfacing the failure — never leak a process
        stop_test_client(handle, restore_apache=apache_stopped)
        raise TimeoutError(
            _launch_timeout_message(target, wait_sec=wait_sec, out_dir=out_dir, returncode=returncode)
        )

    readiness_phase = "process_stability"
    readiness_detail = ""
    if not _wait_for_process_stability(proc, settle_sec):
        readiness_detail = (
            f"TestClient process exited during the {max(settle_sec, 0.0):.1f}s "
            "post-listener stability window."
        )
    if not readiness_detail and not _port_open(target.host, target.port, timeout_sec=0.5):
        readiness_phase = "listener_stability"
        readiness_detail = "TestClient TPort stopped accepting connections after initial listener readiness."
    if readiness_detail:
        returncode = proc.poll()
        stop_test_client(handle, restore_apache=apache_stopped)
        raise TimeoutError(
            _launch_readiness_message(
                target,
                phase=readiness_phase,
                detail=readiness_detail,
                out_dir=out_dir,
                returncode=returncode,
            )
        )
    return handle


def attach_test_client(
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    connect_timeout_sec: float = 0.5,
) -> TestClientProcess:
    """Attach to an already-listening TestClient endpoint without taking process ownership."""
    target = TestClientTarget(
        host=host,
        port=port,
        headless=False,
        clear_lock=False,
    )
    if not _port_open(host, port, timeout_sec=connect_timeout_sec):
        raise ConnectionError(f"TestClient TPort {host}:{port} is not listening; attach owns no process to clean up")
    return TestClientProcess(
        target=target,
        pid=None,
        argv=[],
        listening=True,
        owns_process=False,
        attached=True,
    )


def _reap(pid: int) -> None:
    """If ``pid`` is a child of THIS process, reap it so it doesn't linger as a zombie (a zombie still
    answers os.kill(pid, 0), so without this an in-process teardown would think the client is still alive).
    A no-op (ignored error) when pid is not our child — the normal MCP case where stop runs in a later call."""
    try:
        os.waitpid(pid, os.WNOHANG)
    except (ChildProcessError, OSError):
        pass


def _proc_comm(pid: int) -> str | None:
    try:
        return Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip()
    except (FileNotFoundError, ProcessLookupError):
        return None
    except OSError:
        return None


def _proc_start_ticks(pid: int) -> str | None:
    """Return Linux `/proc/<pid>/stat` starttime ticks (field 22), or None when unreadable."""
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except (FileNotFoundError, ProcessLookupError, OSError):
        return None
    try:
        rest = text.rsplit(")", 1)[1].strip().split()
    except IndexError:
        return None
    return rest[19] if len(rest) > 19 else None


def _proc_pgid(pid: int) -> int | None:
    try:
        return os.getpgid(pid)
    except (ProcessLookupError, OSError):
        return None


def _ownership_root() -> Path:
    # Factory calls activate their immutable Settings.  An active empty value
    # deliberately selects the documented static fallback rather than the
    # ambient process configuration; direct low-level calls retain that legacy
    # environment adapter.
    settings = active_application_settings() or Settings.from_env()
    if settings.testclient_ownership_root:
        return Path(settings.testclient_ownership_root)
    if settings.home:
        return Path(settings.home) / "runtime/protocol-research/testclient-lifecycle"
    return DEFAULT_OWNERSHIP_ROOT


def ownership_root() -> Path:
    """Return the effective marker/output root for the current call scope."""

    return _ownership_root()


def _ownership_marker_path(out_dir: Path) -> Path:
    return out_dir / OWNERSHIP_MARKER_NAME


def _process_identity_record(pid: int | None) -> dict[str, Any] | None:
    if pid is None:
        return None
    return {
        "pid": pid,
        "comm": _proc_comm(pid),
        "pgid": _proc_pgid(pid),
        "start_ticks": _proc_start_ticks(pid),
    }


def _write_ownership_marker(proc: TestClientProcess) -> str | None:
    """Persist proof that this stateless MCP process may later stop the launched process group."""
    if proc.out_dir is None or proc.pid is None or not proc.owns_process:
        return None
    proc.out_dir.mkdir(parents=True, exist_ok=True)
    marker = _ownership_marker_path(proc.out_dir)
    client_identity = _process_identity_record(proc.pid) or {}
    xvfb_identity = _process_identity_record(proc.xvfb_pid) if proc.xvfb_pid is not None else None
    if not client_identity.get("start_ticks") or client_identity.get("pgid") is None:
        raise RuntimeError(f"cannot record qa-mcp ownership for pid {proc.pid}: missing start_ticks/pgid")
    if proc.xvfb_pid is not None and (
        not xvfb_identity
        or not xvfb_identity.get("start_ticks")
        or xvfb_identity.get("pgid") is None
    ):
        raise RuntimeError(f"cannot record qa-mcp ownership for Xvfb pid {proc.xvfb_pid}: missing start_ticks/pgid")
    record = {
        "schema": OWNERSHIP_MARKER_SCHEMA,
        "created_at": time.time(),
        "out_dir": str(proc.out_dir),
        "host": proc.target.host,
        "port": proc.target.port,
        "pid": proc.pid,
        "process_comm": client_identity.get("comm"),
        "process_pgid": client_identity.get("pgid"),
        "process_start_ticks": client_identity.get("start_ticks"),
        "xvfb_pid": proc.xvfb_pid,
        "xvfb_comm": xvfb_identity.get("comm") if xvfb_identity else None,
        "xvfb_pgid": xvfb_identity.get("pgid") if xvfb_identity else None,
        "xvfb_start_ticks": xvfb_identity.get("start_ticks") if xvfb_identity else None,
    }
    tmp = marker.with_suffix(marker.suffix + ".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(marker)
    return str(marker)


def _read_ownership_record(path: Path) -> dict[str, Any] | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict) or record.get("schema") != OWNERSHIP_MARKER_SCHEMA:
        return None
    record["_marker_path"] = str(path)
    return record


def _find_ownership_record(pid: int) -> dict[str, Any] | None:
    root = _ownership_root()
    candidates = list(root.glob(f"*/{OWNERSHIP_MARKER_NAME}"))
    direct = root / OWNERSHIP_MARKER_NAME
    if direct.exists():
        candidates.append(direct)
    records = [record for path in candidates if (record := _read_ownership_record(path))]
    matches = [record for record in records if record.get("pid") == pid]
    if not matches:
        return None
    return max(matches, key=lambda record: float(record.get("created_at") or 0))


def _remove_ownership_record(record: dict[str, Any] | None) -> None:
    if not record:
        return
    marker_path = record.get("_marker_path")
    if not marker_path:
        return
    try:
        Path(str(marker_path)).unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _owned_process_identity(
    pid: int,
    *,
    record: dict[str, Any] | None,
    expect_xvfb: bool = False,
) -> dict[str, Any]:
    if pid <= 0:
        return {"ok": False, "pid": pid, "comm": None, "reason": "invalid_pid"}
    comm = _proc_comm(pid)
    if not comm:
        return {"ok": False, "pid": pid, "comm": comm, "reason": "stale_or_unreadable_pid"}
    if expect_xvfb and comm != "Xvfb":
        return {"ok": False, "pid": pid, "comm": comm, "reason": "unrecognized_process"}
    if record is None:
        known_testclient = comm.startswith("1cv8") or comm == "Xvfb"
        return {
            "ok": False,
            "pid": pid,
            "comm": comm,
            "reason": "not_qa_mcp_owned" if known_testclient else "unrecognized_process",
        }

    prefix = "xvfb_" if expect_xvfb else "process_"
    expected_pid = record.get("xvfb_pid") if expect_xvfb else record.get("pid")
    if expected_pid != pid:
        return {"ok": False, "pid": pid, "comm": comm, "reason": "ownership_pid_mismatch"}

    expected_start = record.get(f"{prefix}start_ticks")
    actual_start = _proc_start_ticks(pid)
    if not expected_start or not actual_start or str(expected_start) != str(actual_start):
        return {"ok": False, "pid": pid, "comm": comm, "reason": "ownership_start_mismatch"}

    expected_pgid = record.get(f"{prefix}pgid")
    actual_pgid = _proc_pgid(pid)
    if expected_pgid is None or actual_pgid is None or int(expected_pgid) != int(actual_pgid):
        return {"ok": False, "pid": pid, "comm": comm, "reason": "ownership_group_mismatch"}

    return {
        "ok": True,
        "pid": pid,
        "comm": comm,
        "reason": None,
        "ownership_record_path": record.get("_marker_path"),
    }


def _stop_refusal(
    *,
    pid: int,
    xvfb_pid: int | None,
    identity: dict[str, Any],
    apache_restored: bool = False,
) -> dict[str, Any]:
    return {
        "stopped": False,
        "pid": pid,
        "xvfb_pid": xvfb_pid,
        "xvfb_stopped": False,
        "apache_restored": apache_restored,
        "refused": True,
        "reason": identity["reason"],
        "process_comm": identity["comm"],
        "process_pid": identity["pid"],
    }


def _terminate_group(pid: int, *, kill_after_sec: float) -> bool:
    """SIGTERM the process group, wait, SIGKILL if still alive. Returns True if the pid is gone afterward."""
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        _reap(pid)
        return True
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        _reap(pid)
        return True
    deadline = time.monotonic() + kill_after_sec
    while time.monotonic() < deadline:
        _reap(pid)
        if not _pid_alive(pid):
            return True
        time.sleep(0.2)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        _reap(pid)
        return True
    time.sleep(0.3)
    _reap(pid)
    return not _pid_alive(pid)


def stop_test_client(
    proc: TestClientProcess,
    *,
    kill_after_sec: float = 5.0,
    restore_apache: bool | None = None,
) -> dict[str, Any]:
    """Tear down a launched client: signal the client's process group and, if we own an Xvfb for its
    display, that group too; then, if apache was stopped for it, restart apache2. ``restore_apache``
    defaults to the handle's ``apache_stopped`` flag."""
    if not proc.owns_process or proc.pid is None:
        return {
            "stopped": False,
            "pid": proc.pid,
            "xvfb_pid": proc.xvfb_pid,
            "xvfb_stopped": False,
            "still_listening": proc.is_listening(),
            "apache_restored": False,
            "attached": proc.attached,
            "owns_process": proc.owns_process,
            "reason": "external TestClient is not owned by qa-mcp",
        }
    terminated = _terminate_group(proc.pid, kill_after_sec=kill_after_sec)
    xvfb_stopped = _terminate_group(proc.xvfb_pid, kill_after_sec=kill_after_sec) if proc.xvfb_pid else None
    want_apache = proc.apache_stopped if restore_apache is None else restore_apache
    apache_restored = _systemctl("start", "apache2") if want_apache else False
    if terminated and (proc.xvfb_pid is None or xvfb_stopped):
        _remove_ownership_record(
            _read_ownership_record(Path(proc.ownership_record_path)) if proc.ownership_record_path else None
        )
    return {
        "stopped": terminated,
        "pid": proc.pid,
        "xvfb_pid": proc.xvfb_pid,
        "xvfb_stopped": xvfb_stopped,
        "still_listening": proc.is_listening(),
        "apache_restored": apache_restored,
    }


def stop_by_pid(
    pid: int,
    *,
    xvfb_pid: int | None = None,
    kill_after_sec: float = 5.0,
    restore_apache: bool = False,
) -> dict[str, Any]:
    """Stateless teardown by PID (for the MCP `stop_test_client` tool, which holds no handle across calls).
    Pass ``xvfb_pid`` (from launch status) to also tear down an owned Xvfb display."""
    record = _find_ownership_record(pid)
    if xvfb_pid is None and record is not None:
        xvfb_pid = record.get("xvfb_pid")
    identity = _owned_process_identity(pid, record=record)
    if not identity["ok"]:
        if identity["reason"] == "stale_or_unreadable_pid" and record is not None:
            xvfb_identity: dict[str, Any] | None = None
            xvfb_already_exited = False
            xvfb_stopped: bool | None = None
            if xvfb_pid is not None:
                xvfb_identity = _owned_process_identity(xvfb_pid, record=record, expect_xvfb=True)
                if not xvfb_identity["ok"]:
                    if xvfb_identity["reason"] != "stale_or_unreadable_pid":
                        apache_restored = _systemctl("start", "apache2") if restore_apache else False
                        return _stop_refusal(
                            pid=pid,
                            xvfb_pid=xvfb_pid,
                            identity=xvfb_identity,
                            apache_restored=apache_restored,
                        )
                    xvfb_already_exited = True
                    xvfb_stopped = True
                else:
                    xvfb_stopped = _terminate_group(xvfb_pid, kill_after_sec=kill_after_sec)
            apache_restored = _systemctl("start", "apache2") if restore_apache else False
            cleaned = xvfb_pid is None or bool(xvfb_stopped)
            if cleaned:
                _remove_ownership_record(record)
            return {
                "stopped": cleaned,
                "pid": pid,
                "client_already_exited": True,
                "xvfb_pid": xvfb_pid,
                "xvfb_stopped": xvfb_stopped,
                "xvfb_already_exited": xvfb_already_exited,
                "apache_restored": apache_restored,
                "refused": False,
                "process_comm": record.get("process_comm"),
                "xvfb_comm": xvfb_identity.get("comm") if xvfb_identity else None,
                "ownership_record_path": record.get("_marker_path"),
            }
        apache_restored = _systemctl("start", "apache2") if restore_apache else False
        return _stop_refusal(pid=pid, xvfb_pid=xvfb_pid, identity=identity, apache_restored=apache_restored)
    xvfb_identity: dict[str, Any] | None = None
    if xvfb_pid is not None:
        xvfb_identity = _owned_process_identity(xvfb_pid, record=record, expect_xvfb=True)
        if not xvfb_identity["ok"]:
            apache_restored = _systemctl("start", "apache2") if restore_apache else False
            return _stop_refusal(
                pid=pid, xvfb_pid=xvfb_pid, identity=xvfb_identity, apache_restored=apache_restored)
    terminated = _terminate_group(pid, kill_after_sec=kill_after_sec)
    xvfb_stopped = _terminate_group(xvfb_pid, kill_after_sec=kill_after_sec) if xvfb_pid else None
    apache_restored = _systemctl("start", "apache2") if restore_apache else False
    if terminated and (xvfb_pid is None or xvfb_stopped):
        _remove_ownership_record(record)
    return {
        "stopped": terminated, "pid": pid, "xvfb_pid": xvfb_pid,
        "xvfb_stopped": xvfb_stopped, "apache_restored": apache_restored,
        "refused": False, "process_comm": identity["comm"],
        "xvfb_comm": xvfb_identity["comm"] if xvfb_identity else None,
        "ownership_record_path": identity.get("ownership_record_path"),
    }


def ensure_test_client(
    *,
    env_file: str | os.PathLike[str] | None = DEFAULT_ENV_FILE,
    out_dir: Path | None = None,
    wait_sec: float = 90.0,
    settle_sec: float = DEFAULT_READINESS_STABILITY_SEC,
    **overrides: Any,
) -> TestClientProcess:
    """Convenience: load the env profile, build a target (overrides win), and launch. Used by the MCP tool."""
    target = TestClientTarget.from_env(load_env_file(env_file), **overrides)
    if out_dir is None:
        out_dir = Path("runtime/protocol-research/testclient-lifecycle") / timestamp_name()
    return launch_test_client(target, wait_sec=wait_sec, settle_sec=settle_sec, out_dir=out_dir)
