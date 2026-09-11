#!/usr/bin/env python3
"""Test NativeWriteSession: open the fixture form ONCE, then write several values on the SAME connection
(multi-write without re-open desync). Card 80 Fork-2 productized — multi-write fix."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_write import NativeWriteSession, derive_write_template  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--values", required=True, help="comma-separated values to write in sequence")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=15381)
    ap.add_argument("--capture", default="genuine-commit-conn")
    ap.add_argument("--field", default="PF_EDIT_STRING")
    ap.add_argument("--captured-value", default="QAGENUINE2026")
    ap.add_argument("--default-value", default="PF_EDIT_STRING_VALUE")
    args = ap.parse_args()

    # generalized: auto-derive the template from the capture (no hard-coded ordinals)
    template = derive_write_template(
        resolve_capture_dir(args.capture), args.field, args.captured_value, args.default_value
    )
    results = []
    with NativeWriteSession(template, host=args.host, port=args.port) as sess:
        for v in args.values.split(","):
            r = sess.write(v)
            print(json.dumps(r, ensure_ascii=False))
            results.append(r)
    return 0 if all(r["committed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
