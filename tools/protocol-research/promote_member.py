"""Promote an API member into the scope tracker after an accepted probe.

Updates ``api-inventory/mutation-evidence-map.json`` with the member's bucket and
evidence path, then regenerates ``scope-tracker.md``. This is the auto-promotion
step of the breadth pipeline: capture -> decode -> probe -> compare -> promote.

A member should only be promoted to ``accepted_reviewed`` when a Python-manager
probe reproduced the same action as the Vanessa reference (``probe-ordinal
accepted``); ``candidate`` records partial evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

DEFAULT_MAP = REPO_ROOT / "docs" / "protocol-research" / "api-inventory" / "mutation-evidence-map.json"
BUCKETS = ("accepted_reviewed", "accepted_seed", "candidate")


def promote(map_path: Path, api: str, bucket: str, evidence_path: str, note: str) -> dict:
    data = json.loads(map_path.read_text(encoding="utf-8-sig"))
    members = data.setdefault("members", [])
    entry = next((m for m in members if m.get("api") == api), None)
    if entry is None:
        entry = {"api": api}
        members.append(entry)
    entry["bucket"] = bucket
    if evidence_path:
        entry["evidence_path"] = evidence_path
    if note:
        entry["note"] = note
    map_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return data


def regenerate_tracker() -> None:
    # import here so the module is usable without the tracker deps loaded
    from scope_tracker import (  # type: ignore
        DEFAULT_CASE_MAP,
        DEFAULT_INVENTORY,
        DEFAULT_MUTATION_EVIDENCE,
        DEFAULT_OUTPUT,
        build_tracker,
        load_json,
        render_markdown,
    )

    inventory = load_json(DEFAULT_INVENTORY)
    case_map = load_json(DEFAULT_CASE_MAP)
    mutation_evidence = load_json(DEFAULT_MUTATION_EVIDENCE)
    result, unmatched = build_tracker(inventory, case_map, mutation_evidence)
    if unmatched:
        raise SystemExit(f"scope tracker has unmatched members: {unmatched}")
    DEFAULT_OUTPUT.write_text(
        render_markdown(result, inventory, mutation_evidence), encoding="utf-8", newline="\n"
    )
    counts = result["bucket_counts"]
    print(
        "scope-tracker: accepted_reviewed={ar} accepted_seed={as_} candidate={c} uncovered={u}".format(
            ar=counts["accepted_reviewed"], as_=counts["accepted_seed"],
            c=counts["candidate"], u=counts["uncovered"],
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="API member, e.g. TestedFormButton.Click")
    parser.add_argument("--bucket", required=True, choices=BUCKETS)
    parser.add_argument("--evidence", default="", help="evidence path (under docs/...)")
    parser.add_argument("--note", default="")
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()

    promote(args.map.resolve(), args.api, args.bucket, args.evidence, args.note)
    print(f"promoted {args.api} -> {args.bucket} in {args.map}")
    regenerate_tracker()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
