"""CLI for the live-regression harness — `python -m qa_mcp.regression`.

Phase-aware sequencing (mirrors the handoff's always-restart-Apache discipline):

  1. ``data_pre``  — Apache UP, no client: the OData data-layer checks.
  2. boot a native /TESTCLIENT (manage_apache STOPS Apache) → run the ``ui`` checks → ALWAYS stop the client
     in ``finally`` (which restarts Apache).
  3. ``data_post`` — Apache restored: post-write data-layer verification (the write-roundtrip tail).
  4. ``measure``   — standalone; ``measure_scenario`` owns its own debug client.

Exit code is 0 only if every REQUIRED check passed, so this is CI/cron-gateable. Reports (JUnit XML + JSON +
text) land under ``--out`` (a runtime path by default, git-ignored).

Examples:
  python -m qa_mcp.regression                          # the read-only CORE set (nightly-safe)
  python -m qa_mcp.regression --include-write          # + UI→DB roundtrip (creates a lab record)
  python -m qa_mcp.regression --include-measure        # + coverage/perf via the debug protocol (slow)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ..config import Settings
from ..protocol.lifecycle import TestClientTarget, launch_test_client, load_env_file
from ..scenario.reporting import junit_xml
from .checks import LiveContext, core_checks, measure_checks, write_roundtrip_checks
from .harness import RegressionReport, run_checks


def _phase(checks, phase):
    return [c for c in checks if c.phase == phase]


def _start_matchbox(display: str):
    """xtest writes need a window manager that strips title bars; start matchbox on the owned display."""
    try:
        return subprocess.Popen(
            ["matchbox-window-manager", "-use_titlebar", "no"],
            env={**os.environ, "DISPLAY": display},
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return None


def main(argv: list[str] | None = None) -> int:
    settings = Settings.from_env()
    ap = argparse.ArgumentParser(prog="qa_mcp.regression", description="qa-mcp live-regression harness")
    ap.add_argument("--env", default=".ai1c/vanessa-qa-mcp.env", help="TestClient env profile")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=15381)
    ap.add_argument("--odata-url", default=settings.odata_url)
    ap.add_argument("--odata-user", default=settings.regression_odata_user)
    ap.add_argument("--odata-password", default=settings.odata_password)
    ap.add_argument("--src-root", default="", help="config .mdo root for the measure module-name resolver")
    ap.add_argument("--out", default="runtime/live-regression", help="report output directory")
    ap.add_argument("--wait-sec", type=float, default=120.0)
    ap.add_argument("--settle-sec", type=float, default=6.0)
    ap.add_argument("--max-ms", type=float, default=0.0, help="perf assertion for the measure check")
    ap.add_argument("--include-write", action="store_true", help="add the UI→DB roundtrip (creates a lab record)")
    ap.add_argument("--include-measure", action="store_true", help="add coverage/perf via the debug protocol")
    ap.add_argument("--no-ui", action="store_true", help="skip the boot + UI checks (data-layer only)")
    args = ap.parse_args(argv)

    checks = core_checks()
    if args.include_write:
        checks += write_roundtrip_checks()
    if args.include_measure:
        checks += measure_checks()

    ctx = LiveContext(
        host=args.host, port=args.port,
        odata_url=args.odata_url, odata_user=args.odata_user, odata_password=args.odata_password,
        env_file=args.env, src_root=args.src_root, measure_max_ms=args.max_ms,
    )
    report = RegressionReport()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Phase 1 — data_pre (Apache up, no client)
    print("[regression] phase data_pre (OData, Apache up)…")
    run_checks(_phase(checks, "data_pre"), ctx, into=report)

    # Phase 2 — ui (boot the client; ALWAYS tear down + restart Apache)
    ui_checks = _phase(checks, "ui")
    if ui_checks and not args.no_ui:
        env = load_env_file(args.env)
        target = TestClientTarget.from_env(
            env, host=args.host, port=args.port, manage_apache=True, clear_lock=True,
            # OWN a known display (not the anonymous `xvfb-run -a`) so the UI checks' cold-state Escape sweep
            # (read_list_grid/column/row, card 124) can reach the client window via XTEST on this display.
            display="auto",
        )
        print(f"[regression] phase ui — booting /TESTCLIENT on {args.host}:{args.port}…")
        handle = launch_test_client(target, wait_sec=args.wait_sec, settle_sec=args.settle_sec)
        wm = None
        try:
            if handle.display:
                ctx.display = handle.display
                # Export DISPLAY so read_list_grid's cold-state sweep (card 124) targets the booted client's
                # display, and start a WM so XTEST keystrokes focus the client window.
                os.environ["DISPLAY"] = handle.display
                wm = _start_matchbox(handle.display)
                time.sleep(2)
            run_checks(ui_checks, ctx, into=report)
        finally:
            try:
                if wm is not None:
                    wm.terminate()
            finally:
                handle.stop()  # restarts Apache
                # belt-and-braces: ensure Apache is back even if stop() could not
                subprocess.run(["sudo", "-n", "systemctl", "start", "apache2"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif ui_checks:
        print("[regression] phase ui SKIPPED (--no-ui)")

    # Phase 3 — data_post (Apache restored)
    post = _phase(checks, "data_post")
    if post:
        print("[regression] phase data_post (OData, Apache restored)…")
        run_checks(post, ctx, into=report)

    # Phase 4 — measure (standalone; owns its own client)
    meas = _phase(checks, "measure")
    if meas:
        print("[regression] phase measure (debug protocol; boots its own client)…")
        run_checks(meas, ctx, into=report)

    # Emit reports
    out = Path(args.out) / stamp
    out.mkdir(parents=True, exist_ok=True)
    (out / "junit.xml").write_text(junit_xml(report.to_scenario_results(),
                                             suite_name="qa-mcp-live-regression"), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "report.txt").write_text(report.render(), encoding="utf-8")

    print("\n" + report.render())
    print(f"\n[regression] reports → {out}")
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
