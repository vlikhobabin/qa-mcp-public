#!/usr/bin/env python3
"""Card 98 / change 5 (the 🚩 GATE) — does the capture-free READ path establish against a 2nd (foreign) config?

Everything is proven on ONE config (the fixture in vanessa_client). The crux question (Q1): is the
bootstrap/handshake config-agnostic, or does it encode fixture/infobase specifics? The native read path replays
the vanessa_client read-only bootstrap (`tm-v1-ro-batchQ3`) + GuidRebinder. This probe points that read at a
DIFFERENT config's TestClient (e.g. demo_1_0_41_3 = a real 1C:БСП base) and reports whether the session
establishes and the active window reads back — with NO config-specific capture.

    PYTHONPATH=src python3 tools/protocol-research/second_config_read_probe.py [port] [kind]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

# Replicate mcp_server._run WITHOUT importing mcp_server (which pulls in FastMCP / the `mcp` package).
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402
from qa_mcp.scenario import Scenario, ScenarioRunner  # noqa: E402

DEFAULT_TEMPLATES = REPO / "docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/manager_frame_templates.json"


def _run(scenario: Scenario, host: str, port: int, capture_dir: str, single_session: bool):
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, REPO))
    templates = ProtocolTemplates.load(DEFAULT_TEMPLATES)
    synthesized = synthesize_bootstrap()
    output_dir = REPO / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()

    def session_factory() -> TestClientSession:
        return TestClientSession(host=host, port=port)

    runner = ScenarioRunner(session_factory, bootstrap, templates, output_dir=output_dir, synthesized=synthesized)
    result = runner.run_single_session(scenario) if single_session else runner.run(scenario)
    return result.to_dict()


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
    kind = sys.argv[2] if len(sys.argv) > 2 else "read_active_window"
    scenario = Scenario.from_dict({"name": f"2ndcfg-{kind}",
                                   "steps": [{"kind": kind, "name": kind}]})
    print(f"port={port} kind={kind} bootstrap=tm-v1-ro-batchQ3 (vanessa_client read-only)")
    try:
        result = _run(scenario, "127.0.0.1", port, "tm-v1-ro-batchQ3", single_session=True)
    except Exception as e:  # noqa: BLE001
        print(f"  EXCEPTION establishing/reading: {type(e).__name__}: {e}")
        print("RESULT: bootstrap did NOT establish against the 2nd config (per-config capture likely needed)")
        return 1
    steps = result.get("steps", [])
    print(f"  scenario status={result.get('status')} steps={len(steps)}")
    for s in steps:
        print(f"    step kind={s.get('kind')} status={s.get('status')} error={s.get('error')}")
        print(f"      preview[:500]={s.get('preview','')!r}")
    # establishment: the read step ran without a transport error AND returned window content (preview)
    step = steps[0] if steps else {}
    established = step.get("status") in ("ok", "assert_failed") and bool(step.get("preview"))
    print("RESULT:", "READ ESTABLISHED against 2nd config — bootstrap is config-portable" if established
          else f"read did NOT establish (step status={step.get('status')}, error={step.get('error')})")
    return 0 if established else 2


if __name__ == "__main__":
    raise SystemExit(main())
