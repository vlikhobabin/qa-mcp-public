from __future__ import annotations

import base64
import json
import sys
import uuid
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from compare_probe_reference import (  # noqa: E402
    PLACEHOLDER_GUID,
    compare,
    compare_probe_by_ordinal,
    normalize_payload,
    phase_ordinals,
    session_guids,
    structural_signature,
)


def _write_capture(
    directory: Path,
    frames: list[tuple[str, bytes]],
    flags: tuple[str, str, str],
    status: str = "mutation_and_recovery_confirmed",
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    result = {
        "preFlag": flags[0],
        "postFlag": flags[1],
        "recoveryFlag": flags[2],
        "status": status,
        "phaseTimeline": [
            {
                "phase": "action_write",
                "started_at": "2026-06-11T10:00:00.000000Z",
                "finished_at": "2026-06-11T10:00:09.000000Z",
            }
        ],
    }
    (directory / "demo_catalog_mutation_result.json").write_text(
        json.dumps(result), encoding="utf-8"
    )
    lines = []
    for i, (direction, payload) in enumerate(frames):
        lines.append(
            json.dumps(
                {
                    "ts": f"2026-06-11T10:00:0{i % 9}.500000Z",
                    "event": "chunk",
                    "direction": direction,
                    "chunk_no": i + 1,
                    "byte_count": len(payload),
                    "payload_b64": base64.b64encode(payload).decode("ascii"),
                }
            )
        )
    (directory / "traffic.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return directory


def test_normalize_replaces_ascii_and_le_guid() -> None:
    guid = "d107afff-b899-4eea-90ba-4c50ac244bff"
    payload = b"X" + guid.encode("ascii") + b"Y" + uuid.UUID(guid).bytes_le + b"Z"
    out = normalize_payload(payload, [guid])
    assert guid.encode("ascii") not in out
    assert uuid.UUID(guid).bytes_le not in out
    assert PLACEHOLDER_GUID.encode("ascii") in out


def test_session_guids_collects_unique() -> None:
    frames = [
        {"payload": b"SecondaryFrame[d107afff-b899-4eea-90ba-4c50ac244bff]"},
        {"payload": b"ManagedForm[718969c8-336b-4565-a240-49a203cd1dfe]"},
        {"payload": b"again d107afff-b899-4eea-90ba-4c50ac244bff"},
    ]
    guids = session_guids(frames)
    assert guids == [
        "d107afff-b899-4eea-90ba-4c50ac244bff",
        "718969c8-336b-4565-a240-49a203cd1dfe",
    ]


def test_session_guids_detects_utf16le_only_guid() -> None:
    # A tabular-section delete carries the managed-form GUID only as UTF-16LE
    # form text. An ASCII-only scan misses it; session_guids must still find it
    # so normalize_payload can strip it and two runs collapse to one hash.
    guid = "4254cda8-782d-48de-97ef-644f7d2d83b1"
    payload = b"\x00\x10" + f"{guid}].ManagedForm[".encode("utf-16le")
    assert guid.encode("ascii") not in payload  # genuinely UTF-16LE only
    assert session_guids([{"payload": payload}]) == [guid]
    out = normalize_payload(payload, [guid], "client_to_manager")
    assert guid.encode("utf-16le") not in out


def test_structural_signature_orders_sizes_per_direction() -> None:
    frames = [
        {"direction": "manager_to_client", "payload": b"abc"},
        {"direction": "client_to_manager", "payload": b"de"},
        {"direction": "manager_to_client", "payload": b"fghi"},
    ]
    assert structural_signature(frames) == {
        "manager_to_client": [3, 4],
        "client_to_manager": [2],
    }


def test_compare_fully_stable_when_only_guids_differ(tmp_path: Path) -> None:
    g1 = "aaaaaaaa-0000-0000-0000-000000000001"
    g2 = "bbbbbbbb-0000-0000-0000-000000000002"
    body = b"WRITE.CommandPanel.Button "
    left = _write_capture(
        tmp_path / "left",
        [("manager_to_client", body + g1.encode()), ("client_to_manager", b"ok" + g1.encode())],
        ("Нет", "Да", "Нет"),
    )
    right = _write_capture(
        tmp_path / "right",
        [("manager_to_client", body + g2.encode()), ("client_to_manager", b"ok" + g2.encode())],
        ("Нет", "Да", "Нет"),
    )
    report = compare(left, right, "action_write", "stability")
    assert report["structural_match"] is True
    assert report["typed_result_match"] is True
    assert report["all_hashes_match"] is True
    assert report["verdict"] == "fully_stable"


def test_compare_divergent_on_different_typed_result(tmp_path: Path) -> None:
    body = b"WRITE.CommandPanel.Button"
    left = _write_capture(
        tmp_path / "l", [("manager_to_client", body)], ("Нет", "Да", "Нет")
    )
    right = _write_capture(
        tmp_path / "r", [("manager_to_client", body)], ("Нет", "Нет", "Нет")
    )
    report = compare(left, right, "action_write", "stability")
    assert report["typed_result_match"] is False
    assert report["verdict"] == "divergent"


def test_compare_acceptance_accepted_on_full_match(tmp_path: Path) -> None:
    body = b"WRITE.CommandPanel.Button"
    left = _write_capture(
        tmp_path / "ref", [("manager_to_client", body)], ("Нет", "Да", "Нет")
    )
    probe = _write_capture(
        tmp_path / "probe", [("manager_to_client", body)], ("Нет", "Да", "Нет")
    )
    report = compare(left, probe, "action_write", "acceptance")
    assert report["verdict"] == "accepted"


def test_probe_by_ordinal_accepts_python_manager_probe(tmp_path: Path) -> None:
    g1 = "aaaaaaaa-0000-0000-0000-000000000001"
    g2 = "bbbbbbbb-0000-0000-0000-000000000002"
    frames_left = [
        ("manager_to_client", b"WRITE.CommandPanel " + g1.encode()),
        ("client_to_manager", b"resp.ManagedForm " + g1.encode()),
    ]
    # probe: same structure, its own session guid (g2) -> normalizes to the same
    frames_right = [
        ("manager_to_client", b"WRITE.CommandPanel " + g2.encode()),
        ("client_to_manager", b"resp.ManagedForm " + g2.encode()),
    ]
    ref = _write_capture(tmp_path / "ref", frames_left, ("Нет", "Да", "Нет"))
    probe = _write_capture(tmp_path / "probe", frames_right, ("Нет", "Да", "Нет"))

    ordinals = phase_ordinals(ref, "action_write")
    assert ordinals["manager_to_client"] == [0]
    assert ordinals["client_to_manager"] == [0]

    report = compare_probe_by_ordinal(ref, probe, "action_write")
    assert report["structural_match"] is True
    assert report["all_hashes_match"] is True
    assert report["verdict"] == "accepted"


def test_probe_by_ordinal_mismatch_on_different_command(tmp_path: Path) -> None:
    ref = _write_capture(
        tmp_path / "ref", [("manager_to_client", b"WRITE.CommandPanel.Button")], ("Нет", "Да", "Нет")
    )
    probe = _write_capture(
        tmp_path / "probe", [("manager_to_client", b"DIFFERENT.OtherCommand!!")], ("Нет", "Да", "Нет")
    )
    report = compare_probe_by_ordinal(ref, probe, "action_write")
    assert report["verdict"] in ("candidate", "mismatch")
    assert report["all_hashes_match"] is False
