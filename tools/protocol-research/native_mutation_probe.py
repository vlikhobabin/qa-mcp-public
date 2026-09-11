"""Live probe: drive the warehouse write with the package-native mutation driver.

Navigation frames are rebound-replayed; the action-write frames are rendered by
``qa_mcp.protocol.mutation.render_write_frame`` from the decoded write template,
so the write is constructed by the package rather than raw-replayed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from replay_probe import (  # type: ignore  # noqa: E402
    MANAGER_TO_CLIENT,
    CLIENT_TO_MANAGER,
    read_capture_chunks,
    select_chunks,
    timestamp_name,
)
from qa_mcp.protocol.native_mutation import run_native_mutation_flow  # noqa: E402


def write_manager_ordinals(manager_chunks: list[dict], template_frames: list[dict]) -> list[int]:
    """Locate each write-template frame in the manager stream by payload identity."""

    by_hex: dict[str, int] = {}
    for i, chunk in enumerate(manager_chunks):
        by_hex.setdefault(chunk["payload"].hex(), i)
    ordinals: list[int] = []
    for frame in template_frames:
        idx = by_hex.get(frame["body_hex"])
        if idx is None:
            raise RuntimeError(f"write template frame ordinal {frame.get('ordinal')} not found in manager stream")
        ordinals.append(idx)
    return ordinals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15382)
    parser.add_argument("--read-timeout-sec", type=float, default=6.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=1.5)
    parser.add_argument("--no-stop-on-no-response", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    chunks = read_capture_chunks(args.capture_dir.resolve())
    manager_chunks = select_chunks(chunks, MANAGER_TO_CLIENT)
    client_chunks = select_chunks(chunks, CLIENT_TO_MANAGER)

    template = json.loads(args.template.read_text(encoding="utf-8"))
    template_frames = template["frames"]
    ordinals = write_manager_ordinals(manager_chunks, template_frames)

    summary = run_native_mutation_flow(
        host=args.host,
        port=args.port,
        manager_chunks=manager_chunks,
        client_chunks=client_chunks,
        write_template_frames=template_frames,
        write_manager_ordinals=ordinals,
        read_timeout_sec=args.read_timeout_sec,
        idle_timeout_sec=args.idle_timeout_sec,
        stop_on_no_response=not args.no_stop_on_no_response,
    )
    summary["write_manager_ordinals"] = ordinals

    out_dir = args.output_dir or (args.capture_dir / "native-mutation" / timestamp_name())
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events = summary.pop("events")
    (out_dir / "native_mutation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "native_mutation_events.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
