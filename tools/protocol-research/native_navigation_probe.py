"""Live chaining driver: drive the warehouse flow as synthesized navigation
operations (open_list / select_row / open_card) over a rebound transport.

The operation frames are routed through the package navigation-command
synthesizers; every other frame is rebound-replayed. ``--target-file`` re-targets
the selected row (same length) to demonstrate semantic operation control.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
import uuid
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
from qa_mcp.protocol.native_mutation import (  # noqa: E402
    build_poll_skip_set,
    manager_originated_guids,
    poll_frame_ordinals,
    run_replay_with_renderers,
)
from qa_mcp.protocol.navigation import (  # noqa: E402
    render_form_command,
    render_select_row_command,
)

CAPTURED_ROW = "Средний"
CAPTURED_BUTTON = "Изменить"


def find_ordinal(manager_chunks: list[dict], needle: bytes) -> int:
    for i, chunk in enumerate(manager_chunks):
        if needle in chunk["payload"]:
            return i
    raise RuntimeError(f"marker {needle!r} not found in manager stream")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15382)
    parser.add_argument("--target-file", type=Path, default=None,
                        help="UTF-8 file with the new row value (same length as Средний)")
    parser.add_argument("--keep-every-poll", type=int, default=1,
                        help="Thin the dominant poll frames, keeping every Nth (1 = keep all)")
    parser.add_argument("--synthesize-polls", action="store_true",
                        help="Construct the kept poll frames (fresh message id + live GUIDs) "
                             "instead of rebound-replaying them")
    parser.add_argument("--synthesize-write", action="store_true",
                        help="Construct the action-write frames via render_form_command "
                             "(fresh message id + live GUIDs); requires --write-template")
    parser.add_argument("--write-template", type=Path, default=None,
                        help="demo_catalog_mutation_write_template.json (locates the write frames)")
    parser.add_argument("--synthesize-handshake", action="store_true",
                        help="Regenerate the manager-originated handshake GUIDs (fresh session)")
    parser.add_argument("--read-timeout-sec", type=float, default=6.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=1.5)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    chunks = read_capture_chunks(args.capture_dir.resolve())
    manager_chunks = select_chunks(chunks, MANAGER_TO_CLIENT)
    client_chunks = select_chunks(chunks, CLIENT_TO_MANAGER)

    target_row = CAPTURED_ROW
    if args.target_file:
        target_row = args.target_file.read_text(encoding="utf-8").splitlines()[0]

    open_list_ord = find_ordinal(manager_chunks, "e1cib/list/".encode("utf-16le"))
    select_row_ord = find_ordinal(manager_chunks, CAPTURED_ROW.encode("utf-16le"))
    open_card_ord = find_ordinal(manager_chunks, CAPTURED_BUTTON.encode("utf-16le"))

    renderers = {
        # open_list: identity command, GUIDs rebound to the live session
        open_list_ord: lambda cap, rb: render_form_command(cap, guid_map=rb.guid_map),
        # select_row: re-target the row value (semantic operation)
        select_row_ord: lambda cap, rb: render_select_row_command(
            cap, old_value=CAPTURED_ROW, new_value=target_row, guid_map=rb.guid_map
        ),
        # open_card: identity Изменить button, GUIDs rebound
        open_card_ord: lambda cap, rb: render_form_command(cap, guid_map=rb.guid_map),
    }

    skip_ordinals = (
        build_poll_skip_set(manager_chunks, keep_every=args.keep_every_poll)
        if args.keep_every_poll > 1
        else set()
    )

    synthesized_writes = 0
    if args.synthesize_write:
        if not args.write_template:
            raise SystemExit("--synthesize-write requires --write-template")
        template = json.loads(args.write_template.read_text(encoding="utf-8"))
        by_hex = {c["payload"].hex(): i for i, c in enumerate(manager_chunks)}
        for frame in template["frames"]:
            idx = by_hex.get(frame["body_hex"])
            if idx is None or idx in skip_ordinals:
                continue
            # construct with a fresh per-frame nonce (offset 68 random); the
            # offset-2 SESSION ack GUID is rebound by guid_map, NOT regenerated
            renderers[idx] = lambda cap, rb: render_form_command(
                cap, guid_map=rb.guid_map, nonce=secrets.token_bytes(16)
            )
            synthesized_writes += 1

    synthesized_polls = 0
    if args.synthesize_polls:
        # construct each kept poll frame (fresh message id + live GUID rebind)
        for ordinal in poll_frame_ordinals(manager_chunks):
            if ordinal in skip_ordinals or ordinal in renderers:
                continue
            renderers[ordinal] = lambda cap, rb: render_form_command(
                cap, guid_map=rb.guid_map, nonce=secrets.token_bytes(16)
            )
            synthesized_polls += 1

    preseed = {}
    if args.synthesize_handshake:
        preseed = {g: str(uuid.uuid4()) for g in manager_originated_guids(manager_chunks, client_chunks)}

    summary = run_replay_with_renderers(
        host=args.host,
        port=args.port,
        manager_chunks=manager_chunks,
        client_chunks=client_chunks,
        renderers=renderers,
        skip_ordinals=skip_ordinals,
        preseed_guid_map=preseed,
        read_timeout_sec=args.read_timeout_sec,
        idle_timeout_sec=args.idle_timeout_sec,
    )
    summary["keep_every_poll"] = args.keep_every_poll
    summary["synthesized_poll_frames"] = synthesized_polls
    summary["synthesized_write_frames"] = synthesized_writes
    summary["synthesized_handshake_guids"] = len(preseed)
    summary["operations"] = {
        "open_list_ordinal": open_list_ord,
        "select_row_ordinal": select_row_ord,
        "open_card_ordinal": open_card_ord,
        "captured_row": CAPTURED_ROW,
        "target_row": target_row,
    }

    out_dir = args.output_dir or (args.capture_dir / "native-navigation" / timestamp_name())
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events = summary.pop("events")
    (out_dir / "native_navigation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "native_navigation_events.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
