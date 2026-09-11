"""Card 84: TestClient lifecycle — offline tests for the env/target/argv/status logic.

No real 1C client is launched here; live boot/teardown is exercised by
tools/protocol-research/run_lifecycle_test.sh.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tests.support.runtime_targets import TargetProfileInputs

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol import lifecycle  # noqa: E402
from qa_mcp.protocol.lifecycle import TestClientTarget, load_env_file  # noqa: E402
from qa_mcp.config import Settings  # noqa: E402
from qa_mcp.core import activate_application_context, resolve_runtime_target  # noqa: E402
from qa_mcp import mcp_server  # noqa: E402


def test_ownership_root_follows_runtime_home(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("QA_MCP_HOME", str(tmp_path))
    monkeypatch.delenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", raising=False)

    assert lifecycle._ownership_root() == (
        tmp_path / "runtime/protocol-research/testclient-lifecycle"
    )


def test_explicit_ownership_root_overrides_runtime_home(monkeypatch, tmp_path) -> None:
    explicit = tmp_path / "owned"
    monkeypatch.setenv("QA_MCP_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", str(explicit))

    assert lifecycle._ownership_root() == explicit


def test_composed_marker_is_discovered_and_cleaned_in_its_own_root_after_env_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Real factory launches retain markers in their own roots across env drift.

    This is intentionally a launch-to-stop control, not a helper test: each
    marker is written by the actual lifecycle launch implementation after the
    factory has selected its output directory.  All process boundaries are
    synthetic; no process outside this temporary fixture is signalled.
    """

    process_root = tmp_path / "process-c"
    process_ownership = tmp_path / "process-c-owned"
    explicit_root = tmp_path / "app-a-owned"
    workspace_root = tmp_path / "app-b-workspace"
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    monkeypatch.setenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", str(process_ownership))

    pids = iter((411, 422, 433, 444, 455, 466))
    starts: dict[int, str] = {}
    groups: dict[int, int] = {}
    active: set[int] = set()
    spawned: list[int] = []
    terminated: list[int] = []
    port_probes: dict[int, int] = {}

    class FakeProcess:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def poll(self) -> None:
            return None

    def fake_popen(*_args: object, **_kwargs: object) -> FakeProcess:
        pid = next(pids)
        starts[pid] = f"start-{pid}"
        groups[pid] = pid
        active.add(pid)
        spawned.append(pid)
        return FakeProcess(pid)

    def fake_port_open(_host: str, port: int, **_kwargs: object) -> bool:
        port_probes[port] = port_probes.get(port, 0) + 1
        return port_probes[port] > 1

    monkeypatch.setattr(lifecycle.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(lifecycle, "_port_open", fake_port_open)
    monkeypatch.setattr(lifecycle, "_wait_for_port", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(lifecycle, "_wait_for_process_stability", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(lifecycle, "_any_client_running", lambda: False)
    monkeypatch.setattr(lifecycle, "_clear_locks", lambda _path: [])
    monkeypatch.setattr(lifecycle, "pick_free_display", lambda: ":201")
    monkeypatch.setattr(lifecycle, "_start_xvfb", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(lifecycle, "_pid_alive", lambda pid: pid in active)
    monkeypatch.setattr(lifecycle, "_proc_comm", lambda pid: "1cv8" if pid in active else None)
    monkeypatch.setattr(lifecycle, "_proc_start_ticks", lambda pid: starts.get(pid) if pid in active else None)
    monkeypatch.setattr(lifecycle, "_proc_pgid", lambda pid: groups.get(pid) if pid in active else None)

    def fake_terminate_group(pid: int, **_kwargs: object) -> bool:
        assert pid in active, f"only an active fake process may be terminated: {pid}"
        terminated.append(pid)
        active.remove(pid)
        return True

    monkeypatch.setattr(lifecycle, "_terminate_group", fake_terminate_group)

    def factory(*, home: Path, ownership: Path | None = None, bound: bool = False, label: str = ""):
        settings = Settings(
            manager_templates="manager.json", value_read_templates="value.json",
            home=str(home),
            testclient_ownership_root=str(ownership) if ownership else "",
            client_port=(15414 if label == "explicit" else 15415) if bound else 15381,
        )
        if not bound:
            return mcp_server.create_mcp_server(settings=settings)
        target_root = tmp_path / f"bound-{label}-target"
        target_root.mkdir()
        (target_root / "evidence").mkdir()
        (target_root / "base").mkdir()
        (target_root / "platform").mkdir()
        (target_root / "platform" / "1cv8").write_text("binary", encoding="utf-8")
        (target_root / "target.env").write_text(
            f"INFOBASE_PATH={target_root / 'base'}\nPLATFORM_ROOT={target_root / 'platform'}\n"
            "TEST_CLIENT_USER=Declared\nTEST_CLIENT_PASSWORD=synthetic\nSRC_ROOT=/synthetic/source\n",
            encoding="utf-8",
        )
        inputs = TargetProfileInputs(target_root)
        inputs.write_profile()
        resolution = resolve_runtime_target(inputs.handoff_env())
        assert resolution is not None
        return mcp_server.create_mcp_server(settings=settings, runtime_target=resolution)

    explicit = factory(home=tmp_path / "app-a-workspace", ownership=explicit_root)
    fallback = factory(home=workspace_root)
    bound_explicit_root = tmp_path / "bound-a-owned"
    bound_explicit = factory(
        home=tmp_path / "bound-a-workspace", ownership=bound_explicit_root, bound=True, label="explicit",
    )
    bound_workspace_root = tmp_path / "bound-b-workspace"
    bound_fallback = factory(home=bound_workspace_root, bound=True, label="fallback")
    with activate_application_context(mcp_server.application_context(bound_explicit)):
        provider_target = mcp_server._provider_testclient_target()
    assert provider_target.infobase_path is not None
    def launch_args(port: int) -> dict[str, object]:
        return {"wait_sec": 0, "port": port, "infobase_path": str(tmp_path / "synthetic-infobase")}

    explicit_launch = asyncio.run(explicit.call_tool("launch_test_client", launch_args(15411))).structured_content
    fallback_launch = asyncio.run(fallback.call_tool("launch_test_client", launch_args(15412))).structured_content
    # Bound tools hide physical overrides, but still take the same local
    # lifecycle branch and serialize markers in their own configured roots.
    bound_explicit_launch = asyncio.run(bound_explicit.call_tool(
        "launch_test_client", {"wait_sec": 0, "headless": False},
    )).structured_content
    bound_fallback_launch = asyncio.run(bound_fallback.call_tool(
        "launch_test_client", {"wait_sec": 0, "headless": False},
    )).structured_content
    assert bound_explicit_launch["verdict"] == "success"
    assert bound_fallback_launch["verdict"] == "success"
    # The deliberately unbound public call is still an environment-compatible
    # legacy path, but it must not affect either factory's selected root.
    legacy_launch = mcp_server.launch_test_client(**launch_args(15413))

    explicit_marker = Path(str(explicit_launch["ownership_record_path"]))
    fallback_marker = Path(str(fallback_launch["ownership_record_path"]))
    legacy_marker = Path(str(legacy_launch["ownership_record_path"]))
    bound_explicit_marker = next(bound_explicit_root.rglob(lifecycle.OWNERSHIP_MARKER_NAME))
    bound_fallback_marker = next(
        (bound_workspace_root / "runtime/protocol-research/testclient-lifecycle").rglob(
            lifecycle.OWNERSHIP_MARKER_NAME
        )
    )
    assert explicit_marker.is_relative_to(explicit_root)
    assert fallback_marker.is_relative_to(workspace_root / "runtime/protocol-research/testclient-lifecycle")
    assert legacy_marker.is_relative_to(process_ownership)
    assert bound_explicit_marker.is_relative_to(bound_explicit_root)
    assert bound_fallback_marker.is_relative_to(
        bound_workspace_root / "runtime/protocol-research/testclient-lifecycle"
    )
    for marker in (explicit_marker, fallback_marker, bound_explicit_marker, bound_fallback_marker, legacy_marker):
        record = json.loads(marker.read_text(encoding="utf-8"))
        assert record["out_dir"] == str(marker.parent)
        assert record["pid"] in spawned and record["process_start_ticks"] == starts[record["pid"]]

    # A valid foreign marker is deliberately outside A's ownership root.  A
    # lookup for that PID must neither discover it nor signal its fake process.
    foreign_marker = tmp_path / "foreign-owned" / "launch" / lifecycle.OWNERSHIP_MARKER_NAME
    foreign_marker.parent.mkdir(parents=True)
    foreign_record = json.loads(explicit_marker.read_text(encoding="utf-8"))
    foreign_record.update({"pid": 999, "process_start_ticks": "start-999", "process_pgid": 999})
    foreign_marker.write_text(json.dumps(foreign_record), encoding="utf-8")
    starts[999], groups[999] = "start-999", 999
    active.add(999)

    # Every root has an unrelated byte sentinel.  The inventories below make
    # accidental foreign deletion observable rather than relying on marker
    # existence alone.
    fallback_root = workspace_root / "runtime/protocol-research/testclient-lifecycle"
    bound_fallback_root = bound_workspace_root / "runtime/protocol-research/testclient-lifecycle"
    unrelated_root = tmp_path / "unrelated-sentinels"
    roots = {
        "A explicit": explicit_root,
        "B workspace fallback": fallback_root,
        "bound explicit": bound_explicit_root,
        "bound workspace fallback": bound_fallback_root,
        "legacy process": process_ownership,
        "foreign only": foreign_marker.parents[1],
        "unrelated": unrelated_root,
    }
    for root_name, root in roots.items():
        sentinel = root / "sentinels" / f"{root_name}.bin"
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_bytes(f"preserve:{root_name}".encode())

    def file_inventory(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()
        }

    def control_snapshot() -> dict[str, object]:
        return {
            "roots": {name: file_inventory(root) for name, root in roots.items()},
            "processes": {
                pid: {"comm": "1cv8", "start_ticks": starts[pid], "pgid": groups[pid]}
                for pid in sorted(active)
            },
            "signals": tuple(terminated),
        }

    def assert_only_owner_cleanup(
        before: dict[str, object], *, owner: str, marker: Path, pid: int,
    ) -> None:
        """Show this one cleanup changed only its owner marker/process."""
        after = control_snapshot()
        before_roots = before["roots"]
        after_roots = after["roots"]
        assert isinstance(before_roots, dict) and isinstance(after_roots, dict)
        expected_owner_files = dict(before_roots[owner])
        marker_name = marker.relative_to(roots[owner]).as_posix()
        assert marker_name in expected_owner_files, f"{owner} marker was absent before its cleanup"
        expected_owner_files.pop(marker_name)
        assert not marker.exists(), f"{owner} marker survived its successful cleanup"
        assert after_roots[owner] == expected_owner_files, (
            f"{owner} cleanup changed more than its ownership marker"
        )
        for foreign_owner, foreign_files in before_roots.items():
            if foreign_owner != owner:
                assert after_roots[foreign_owner] == foreign_files, (
                    f"{owner} cleanup changed foreign root {foreign_owner}"
                )

        before_processes = before["processes"]
        assert isinstance(before_processes, dict)
        expected_processes = dict(before_processes)
        del expected_processes[pid]
        assert after["processes"] == expected_processes, (
            f"{owner} cleanup changed a foreign fake process identity"
        )
        assert after["signals"] == before["signals"] + (pid,), (
            f"{owner} cleanup emitted a signal beyond its owned process"
        )

    def assert_refusal_preserves_everything(before: dict[str, object], *, refusal: str) -> None:
        after = control_snapshot()
        assert after["roots"] == before["roots"], f"{refusal} changed marker or resource bytes"
        assert after["processes"] == before["processes"], f"{refusal} changed fake process identity"
        assert after["signals"] == before["signals"], f"{refusal} emitted a signal"

    # Drift the ambient process roots after all factory launches.  Factory A
    # has an explicit ownership root; B derives it from its workspace.
    monkeypatch.setenv("QA_MCP_HOME", str(tmp_path / "drifted-home"))
    monkeypatch.setenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", str(tmp_path / "drifted-owned"))
    before_a_stop = control_snapshot()
    explicit_stop = asyncio.run(explicit.call_tool("stop_test_client", {"pid": 411})).structured_content
    assert explicit_stop["stopped"] is True and explicit_stop["refused"] is False
    assert_only_owner_cleanup(before_a_stop, owner="A explicit", marker=explicit_marker, pid=411)

    before_b_stop = control_snapshot()
    fallback_stop = asyncio.run(fallback.call_tool("stop_test_client", {"pid": 422})).structured_content
    assert fallback_stop["stopped"] is True and fallback_stop["refused"] is False
    assert_only_owner_cleanup(before_b_stop, owner="B workspace fallback", marker=fallback_marker, pid=422)

    before_bound_explicit_stop = control_snapshot()
    bound_explicit_stop = asyncio.run(bound_explicit.call_tool("stop_test_client", {})).structured_content
    assert bound_explicit_stop["verdict"] == "success"
    assert_only_owner_cleanup(
        before_bound_explicit_stop, owner="bound explicit", marker=bound_explicit_marker, pid=433,
    )

    before_bound_fallback_stop = control_snapshot()
    bound_fallback_stop = asyncio.run(bound_fallback.call_tool("stop_test_client", {})).structured_content
    assert bound_fallback_stop["verdict"] == "success"
    assert_only_owner_cleanup(
        before_bound_fallback_stop,
        owner="bound workspace fallback",
        marker=bound_fallback_marker,
        pid=444,
    )

    before_foreign_refusal = control_snapshot()
    foreign_stop = asyncio.run(explicit.call_tool("stop_test_client", {"pid": 999})).structured_content

    assert foreign_stop["stopped"] is False and foreign_stop["refused"] is True
    assert_refusal_preserves_everything(before_foreign_refusal, refusal="foreign-only PID refusal")
    assert terminated == [411, 422, 433, 444]

    # Reused PID/start and process-group changes are refused and retain their
    # original real markers.  The fourth launch is used only to keep the group
    # mismatch independent from the start-tick mismatch.
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    monkeypatch.setenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", str(process_ownership))
    starts[455] = "reused-start"
    before_start_refusal = control_snapshot()
    start_refusal = mcp_server.stop_test_client(455)
    assert start_refusal["reason"] == "ownership_start_mismatch" and start_refusal["refused"] is True
    assert_refusal_preserves_everything(before_start_refusal, refusal="reused-start refusal")

    group_launch = mcp_server.launch_test_client(**launch_args(15416))
    group_marker = Path(str(group_launch["ownership_record_path"]))
    groups[466] = 4660
    before_group_refusal = control_snapshot()
    group_refusal = mcp_server.stop_test_client(466)
    assert group_refusal["reason"] == "ownership_group_mismatch" and group_refusal["refused"] is True
    assert_refusal_preserves_everything(before_group_refusal, refusal="group-mismatch refusal")
    assert terminated == [411, 422, 433, 444]


def test_require_target_infobase_guards_wrong_base(tmp_path) -> None:
    # card 125 — a mutating proof must fail closed on a non-target infobase instead of silently
    # running on the retired vanessa_client via the stale default env.
    demo = tmp_path / "demo.env"
    demo.write_text("INFOBASE_PATH=/opt/ai-dev-suite-for-1c/demo10413/1cd\n", encoding="utf-8")
    assert lifecycle.require_target_infobase(demo, "demo10413/1cd", purpose="proof") \
        == "/opt/ai-dev-suite-for-1c/demo10413/1cd"

    vanessa = tmp_path / "vanessa.env"
    vanessa.write_text("INFOBASE_PATH=/opt/1c-dev/vanessa_client\n", encoding="utf-8")
    with pytest.raises(ValueError, match="wrong infobase"):
        lifecycle.require_target_infobase(vanessa, "demo10413/1cd", purpose="proof")

    empty = tmp_path / "empty.env"
    empty.write_text("PLATFORM_ROOT=/opt/1cv8\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no INFOBASE_PATH"):
        lifecycle.require_target_infobase(empty, "demo10413/1cd")


def test_load_env_file_utf8_quotes_comments(tmp_path) -> None:
    env_path = tmp_path / "p.env"
    env_path.write_text(
        "# comment\n"
        'INFOBASE_PATH="/opt/1c-dev/vanessa_client"\n'
        "TEST_CLIENT_USER=Администратор\n"
        "\n"
        "TEST_CLIENT_PASSWORD='s3cret'\n"
        "PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2130\n",
        encoding="utf-8",
    )
    env = load_env_file(env_path)
    assert env["INFOBASE_PATH"] == "/opt/1c-dev/vanessa_client"  # quotes stripped
    assert env["TEST_CLIENT_USER"] == "Администратор"  # Cyrillic preserved
    assert env["TEST_CLIENT_PASSWORD"] == "s3cret"
    assert "# comment" not in env


def test_load_env_file_missing_is_empty(tmp_path) -> None:
    assert load_env_file(tmp_path / "nope.env") == {}
    assert load_env_file(None) == {}


def test_target_from_env_with_overrides() -> None:
    env = {
        "INFOBASE_PATH": "/ib/vanessa_client",
        "PLATFORM_ROOT": "/opt/1cv8/x86_64/8.3.27.2130",
        "TEST_CLIENT_USER": "Администратор",
        "TEST_CLIENT_PASSWORD": "pw",
        "TEST_CLIENT_KIND": "thick",
    }
    # explicit (non-None) overrides win; None overrides are ignored (fall back to env)
    target = TestClientTarget.from_env(env, port=20000, user=None, headless=False)
    assert target.infobase_path == "/ib/vanessa_client"
    assert target.user == "Администратор"  # None override ignored
    assert target.password == "pw"
    assert target.port == 20000
    assert target.headless is False
    assert target.kind == "thick"


def test_resolved_client_bin_thick_vs_thin() -> None:
    thick = TestClientTarget(platform_root="/plat", kind="thick")
    thin = TestClientTarget(platform_root="/plat", kind="thin")
    assert thick.resolved_client_bin() == "/plat/1cv8"
    assert thin.resolved_client_bin() == "/plat/1cv8c"
    assert TestClientTarget(client_bin="/custom/1cv8").resolved_client_bin() == "/custom/1cv8"


def test_build_argv_file_infobase_headless() -> None:
    target = TestClientTarget(
        infobase_path="/opt/1c-dev/vanessa_client", platform_root="/plat",
        user="Администратор", port=15381, headless=True,
    )
    argv = target.build_argv()
    assert argv[:2] == ["xvfb-run", "-a"]  # headless wrapper
    assert "/plat/1cv8" in argv and "ENTERPRISE" in argv
    i = argv.index("/IBConnectionString")
    assert argv[i + 1] == 'File="/opt/1c-dev/vanessa_client";'
    assert "/NАдминистратор" in argv
    assert argv[argv.index("-TPort") + 1] == "15381"
    assert "/TESTCLIENT" in argv
    # no password -> no /P flag
    assert not any(a.startswith("/P") for a in argv)


def test_build_argv_password_and_out_and_no_xvfb(tmp_path) -> None:
    target = TestClientTarget(
        infobase_path="/ib", platform_root="/plat", user="U", password="pw",
        port=9, headless=False,
    )
    argv = target.build_argv(out_dir=tmp_path)
    assert argv[0] == "/plat/1cv8"  # no xvfb-run when headless=False
    assert "/Ppw" in argv
    assert "/Out" in argv and str(tmp_path / "testclient.out") in argv
    assert "-NoTruncate" in argv


def test_connection_string_override_and_error() -> None:
    assert TestClientTarget(connection_string="Srvr=...;Ref=...;").connection_string_value() == "Srvr=...;Ref=...;"
    try:
        TestClientTarget().connection_string_value()
    except ValueError as exc:
        assert "infobase_path or connection_string" in str(exc)
    else:
        raise AssertionError("expected ValueError when neither path nor connection_string is set")


def test_redacted_summary_hides_password() -> None:
    target = TestClientTarget(infobase_path="/ib/vanessa_client", user="U", password="topsecret", port=42)
    summary = target.redacted_summary()
    assert summary["port"] == 42
    assert summary["user"] == "U"
    assert summary["password_set"] is True
    # the password value must NOT leak anywhere in the summary
    assert "topsecret" not in repr(summary)


def test_resolve_launch_environment_autodetects_and_prepends_libgcc(tmp_path) -> None:
    libgcc = tmp_path / "libgcc_s.so.1"
    libgcc.write_text("stub", encoding="utf-8")
    env = lifecycle.resolve_testclient_launch_environment(
        base_env={"LD_PRELOAD": "/existing.so"},
        candidate_paths=[str(libgcc)],
    )
    assert env.libgcc_preload == str(libgcc)
    assert env.libgcc_preload_source == "autodetected"
    assert env.env["LD_PRELOAD"] == f"{libgcc}:/existing.so"
    assert env.env["LIBGL_ALWAYS_SOFTWARE"] == "1"
    assert env.env["GALLIUM_DRIVER"] == "softpipe"
    assert env.status()["software_rendering"] == {
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "GALLIUM_DRIVER": "softpipe",
    }


def test_resolve_launch_environment_honors_opt_out_and_override(tmp_path) -> None:
    libgcc = tmp_path / "libgcc_s.so.1"
    libgcc.write_text("stub", encoding="utf-8")
    disabled = lifecycle.resolve_testclient_launch_environment(
        base_env={lifecycle.TESTCLIENT_LIBGCC_PRELOAD_ENV: "", "LD_PRELOAD": "/existing.so"},
        candidate_paths=[str(libgcc)],
    )
    assert disabled.libgcc_preload is None
    assert disabled.libgcc_preload_source == "disabled"
    assert disabled.env["LD_PRELOAD"] == "/existing.so"

    override = lifecycle.resolve_testclient_launch_environment(
        base_env={lifecycle.TESTCLIENT_LIBGCC_PRELOAD_ENV: "/custom/libgcc.so"},
        candidate_paths=[str(libgcc)],
    )
    assert override.libgcc_preload == "/custom/libgcc.so"
    assert override.libgcc_preload_source == "override"
    assert override.env["LD_PRELOAD"] == "/custom/libgcc.so"

    rendering_override = lifecycle.resolve_testclient_launch_environment(
        base_env={"LIBGL_ALWAYS_SOFTWARE": "0", "GALLIUM_DRIVER": "llvmpipe"},
        candidate_paths=[],
    )
    assert rendering_override.env["LIBGL_ALWAYS_SOFTWARE"] == "0"
    assert rendering_override.env["GALLIUM_DRIVER"] == "llvmpipe"


def test_launch_timeout_includes_bounded_sanitized_logs(monkeypatch, tmp_path) -> None:
    class FakeProc:
        pid = 424242

        def poll(self) -> int:
            return 127

    def fake_popen(*_args, **kwargs):
        stdout = kwargs["stdout"]
        stdout.write("1cv8: libgcc_s.so.1: version GCC_13.0.0 not found\npassword=topsecret\n")
        stdout.flush()
        return FakeProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(lifecycle, "_any_client_running", lambda: False)
    monkeypatch.setattr(lifecycle, "_write_ownership_marker", lambda _handle: str(tmp_path / "owned.json"))
    monkeypatch.setattr(lifecycle, "_wait_for_port", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(lifecycle, "stop_test_client", lambda *_args, **_kwargs: {"stopped": True})

    target = TestClientTarget(infobase_path="/ib", user="U", password="topsecret", port=54321, headless=False)
    with pytest.raises(TimeoutError) as exc:
        lifecycle.launch_test_client(target, wait_sec=1, out_dir=tmp_path)
    message = str(exc.value)
    assert "TestClient TPort 54321 did not start listening within 1s" in message
    assert "process return code: 127" in message
    assert "client.out tail" in message
    assert "GCC_13.0.0 not found" in message
    assert "topsecret" not in message


def test_launch_refuses_preexisting_tport_before_start(monkeypatch, tmp_path) -> None:
    started: list[bool] = []
    monkeypatch.setattr(lifecycle, "_port_open", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *_args, **_kwargs: started.append(True),
    )

    target = TestClientTarget(connection_string='Srvr="db";Ref="demo";', port=54320)
    with pytest.raises(RuntimeError) as exc:
        lifecycle.launch_test_client(target, out_dir=tmp_path)

    assert "127.0.0.1:54320 is already listening" in str(exc.value)
    assert "attach to the existing endpoint" in str(exc.value)
    assert started == []


def test_launch_records_ownership_before_readiness_wait(monkeypatch, tmp_path) -> None:
    class FakeProc:
        pid = 424241

        def poll(self) -> None:
            return None

    events: list[str] = []
    monkeypatch.setattr(lifecycle, "_port_open", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(subprocess, "Popen", lambda *_args, **_kwargs: FakeProc())
    monkeypatch.setattr(
        lifecycle,
        "_write_ownership_marker",
        lambda _handle: events.append("marker") or str(tmp_path / "owned.json"),
    )
    monkeypatch.setattr(
        lifecycle,
        "_wait_for_port",
        lambda *_args, **_kwargs: events.append("wait") or False,
    )
    monkeypatch.setattr(lifecycle, "stop_test_client", lambda *_args, **_kwargs: {"stopped": True})

    target = TestClientTarget(connection_string='Srvr="db";Ref="demo";', port=54319, headless=False)
    with pytest.raises(TimeoutError):
        lifecycle.launch_test_client(target, wait_sec=0.1, out_dir=tmp_path)

    assert events == ["marker", "wait"]


def test_launch_fails_when_process_exits_after_transient_listener(monkeypatch, tmp_path) -> None:
    class FakeProc:
        pid = 424243

        def poll(self) -> int:
            return 26

    stopped: list[int] = []

    def fake_popen(*_args, **_kwargs):
        (tmp_path / "testclient.out").write_text(
            "License not found for password=topsecret\n",
            encoding="utf-8",
        )
        return FakeProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(lifecycle, "_write_ownership_marker", lambda _handle: str(tmp_path / "owned.json"))
    monkeypatch.setattr(lifecycle, "_wait_for_port", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(lifecycle, "_wait_for_process_stability", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        lifecycle,
        "stop_test_client",
        lambda proc, **_kwargs: stopped.append(proc.pid) or {"stopped": True},
    )

    target = TestClientTarget(
        connection_string='Srvr="db";Ref="demo";',
        user="U",
        password="topsecret",
        port=54322,
        headless=False,
    )
    with pytest.raises(TimeoutError) as exc:
        lifecycle.launch_test_client(target, wait_sec=1, settle_sec=0.1, out_dir=tmp_path)

    message = str(exc.value)
    assert "did not remain ready after becoming connectable" in message
    assert "readiness phase: process_stability" in message
    assert "post-listener stability window" in message
    assert "License not found" in message
    assert "topsecret" not in message
    assert stopped == [424243]


def test_local_launch_defaults_cover_delayed_post_listener_failures() -> None:
    launch_default = inspect.signature(lifecycle.launch_test_client).parameters["settle_sec"].default
    ensure_default = inspect.signature(lifecycle.ensure_test_client).parameters["settle_sec"].default

    assert launch_default == lifecycle.DEFAULT_READINESS_STABILITY_SEC == 20.0
    assert ensure_default == lifecycle.DEFAULT_READINESS_STABILITY_SEC


def test_attach_test_client_returns_external_handle() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    host, port = srv.getsockname()
    try:
        handle = lifecycle.attach_test_client(host=host, port=port)
        status = handle.status()
        assert status["attached"] is True
        assert status["owns_process"] is False
        assert status["pid"] is None
        assert status["alive"] is None
        assert status["listening"] is True
        stopped = handle.stop()
        assert stopped["stopped"] is False
        assert stopped["reason"] == "external TestClient is not owned by qa-mcp"
    finally:
        srv.close()


def test_attach_test_client_missing_endpoint_fails_closed() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    host, port = srv.getsockname()
    srv.close()
    with pytest.raises(ConnectionError) as exc:
        lifecycle.attach_test_client(host=host, port=port, connect_timeout_sec=0.05)
    assert f"{host}:{port}" in str(exc.value)


def test_port_is_listening_true_then_false() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    host, port = srv.getsockname()
    try:
        assert lifecycle.port_is_listening(host, port) is True
    finally:
        srv.close()
    # after close, nothing accepts on that port
    assert lifecycle.port_is_listening(host, port) is False


def test_port_is_listening_uses_listener_only_probe_for_relay(monkeypatch) -> None:
    observed: list[tuple[tuple[str, int], float]] = []
    relay_endpoint = ("station.example", 15382)
    monkeypatch.setattr(
        lifecycle,
        "relay_configuration",
        lambda: (relay_endpoint, "relay-secret"),
        raising=False,
    )
    monkeypatch.setattr(
        lifecycle,
        "relay_listener_reachable",
        lambda address, timeout: observed.append((address, timeout)) is None,
        raising=False,
    )
    monkeypatch.setattr(
        lifecycle,
        "connect_testclient",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("relay readiness must not authenticate or dial the target")
        ),
    )

    assert lifecycle.port_is_listening(*relay_endpoint, timeout_sec=0.25) is True
    assert observed == [(relay_endpoint, 0.25)]


def test_terminate_group_kills_child() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
    )
    assert lifecycle.pid_is_alive(proc.pid) is True
    gone = lifecycle._terminate_group(proc.pid, kill_after_sec=3.0)
    assert gone is True
    assert lifecycle.pid_is_alive(proc.pid) is False
    proc.wait(timeout=2)


def test_stop_by_pid_refuses_unrecognized_pid_without_kill(monkeypatch) -> None:
    terminated: list[int] = []
    monkeypatch.setattr(lifecycle, "_proc_comm", lambda _pid: "bash")
    monkeypatch.setattr(
        lifecycle,
        "_terminate_group",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )

    result = lifecycle.stop_by_pid(424242, kill_after_sec=0.01)

    assert result["refused"] is True
    assert result["stopped"] is False
    assert result["reason"] == "unrecognized_process"
    assert result["process_comm"] == "bash"
    assert terminated == []


def test_stop_by_pid_refuses_recognized_but_unowned_testclient(monkeypatch) -> None:
    terminated: list[int] = []
    monkeypatch.setattr(lifecycle, "_proc_comm", lambda _pid: "1cv8")
    monkeypatch.setattr(lifecycle, "_find_ownership_record", lambda _pid: None)
    monkeypatch.setattr(
        lifecycle,
        "_terminate_group",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )

    result = lifecycle.stop_by_pid(111, kill_after_sec=0.01)

    assert result["refused"] is True
    assert result["stopped"] is False
    assert result["reason"] == "not_qa_mcp_owned"
    assert result["process_comm"] == "1cv8"
    assert terminated == []


def test_stop_by_pid_allows_recognized_testclient_and_xvfb(monkeypatch) -> None:
    terminated: list[int] = []
    record = {
        "schema": lifecycle.OWNERSHIP_MARKER_SCHEMA,
        "pid": 111,
        "process_pgid": 111,
        "process_start_ticks": "1001",
        "xvfb_pid": 222,
        "xvfb_pgid": 222,
        "xvfb_start_ticks": "2002",
        "_marker_path": "/tmp/qa-mcp-owned-process.json",
    }

    def fake_comm(pid: int) -> str | None:
        return {111: "1cv8", 222: "Xvfb"}.get(pid)

    monkeypatch.setattr(lifecycle, "_proc_comm", fake_comm)
    monkeypatch.setattr(lifecycle, "_proc_start_ticks", lambda pid: {111: "1001", 222: "2002"}.get(pid))
    monkeypatch.setattr(lifecycle, "_proc_pgid", lambda pid: {111: 111, 222: 222}.get(pid))
    monkeypatch.setattr(lifecycle, "_find_ownership_record", lambda pid: record if pid == 111 else None)
    monkeypatch.setattr(
        lifecycle,
        "_terminate_group",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )

    result = lifecycle.stop_by_pid(111, xvfb_pid=222, kill_after_sec=0.01)

    assert result["refused"] is False
    assert result["stopped"] is True
    assert result["xvfb_stopped"] is True
    assert result["process_comm"] == "1cv8"
    assert result["xvfb_comm"] == "Xvfb"
    assert result["ownership_record_path"] == "/tmp/qa-mcp-owned-process.json"
    assert terminated == [111, 222]


def test_stop_by_pid_cleans_owned_xvfb_after_client_exited(monkeypatch) -> None:
    terminated: list[int] = []
    removed: list[dict[str, object]] = []
    record = {
        "schema": lifecycle.OWNERSHIP_MARKER_SCHEMA,
        "pid": 111,
        "process_comm": "1cv8",
        "process_pgid": 111,
        "process_start_ticks": "1001",
        "xvfb_pid": 222,
        "xvfb_comm": "Xvfb",
        "xvfb_pgid": 222,
        "xvfb_start_ticks": "2002",
        "_marker_path": "/tmp/qa-mcp-owned-process.json",
    }

    monkeypatch.setattr(lifecycle, "_proc_comm", lambda pid: {111: None, 222: "Xvfb"}.get(pid))
    monkeypatch.setattr(lifecycle, "_proc_start_ticks", lambda pid: {222: "2002"}.get(pid))
    monkeypatch.setattr(lifecycle, "_proc_pgid", lambda pid: {222: 222}.get(pid))
    monkeypatch.setattr(lifecycle, "_find_ownership_record", lambda pid: record if pid == 111 else None)
    monkeypatch.setattr(
        lifecycle,
        "_terminate_group",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )
    monkeypatch.setattr(lifecycle, "_remove_ownership_record", lambda value: removed.append(value))

    result = lifecycle.stop_by_pid(111, kill_after_sec=0.01)

    assert result["refused"] is False
    assert result["stopped"] is True
    assert result["client_already_exited"] is True
    assert result["xvfb_stopped"] is True
    assert result["xvfb_already_exited"] is False
    assert result["xvfb_comm"] == "Xvfb"
    assert terminated == [222]
    assert removed == [record]


def test_stop_by_pid_refuses_reused_xvfb_after_client_exited(monkeypatch) -> None:
    terminated: list[int] = []
    record = {
        "schema": lifecycle.OWNERSHIP_MARKER_SCHEMA,
        "pid": 111,
        "process_comm": "1cv8",
        "process_pgid": 111,
        "process_start_ticks": "1001",
        "xvfb_pid": 222,
        "xvfb_comm": "Xvfb",
        "xvfb_pgid": 222,
        "xvfb_start_ticks": "2002",
        "_marker_path": "/tmp/qa-mcp-owned-process.json",
    }

    monkeypatch.setattr(lifecycle, "_proc_comm", lambda pid: {111: None, 222: "Xvfb"}.get(pid))
    monkeypatch.setattr(lifecycle, "_proc_start_ticks", lambda pid: {222: "reused"}.get(pid))
    monkeypatch.setattr(lifecycle, "_proc_pgid", lambda pid: {222: 222}.get(pid))
    monkeypatch.setattr(lifecycle, "_find_ownership_record", lambda pid: record if pid == 111 else None)
    monkeypatch.setattr(
        lifecycle,
        "_terminate_group",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )

    result = lifecycle.stop_by_pid(111, kill_after_sec=0.01)

    assert result["refused"] is True
    assert result["stopped"] is False
    assert result["reason"] == "ownership_start_mismatch"
    assert terminated == []


def test_wait_for_port_times_out_fast() -> None:
    # a port nobody listens on -> returns False within ~the timeout, never hangs
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    _, port = srv.getsockname()
    srv.close()  # free the port so connections are refused
    start = time.monotonic()
    assert lifecycle._wait_for_port("127.0.0.1", port, timeout_sec=0.4, interval_sec=0.1) is False
    assert time.monotonic() - start < 3.0
