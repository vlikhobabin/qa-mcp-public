"""Package-native mutation driver: navigate a live TestClient and send the
decoded write via ``render_write_frame`` instead of raw-replaying it.

The driver replays a captured flow's manager command frames with adaptive
per-session GUID rebinding (learned by first-appearance order from the live
responses) to reach the target form state. For the action-write frames it does
not replay the captured bytes — it **renders** them with
``qa_mcp.protocol.mutation.render_write_frame`` from the decoded write template,
substituting the live session GUIDs, so the write is constructed by the package.

Message id and sequence are kept from the captured write frame (the client
tolerates them, proven by the accepted full-flow replay); only the nonce is
regenerated and the session GUIDs are rebound. This isolates the claim to
"the package constructs the write frame and the live client executes it".
"""

from __future__ import annotations

import re
import socket
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .mutation import render_write_frame
from .transport import connect_testclient, read_protocol_available

# A frame renderer maps (captured_payload, rebinder) -> payload to send. It lets
# the chaining driver route specific operation frames through the navigation
# command synthesizers instead of raw rebound replay.
FrameRenderer = Callable[[bytes, "GuidRebinder"], bytes]

_GUID_RE = re.compile(
    rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def ascii_guids_in_order(payload: bytes) -> list[str]:
    seen: list[str] = []
    for match in _GUID_RE.findall(payload):
        guid = match.decode("ascii").lower()
        if guid not in seen:
            seen.append(guid)
    return seen


def substitute_guid_all_encodings(payload: bytes, captured: str, live: str) -> bytes:
    if captured == live:
        return payload
    out = payload
    for text in (captured, captured.upper()):
        out = out.replace(text.encode("ascii"), live.encode("ascii"))
        out = out.replace(text.encode("utf-16le"), live.encode("utf-16le"))
    try:
        out = out.replace(uuid.UUID(captured).bytes_le, uuid.UUID(live).bytes_le)
    except ValueError:
        pass
    return out


@dataclass
class GuidRebinder:
    """Learns captured->live GUID mappings by first-appearance order.

    The k-th distinct GUID seen in the captured client responses maps to the
    k-th distinct GUID seen in the live responses. Substitution covers ASCII /
    UTF-16LE path text and little-endian UUID bytes.
    """

    captured_order: list[str]
    guid_map: dict[str, str] = field(default_factory=dict)
    live_order: list[str] = field(default_factory=list)

    @classmethod
    def from_client_chunks(cls, client_chunks: list[dict[str, Any]]) -> "GuidRebinder":
        order: list[str] = []
        for chunk in client_chunks:
            for guid in ascii_guids_in_order(chunk["payload"]):
                if guid not in order:
                    order.append(guid)
        return cls(captured_order=order)

    def observe_response(self, response: bytes) -> list[str]:
        learned: list[str] = []
        for guid in ascii_guids_in_order(response):
            if guid not in self.live_order:
                self.live_order.append(guid)
                k = len(self.live_order) - 1
                if k < len(self.captured_order):
                    cap = self.captured_order[k]
                    if cap not in self.guid_map:
                        self.guid_map[cap] = guid
                        learned.append(f"{cap}->{guid}")
        return learned

    def apply(self, payload: bytes) -> bytes:
        out = payload
        for captured, live in self.guid_map.items():
            out = substitute_guid_all_encodings(out, captured, live)
        return out


def retarget_row_value(
    manager_chunks: list[dict[str, Any]], old_value: str, new_value: str
) -> tuple[list[dict[str, Any]], int]:
    """Re-target the navigation by replacing a row value in the command frames.

    The navigation command frames carry the selected row value as UTF-16LE text
    (decoded: the row-select command holds ``column 'Наименование' value '<row>'``).
    Replacing it with a same-length value re-points the flow at a different row
    without touching frame structure. The value must be the same length so the
    UTF-16LE byte length is preserved.
    """

    if len(old_value) != len(new_value):
        raise ValueError(
            f"retarget value length must match for in-place substitution: "
            f"{old_value!r}({len(old_value)}) != {new_value!r}({len(new_value)})"
        )
    old_b = old_value.encode("utf-16le")
    new_b = new_value.encode("utf-16le")
    out: list[dict[str, Any]] = []
    substitutions = 0
    for chunk in manager_chunks:
        payload = chunk["payload"]
        if old_b in payload:
            payload = payload.replace(old_b, new_b)
            substitutions += 1
        item = dict(chunk)
        item["payload"] = payload
        out.append(item)
    return out, substitutions


def _normalize_for_form(payload: bytes) -> bytes:
    """Zero per-frame dynamic fields and strip session GUIDs to a structural form."""

    import hashlib
    import uuid as _uuid

    body = bytearray(payload)
    for off, ln in ((2, 16), (19, 2), (68, 16)):
        if len(body) >= off + ln:
            body[off : off + ln] = b"\x00" * ln
    out = bytes(body)
    guids = set(_GUID_RE.findall(payload))
    for g in guids:
        text = g.decode("ascii").lower()
        for form in (text.encode("ascii"), text.upper().encode("ascii"), text.encode("utf-16le")):
            out = out.replace(form, b"\x00" * len(form))
        try:
            out = out.replace(_uuid.UUID(text).bytes_le, b"\x00" * 16)
        except ValueError:
            pass
    return hashlib.sha256(out).digest()


def poll_frame_ordinals(manager_chunks: list[dict[str, Any]]) -> list[int]:
    """Ordinals of the dominant repeated frame form (the managed-form state poll).

    These busy-wait poll frames dominate the flow (~75%); their normalized form
    is the single most common across the manager stream.
    """

    import collections

    forms = [_normalize_for_form(c["payload"]) for c in manager_chunks]
    counts = collections.Counter(forms)
    if not counts:
        return []
    dominant, _ = counts.most_common(1)[0]
    return [i for i, f in enumerate(forms) if f == dominant]


def build_poll_skip_set(manager_chunks: list[dict[str, Any]], keep_every: int) -> set[int]:
    """Skip set that thins the poll frames, keeping every ``keep_every``-th poll.

    Non-poll (semantic) frames are never skipped.
    """

    polls = poll_frame_ordinals(manager_chunks)
    skip: set[int] = set()
    for n, ordinal in enumerate(polls):
        if keep_every <= 1 or n % keep_every != 0:
            skip.add(ordinal)
    return skip


def run_replay_with_renderers(
    *,
    host: str,
    port: int,
    manager_chunks: list[dict[str, Any]],
    client_chunks: list[dict[str, Any]],
    renderers: dict[int, FrameRenderer],
    skip_ordinals: set[int] | None = None,
    preseed_guid_map: dict[str, str] | None = None,
    connect_timeout_sec: float = 10.0,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    stop_on_no_response: bool = True,
) -> dict[str, Any]:
    """Chaining driver: rebound-replay a flow, routing operation frames through
    their navigation-command synthesizers.

    For each manager ordinal present in ``renderers`` the renderer builds the
    frame (synthesized + live GUID rebind); every other frame is rebound-replayed.
    ``preseed_guid_map`` pre-binds manager-originated handshake GUIDs to fresh
    values so the manager establishes its own session (handshake synthesis).
    """

    rebinder = GuidRebinder.from_client_chunks(client_chunks)
    if preseed_guid_map:
        rebinder.guid_map.update(preseed_guid_map)
    skip_ordinals = skip_ordinals or set()
    events: list[dict[str, Any]] = []
    rendered = 0
    responded = 0
    sent = 0
    skipped = 0
    diverged_at: int | None = None

    with connect_testclient((host, port), timeout=connect_timeout_sec) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, read_timeout_sec, idle_timeout_sec))

        for index, chunk in enumerate(manager_chunks):
            if index in skip_ordinals:
                skipped += 1
                continue
            captured = chunk["payload"]
            renderer = renderers.get(index)
            if renderer is not None:
                payload = renderer(captured, rebinder)
                rendered += 1
            else:
                payload = rebinder.apply(captured)
            sock.sendall(payload)
            sent += 1
            response = _read_available(sock, read_timeout_sec, idle_timeout_sec)
            rebinder.observe_response(response)
            if response:
                responded += 1
            events.append(
                {
                    "send_index": index + 1,
                    "synthesized": renderer is not None,
                    "sent_bytes": len(payload),
                    "recv_bytes": len(response),
                }
            )
            if not response:
                diverged_at = index + 1
                if stop_on_no_response:
                    break

    return {
        "schema": "qa-mcp.synthesized-navigation-flow.v1",
        "manager_frames_total": len(manager_chunks),
        "frames_skipped": skipped,
        "frames_sent": sent,
        "exchanges_with_response": responded,
        "synthesized_frames": rendered,
        "guid_map_final_size": len(rebinder.guid_map),
        "diverged_at_send_index": diverged_at,
        "events": events,
    }


_NULL_GUID = "00000000-0000-0000-0000-000000000000"


def manager_originated_guids(
    manager_chunks: list[dict[str, Any]], client_chunks: list[dict[str, Any]]
) -> list[str]:
    """GUIDs the manager originates in the handshake (present in manager frames,
    never in client frames), excluding the null GUID.

    These are the manager's own session identifiers; for a fresh synthetic
    session they can be regenerated (the client echoes them). The client-assigned
    GUIDs (ack/SecondaryFrame/ManagedForm) are learned from responses instead.
    """

    man: list[str] = []
    for chunk in manager_chunks:
        for g in ascii_guids_in_order(chunk["payload"]):
            if g not in man:
                man.append(g)
    cli: set[str] = set()
    for chunk in client_chunks:
        cli.update(ascii_guids_in_order(chunk["payload"]))
    return [g for g in man if g not in cli and g != _NULL_GUID]


def _read_available(sock: socket.socket, first_timeout: float, idle_timeout: float) -> bytes:
    return read_protocol_available(sock, first_timeout, idle_timeout)


def _captured_message_id(payload: bytes) -> uuid.UUID | None:
    if len(payload) >= 18:
        try:
            return uuid.UUID(bytes_le=bytes(payload[2:18]))
        except ValueError:
            return None
    return None


def _captured_sequence(payload: bytes) -> int | None:
    if len(payload) >= 21:
        return int.from_bytes(payload[19:21], "little")
    return None


# Per-frame 16-byte field (a nonce/correlation value that varies across runs).
# It is preserved from the captured frame by default so a rendered write frame
# stays byte-identical to the captured one for the same target; ``render_write_frame``
# can regenerate it. (An earlier live probe wrongly blamed this field for a
# cross-session reproduction failure; the rendered write frames were later proven
# byte-identical to the accepted replay, so the field is not the cause.)
_NONCE_OFFSET = 68
_NONCE_LENGTH = 16


def _captured_nonce(payload: bytes) -> bytes | None:
    if len(payload) >= _NONCE_OFFSET + _NONCE_LENGTH:
        return bytes(payload[_NONCE_OFFSET : _NONCE_OFFSET + _NONCE_LENGTH])
    return None


def run_native_mutation_flow(
    *,
    host: str,
    port: int,
    manager_chunks: list[dict[str, Any]],
    client_chunks: list[dict[str, Any]],
    write_template_frames: list[dict[str, Any]],
    write_manager_ordinals: list[int],
    connect_timeout_sec: float = 10.0,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    stop_on_no_response: bool = True,
    regenerate_nonce: bool = False,
) -> dict[str, Any]:
    """Drive the flow live: rebound-replay to navigate, render the write frames.

    The write frames are rendered by ``render_write_frame`` with live-rebound
    session GUIDs. The offset-68 field is preserved from the captured frame by
    default so the rendered frame stays byte-identical to the captured one for
    the same target; ``regenerate_nonce=True`` regenerates it.
    """

    rebinder = GuidRebinder.from_client_chunks(client_chunks)
    write_ordinal_to_template = {ord_: i for i, ord_ in enumerate(sorted(write_manager_ordinals))}
    events: list[dict[str, Any]] = []
    rendered_writes = 0
    responded = 0
    diverged_at: int | None = None

    with connect_testclient((host, port), timeout=connect_timeout_sec) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        initial = _read_available(sock, read_timeout_sec, idle_timeout_sec)
        rebinder.observe_response(initial)

        for index, chunk in enumerate(manager_chunks):
            captured = chunk["payload"]
            if index in write_ordinal_to_template:
                tmpl = write_template_frames[write_ordinal_to_template[index]]
                payload = render_write_frame(
                    tmpl,
                    message_id=_captured_message_id(captured),
                    sequence=_captured_sequence(captured),
                    nonce=None if regenerate_nonce else _captured_nonce(captured),
                    session_guid_map=rebinder.guid_map,
                ).payload
                rendered = True
                rendered_writes += 1
            else:
                payload = rebinder.apply(captured)
                rendered = False
            sock.sendall(payload)
            response = _read_available(sock, read_timeout_sec, idle_timeout_sec)
            rebinder.observe_response(response)
            if response:
                responded += 1
            events.append(
                {
                    "send_index": index + 1,
                    "rendered_write": rendered,
                    "sent_bytes": len(payload),
                    "recv_bytes": len(response),
                    "guid_map_size": len(rebinder.guid_map),
                }
            )
            if not response:
                diverged_at = index + 1
                if stop_on_no_response:
                    break

    return {
        "schema": "qa-mcp.native-mutation-flow.v1",
        "manager_frames_total": len(manager_chunks),
        "exchanges_attempted": len(events),
        "exchanges_with_response": responded,
        "rendered_write_frames": rendered_writes,
        "guid_map_final_size": len(rebinder.guid_map),
        "diverged_at_send_index": diverged_at,
        "events": events,
    }
