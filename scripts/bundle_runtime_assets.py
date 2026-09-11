#!/usr/bin/env python3
"""Bundle the runtime assets the qa-mcp package needs into `src/qa_mcp/_bundled/<version>/` (per platform family).

The engine replays genuine TestClient captures + manager-frame templates that currently live under the
git-ignored `runtime/` tree and the research tree under `docs/`. For the package to be self-contained
(fresh clone / Docker image / wheel), those inputs must travel inside the package.

This script copies ONLY the files the runtime actually reads:
  * per capture: `traffic.jsonl` (sanitized — see below),
  * `manager_frame_templates.json` (DEFAULT_TEMPLATES) and the value-read template set,
  * `accepted_mappings.json` (read-only operation descriptor evidence).

Sanitizing capture traffic: `payload_from_record` prefers an inline `payload_b64`; the `aggregate_path`
(an absolute machine path, e.g. `C:\\Users\\...`) is only a fallback. We drop the `aggregate_*` keys when
`payload_b64` is present (so no machine path leaks into the public image), and INLINE the bytes when a
record has no `payload_b64` (so the bundled capture is fully portable with no external `.bin`).

Idempotent: re-run after refreshing a capture. Source = the dev `runtime/`+`docs/` trees on this machine.
"""

from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME_CAPTURES = REPO / "runtime" / "protocol-research" / "captures"
BUNDLED = REPO / "src" / "qa_mcp" / "_bundled"  # parent of the per-version subdirs (_bundled/<version>/)

# Capture names the shipped tool surface references as defaults (string literals in src/).
CAPTURES = [
    "genuine-card97-ch3-cellread-20260619",
    "genuine-card97-ch3-report-20260619",
    "genuine-card97-ch4-advsearch-20260619",
    "genuine-card97-ch4-search-20260619",
    "genuine-card97-ch4-viewmode-20260619",
    "genuine-card98-demo-write",
    "genuine-card98-listform-read",
    "genuine-card98-nextrow",
    "genuine-card98-nextrow-flat",
    "genuine-card98-rowbyvalue",
    "genuine-commit-conn",
    "genuine-multiaction-clean-20260617",
    "tm-v1-ro-batchQ3",
]

# Default source paths for the 8.3 family (the corpus captured on 8.3.27.x). A new family (e.g. 8.5) overrides
# these on the CLI — see `--source-*` in main(). The bundled *relative* layout is identical per version.
DEFAULT_MANAGER_TEMPLATES_SRC = REPO / "docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/manager_frame_templates.json"
DEFAULT_VALUE_READ_TEMPLATES_SRC = RUNTIME_CAPTURES.parent / "templates/tm-v1-open-plus-valueread/manager_frame_templates.json"
DEFAULT_ACCEPTED_MAPPINGS_SRC = REPO / "docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/accepted_mappings.json"


def sanitize_capture(src_dir: Path) -> list[str]:
    """Return minimal, portable, leak-free traffic.jsonl lines.

    `CaptureBootstrap.load` reads ONLY `event=="chunk"` records and, per record, `direction` + the payload
    (`payload_b64`, else `aggregate_*`). We keep exactly those three keys: this inlines any aggregate-only
    bytes (full portability, no external `.bin`) and drops every other field — including inert metadata that
    leaks a machine path (`connection_path`, `aggregate_path`, capture source paths, embedded feature text).
    The reconstructed manager/client frame lists are byte-identical to the original.
    """
    out: list[str] = []
    for line in (src_dir / "traffic.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("event") != "chunk":
            continue
        payload = rec.get("payload_b64")
        if not payload and rec.get("aggregate_path"):
            agg = src_dir / Path(rec["aggregate_path"]).name
            with agg.open("rb") as fh:
                fh.seek(int(rec["aggregate_offset"]))
                payload = base64.b64encode(fh.read(int(rec["byte_count"]))).decode("ascii")
        out.append(json.dumps(
            {"event": "chunk", "direction": rec.get("direction"), "payload_b64": payload},
            ensure_ascii=False,
        ))
    return out


def sanitize_template(src: Path, dst: Path) -> None:
    """Copy a frame-template JSON, dropping the inert top-level `capture_dir` (leaks a machine path).

    `ProtocolTemplates.load` reads only `templates`; the rest is metadata."""
    data = json.loads(src.read_text(encoding="utf-8-sig"))
    data.pop("capture_dir", None)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Bundle qa-mcp runtime assets into _bundled/<version>/.")
    ap.add_argument("--version", default="8.3",
                    help="platform version-family key — target dir is _bundled/<version>/ (default: 8.3)")
    ap.add_argument("--source-captures", type=Path, default=RUNTIME_CAPTURES,
                    help="dir holding the named capture subdirs (default: runtime/protocol-research/captures)")
    ap.add_argument("--source-manager-templates", type=Path, default=DEFAULT_MANAGER_TEMPLATES_SRC,
                    help="manager_frame_templates.json source for this version")
    ap.add_argument("--source-value-read-templates", type=Path, default=DEFAULT_VALUE_READ_TEMPLATES_SRC,
                    help="value-read templates JSON source for this version")
    ap.add_argument("--source-accepted-mappings", type=Path, default=DEFAULT_ACCEPTED_MAPPINGS_SRC,
                    help="accepted_mappings.json source for this version")
    args = ap.parse_args()

    # (source path, bundled relative path) — relative layout is identical across versions.
    data_files = [
        (args.source_manager_templates, "templates/manager_frame_templates.json"),
        (args.source_value_read_templates, "templates/value_read_templates.json"),
        (args.source_accepted_mappings, "accepted_mappings.json"),
    ]

    # Target ONLY this version's subdir — siblings (other versions) and the package __init__.py are preserved.
    target = BUNDLED / args.version
    if target.exists():
        shutil.rmtree(target)
    (target / "captures").mkdir(parents=True)
    (target / "templates").mkdir(parents=True)

    for cap in CAPTURES:
        src = args.source_captures / cap
        if not (src / "traffic.jsonl").exists():
            raise SystemExit(f"missing capture: {src}")
        dst = target / "captures" / cap
        dst.mkdir(parents=True, exist_ok=True)
        lines = sanitize_capture(src)
        (dst / "traffic.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"capture {cap}: {len(lines)} records")

    for src, rel in data_files:
        if not src.exists():
            raise SystemExit(f"missing data file: {src}")
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith("templates/"):
            sanitize_template(src, dst)
        else:
            shutil.copyfile(src, dst)
        print(f"data {rel}: {dst.stat().st_size} bytes")

    total = sum(p.stat().st_size for p in target.rglob("*") if p.is_file())
    print(f"bundled total for {args.version}: {total/1024/1024:.1f} MiB at {target}")


if __name__ == "__main__":
    main()
