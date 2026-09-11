"""CLI for the platform-support factory — ``python -m qa_mcp.platform_support``.

  probe <version>       classify a build offline (case already/A/B) — no client boot
  validate <version>    boot /TESTCLIENT on the build + run live-regression → GREEN/RED verdict (writes verdict.json)
  bless <version>       append a GREEN same-family build to its capture manifest (the supported-build list)
  matrix [--validate]   probe (and optionally validate not-yet-blessed case-A builds) every installed build

Exit code: 0 on success/GREEN, 1 on RED/refused, 2 on usage error. Add ``--json`` for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import (
    DEFAULT_ENV_FILE,
    DEFAULT_ODATA_URL,
    bless,
    installed_platforms,
    probe,
    validate,
)


def _emit(obj, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))


def _cmd_probe(args) -> int:
    pr = probe(args.version)
    if args.json:
        _emit(pr.to_dict(), True)
    else:
        inst = "installed" if pr.installed else "NOT installed"
        print(f"[probe] {pr.version}  family={pr.family}  {inst}")
        print(f"        case {pr.case.upper()}: {pr.reason}")
    return 0 if pr.case != "unknown" else 2


def _cmd_validate(args) -> int:
    v = validate(
        args.version,
        odata_url=args.odata_url,
        include_write=not args.no_write,
        base_env_file=args.env,
        timeout_sec=args.timeout_sec,
    )
    if args.json:
        _emit(v.to_dict(), True)
    else:
        verdict = "GREEN" if v.green else "RED"
        print(f"[validate] {v.version} → {verdict}  ({v.passed}/{v.total} passed, exit={v.exit_code})")
        if v.drift:
            print(f"           drift: {v.drift.get('severity','?').upper()} — {v.drift.get('message','')}")
        if v.failed_checks:
            print(f"           failed: {', '.join(v.failed_checks)}")
        if v.error:
            print(f"           error: {v.error}")
        if v.report_json:
            print(f"           report: {v.report_json}")
    return 0 if v.green else 1


def _cmd_bless(args) -> int:
    r = bless(args.version, notes=args.notes or None, require_green=not args.force)
    if args.json:
        _emit(r.to_dict(), True)
    else:
        print(f"[bless] {r.message}")
        if r.changed:
            print(f"        {r.manifest_path}: compatible {len(r.compatible_before)} → "
                  f"{len(r.compatible_after)} builds")
    return 0 if (r.changed or "no-op" in r.message) else 1


def _cmd_matrix(args) -> int:
    rows = []
    worst = 0
    for version in installed_platforms():
        pr = probe(version)
        row = {"version": version, "family": pr.family, "case": pr.case,
               "installed": pr.installed, "green": None, "note": pr.reason}
        if args.validate and pr.case == "A":
            v = validate(version, odata_url=args.odata_url, include_write=not args.no_write,
                         base_env_file=args.env, timeout_sec=args.timeout_sec)
            row["green"] = v.green
            row["note"] = ("GREEN" if v.green else f"RED: {', '.join(v.failed_checks) or v.error or '?'}")
            if not v.green:
                worst = 1
        rows.append(row)

    if args.json:
        _emit({"rows": rows}, True)
    else:
        print(f"{'version':16} {'fam':4} {'case':8} {'green':6} note")
        print("-" * 80)
        for r in rows:
            g = "" if r["green"] is None else ("GREEN" if r["green"] else "RED")
            print(f"{r['version']:16} {str(r['family']):4} {r['case']:8} {g:6} {r['note']}")
    return worst


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="qa_mcp.platform_support",
                                 description="qa-mcp platform-version support factory")
    ap.add_argument("--json", action="store_true", help="machine-readable JSON output")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("probe", help="classify a build offline")
    p.add_argument("version")
    p.set_defaults(func=_cmd_probe)

    p = sub.add_parser("validate", help="boot + live-regression → GREEN/RED")
    p.add_argument("version")
    p.add_argument("--odata-url", default=DEFAULT_ODATA_URL)
    p.add_argument("--env", default=DEFAULT_ENV_FILE, help="base env profile to clone (PLATFORM_ROOT overridden)")
    p.add_argument("--no-write", action="store_true", help="skip the UI→DB write roundtrip (read-only checks)")
    p.add_argument("--timeout-sec", type=float, default=900.0)
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("bless", help="record a GREEN same-family build in its manifest")
    p.add_argument("version")
    p.add_argument("--notes", default="")
    p.add_argument("--force", action="store_true", help="bless without requiring a GREEN verdict on disk")
    p.set_defaults(func=_cmd_bless)

    p = sub.add_parser("matrix", help="probe (and optionally validate) every installed build")
    p.add_argument("--validate", action="store_true", help="also run live validate on not-yet-blessed case-A builds")
    p.add_argument("--odata-url", default=DEFAULT_ODATA_URL)
    p.add_argument("--env", default=DEFAULT_ENV_FILE)
    p.add_argument("--no-write", action="store_true")
    p.add_argument("--timeout-sec", type=float, default=900.0)
    p.set_defaults(func=_cmd_matrix)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
