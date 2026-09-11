#!/usr/bin/env python3
"""Live CLI for qa_mcp.protocol.native_write.write_form_value — card 80 Fork-2 productized.

Writes an ARBITRARY value into a form field on a live /TESTCLIENT (no Vanessa), via full-session replay of a
genuine INPUT capture + variable-length value retarget, and verifies by read-back.

Run (needs a live TestClient): PYTHONPATH=src python3 tools/protocol-research/native_write_probe.py \
    --value "AnyNewValue" --host 127.0.0.1 --port 15381
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_write import derive_write_template, write_form_value  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", required=True, help="the new value to write+commit")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=15381)
    ap.add_argument("--capture", default="genuine-commit-conn", help="genuine INPUT capture template")
    ap.add_argument("--field", default="PF_EDIT_STRING")
    ap.add_argument("--captured-value", default="QAGENUINE2026", help="value the template capture set")
    ap.add_argument("--default-value", default="PF_EDIT_STRING_VALUE")
    ap.add_argument("--read-frames", default="549,550", help="mgr ordinals whose responses read the field back")
    ap.add_argument("--stop-after", type=int, default=360,
                    help="replay through the commit (focus-change) only; read frames beyond this are sent "
                         "out-of-order (short replay keeps multi-write on one client in sync)")
    ap.add_argument("--output-dir", default=None, help="save set/read responses here for debugging")
    args = ap.parse_args()

    template = derive_write_template(
        resolve_capture_dir(args.capture), args.field, args.captured_value, args.default_value
    )
    result = write_form_value(
        template, args.value, host=args.host, port=args.port,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["committed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
