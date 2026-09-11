"""Card 80 Fork-2 — write an arbitrary value into a form field, no Vanessa.

The value-commit needs an INPUT-AUTHORIZED session. That session is established by faithfully replaying a
genuine INPUT capture's WHOLE frame stream (handshake -> open form -> activate field -> SET edit-text ->
focus-change) against a live `/TESTCLIENT`, with live GUID rebind. The target value is then re-targeted in
the SET frame to an arbitrary new value. Proven live 2026-06-16 (card 80 BREAKTHROUGH): both the captured
value and an arbitrary new value commit (verified by read-back).

Earlier "off-wire wall" conclusions were artifacts of SPLICING input frames onto a read-only bootstrap +
tooling bugs (see card 80). The key is: replay an INPUT capture in full, do not splice.

This module is capture-template driven: a `WriteTemplate` describes one genuine INPUT capture (where the SET
value lives, which frames read it back). Variable-length values are supported via the 1C length-prefix
(LEB128-style varint immediately before the value); same-length needs no fixup, longer/shorter resizes the
frame by the length delta.
"""
from __future__ import annotations

import base64
import json
import re
import socket
from dataclasses import dataclass, field as _field
from pathlib import Path
from typing import Any

from .element_ref import (
    encode_element_path_block,
    extract_element_paths,
    extract_element_paths_utf16,
    retarget_element_leaf,
    retarget_element_leaf_any,
    retarget_element_leaf_reencode,
    retarget_element_segment,
)
from .navigation import retarget_nav_link
from .frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT, TAIL_MARKER
from .native_mutation import GuidRebinder
from .replay import (
    DEFAULT_SEND_TIMEOUT_SEC,
    ProtocolSendTimeout,
    ReplayOp,
    ReplaySession,
    SEND_TIMEOUT_REASON,
    send_all as _send_all,
)
from .transport import connect_testclient, read_protocol_available


def encode_1c_length(n: int) -> bytes:
    """1C string length prefix: LEB128-style varint (7 bits/byte, high bit = continuation)."""
    if n < 0:
        raise ValueError("length must be non-negative")
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def retarget_value(frame: bytes, old: str, new: str) -> bytes:
    """Replace a length-prefixed string value ``old`` -> ``new`` in a manager frame, FIXED-WIDTH aware.

    The wire form of an edit-string field is ``<varint content-length><value bytes><space padding>`` — a
    fixed-width buffer (the field's declared length): the length prefix is the actual content length, the
    value is right-padded with spaces to the buffer width. So the frame size is kept CONSTANT: the value is
    replaced and the trailing space padding is grown/shrunk to compensate (resizing the frame instead
    desyncs the session even though the SET is accepted — observed 2026-06-16). ``new`` must fit the buffer.

    Handles the UTF-8 form (the edit field) and, if present, a simple UTF-16LE occurrence. No-op if absent.
    """
    out = frame
    ob = old.encode("utf-8")
    nb = new.encode("utf-8")
    old_prefix = encode_1c_length(len(ob))
    needle = old_prefix + ob
    idx = out.find(needle)
    while idx >= 0:
        vend = idx + len(needle)
        pad = 0
        while vend + pad < len(out) and out[vend + pad] == 0x20:  # trailing space padding
            pad += 1
        region_len = len(needle) + pad  # prefix + value + padding (the fixed-width field slot)
        new_prefix = encode_1c_length(len(nb))
        new_pad = region_len - len(new_prefix) - len(nb)
        if new_pad < 0:
            raise ValueError(
                f"value {new!r} ({len(nb)} bytes) exceeds the field buffer width "
                f"({region_len - len(new_prefix)} bytes)"
            )
        new_region = new_prefix + nb + b"\x20" * new_pad
        out = out[:idx] + new_region + out[idx + region_len:]
        idx = out.find(needle, idx + len(new_region))
    # UTF-16LE occurrence (not the fixed-width edit field; simple swap if present)
    ob16 = old.encode("utf-16-le")
    if (encode_1c_length(len(ob16)) + ob16) in out:
        out = out.replace(encode_1c_length(len(ob16)) + ob16,
                          encode_1c_length(len(new.encode("utf-16-le"))) + new.encode("utf-16-le"))
    return out


def _read_chunks(capture_dir: Path, direction: str) -> list[bytes]:
    chunks: list[bytes] = []
    traffic = capture_dir / "traffic.jsonl"
    for line in traffic.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("event") != "chunk" or rec.get("direction") != direction:
            continue
        payload_b64 = rec.get("payload_b64")
        if payload_b64:
            chunks.append(base64.b64decode(payload_b64))
        else:
            with Path(rec["aggregate_path"]).open("rb") as f:
                f.seek(int(rec["aggregate_offset"]))
                chunks.append(f.read(int(rec["byte_count"])))
    return chunks


def _decode_1c_varint_at(data: bytes, offset: int) -> tuple[int, int] | None:
    length = 0
    shift = 0
    pos = offset
    while pos < len(data) and shift <= 21:
        byte = data[pos]
        pos += 1
        length |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return length, pos
        shift += 7
    return None


_EDITFIELD_ASCII = b"EditField["
_EDITFIELD_UTF16 = "EditField[".encode("utf-16-le")
_READBACK_SCAN_LIMIT = 4096


def _decode_wire_text(raw: bytes) -> str | None:
    if not raw:
        return None
    for encoding in ("utf-8", "utf-16-le", "latin1"):
        try:
            value = raw.decode(encoding).rstrip()
        except UnicodeDecodeError:
            continue
        if value and all(ch.isprintable() or ch.isspace() for ch in value):
            return value
    return None


def _value_terminator_ok(region: bytes, end: int) -> bool:
    if end >= len(region):
        return True
    marker = region[end]
    return marker in (0x20, 0xA1, 0xA3) or marker < 0x20 or marker >= 0x80


def _looks_like_utf16le_wire(raw: bytes) -> bool:
    if len(raw) < 2 or len(raw) % 2:
        return False
    high_bytes = raw[1::2]
    likely_high = sum(1 for byte in high_bytes if byte in (0x00, 0x04))
    return likely_high >= max(1, len(high_bytes) // 2)


def _readback_region(blob: bytes, start: int) -> bytes:
    end = min(len(blob), start + _READBACK_SCAN_LIMIT)
    tail = blob.find(TAIL_MARKER, start, end)
    if tail >= 0:
        end = min(end, tail)
    for marker in (_EDITFIELD_ASCII, _EDITFIELD_UTF16):
        nxt = blob.find(marker, start + 1, end)
        if nxt >= 0:
            end = min(end, nxt)
    return blob[start:end]


_DATE_READBACK_RE = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}$")


def _write_value_matches_readback(expected: str, readback: str | None) -> bool:
    if readback is None:
        return False
    req = (expected or "").strip()
    val = (readback or "").strip()
    if not req or not val:
        return False
    req_cf = req.casefold()
    val_cf = val.casefold()
    if req_cf == val_cf:
        return True
    return bool(_DATE_READBACK_RE.fullmatch(req) and val_cf.startswith(req_cf + " "))


def read_field_value_near(blob: bytes, field: str) -> str | None:
    """Best-effort committed-value read after ``EditField[<field>]`` value mode. Tolerant of both the
    ``\\xfa<len>`` and ``\\xe0..<len>`` value tails: scans for a length-prefixed printable run between the
    field anchor and the next field/tail boundary. This is length-aware, so it works for variable-length
    values (the tag metadata may itself contain printable bytes, so a plain 'first printable run' is wrong).

    Card 98 (2nd-config gate): the element path is encoded 1-byte ASCII when the field name is ASCII (the
    fixture, ``EditField[PF_EDIT_STRING]``) but UTF-16LE when the name has non-ASCII chars (any real
    Russian-named config, ``EditField[НаименованиеПолное]``). Tries the ASCII value-mode anchor first
    (unchanged for the fixture) then the UTF-16LE leaf, scanning past whatever value-mode tag follows."""
    candidates: list[bytes] = []
    try:
        candidates.append(b"EditField[" + field.encode("latin1") + b"]\x81\x81\x81")
    except UnicodeEncodeError:
        pass  # non-ASCII name has no 1-byte path; only the UTF-16LE leaf below applies
    candidates.append(("EditField[" + field + "]").encode("utf-16-le"))
    for anchor in candidates:
        i = blob.find(anchor)
        if i < 0:
            continue
        region = _readback_region(blob, i + len(anchor))
        for off in range(len(region)):
            parsed = _decode_1c_varint_at(region, off)
            if parsed is None:
                continue
            length, value_start = parsed
            if length < 1 or length > len(region) - value_start:
                continue
            byte_lengths = [length]
            doubled = length * 2
            if doubled <= len(region) - value_start:
                doubled_value = region[value_start: value_start + doubled]
                if _looks_like_utf16le_wire(doubled_value):
                    byte_lengths.insert(0, doubled)
            for byte_length in byte_lengths:
                value = region[value_start: value_start + byte_length]
                if len(value) != byte_length or not all(0x20 <= c <= 0x7E for c in value):
                    decoded = _decode_wire_text(value)
                else:
                    decoded = value.decode("latin1").rstrip()
                if decoded is not None and _value_terminator_ok(region, value_start + byte_length):
                    return decoded
    return None


def read_table_cell_value(blob: bytes, column: str) -> str | None:
    """Card 90 follow-up #3 — read a table-cell value from a response frame. A committed cell echoes via the
    column EditField + the value-SET tag: ``EditField[<column>] <3 counter bytes> e0 41 81 81 ba <varint-len>
    <value> <pad>`` (the same value buffer as a plain string SET). ``read_field_value_near`` misses it because
    it anchors on a fixed ``\\x81\\x81\\x81`` but the middle counter byte varies (e.g. ``\\x81\\x82\\x81``). This
    anchors on the leaf then the value-SET tag and decodes the 1C varint length. Returns the value (right-
    trimmed) or None. Decoded 2026-06-17 from the table-cell SET response."""
    anchor = b"EditField[" + column.encode("latin1") + b"]"
    tag = bytes.fromhex("e0418181ba")
    start = 0
    while True:
        i = blob.find(anchor, start)
        if i < 0:
            return None
        j = blob.find(tag, i, i + 48)  # the value-SET tag shortly after the leaf (skips the counter bytes)
        if j >= 0:
            off = j + len(tag)
            length = 0
            shift = 0
            while off < len(blob):  # 1C varint length (LEB128)
                b = blob[off]
                off += 1
                length |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            value = blob[off:off + length]
            if 1 <= length == len(value) and all(0x20 <= c <= 0x7E for c in value):
                return value.decode("latin1").rstrip()
        start = i + len(anchor)


def extract_user_messages(blob: bytes) -> list[str]:
    """Card 96 / E5 — read the user messages (`Сообщить` text / the "messages to user" panel) out of a client
    response blob. A message rides the client→manager stream as the envelope ``cb 53 9a <varint byte-len>
    <UTF-8 text>`` (decoded 2026-06-18 from the choose-from-list / choose-from-menu `Сообщить` callbacks —
    `cb 53 9a` is the user-message string envelope, the byte after it is the 1C LEB128 byte-length). Returns the
    message texts in first-seen order (right-trimmed), de-duplicating adjacent repeats (the same message can echo
    across consecutive poll responses). NOTE: byte-length-prefixed UTF-8 — proven on ASCII messages; a Cyrillic
    `Сообщить` should decode the same (UTF-8 handles it), but confirm the length-unit on a Cyrillic capture."""
    anchor = b"\xcb\x53\x9a"
    out: list[str] = []
    pos = 0
    while True:
        j = blob.find(anchor, pos)
        if j < 0:
            break
        off = j + len(anchor)
        length = 0
        shift = 0
        while off < len(blob):  # 1C varint length (LEB128, byte count)
            b = blob[off]
            off += 1
            length |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        text = blob[off:off + length]
        pos = off + max(length, 1)
        if length and len(text) == length:
            try:
                msg = text.decode("utf-8").rstrip()
            except UnicodeDecodeError:
                continue
            if not out or out[-1] != msg:
                out.append(msg)
    return out


@dataclass
class WriteTemplate:
    """Describes one genuine INPUT capture used as the write template."""

    capture_dir: Path
    field: str
    captured_value: str          # the value the genuine capture set (to be retargeted)
    read_frames: list[int]       # manager ordinals whose responses read the field back
    stop_after: int              # last manager ordinal to replay (single-shot write_form_value)
    default_value: str = ""      # the field's baseline (must be absent after a successful write)
    # NativeWriteSession (open-once, write-many): the setup prefix [0..setup_end] (handshake+open) is
    # replayed ONCE; each write re-sends the [write_block] (activate+SET+focus-change) + read_frames with
    # the binary message counter (offset 19-20 LE) bumped so the client does not see a backwards sequence.
    setup_end: int = 347
    write_block: tuple[int, int] = (348, 360)
    # Card 86c: when the field's genuine input had NO trailing focus-change (e.g. it was the LAST input — the
    # number in the card-80 two-input capture), the commit is synthesized by appending a partner field's
    # activate frames (focus-change = "activate ANY other field"). When set, write_block is activate+SET only.
    commit_block: tuple[int, int] | None = None


_EDITFIELD_RE = re.compile(rb"EditField\[([A-Za-z0-9_]+)\]")
_EF_UTF16 = "EditField[".encode("utf-16-le")
_RBRACKET_UTF16 = "]".encode("utf-16-le")


def editfields_in(frame: bytes) -> set[str]:
    """All ``EditField[<name>]`` element-path leaves in a frame, returned as decoded field NAMES (str).

    Card 98 (2nd-config gate): the wire encodes the element path as 1-byte ASCII when the field name is
    ASCII-only (``EditField[PF_EDIT_STRING]`` — the fixture) but as UTF-16LE when the name contains
    non-ASCII characters (``EditField[НаименованиеПолное]`` — any real Russian-named config). The original
    deriver matched only the ASCII form, so it silently found NO fields on a real config. This handles both,
    which is what lifts the write path off the ASCII-named fixture onto real configs."""
    out: set[str] = set()
    for m in _EDITFIELD_RE.finditer(frame):  # ASCII (1-byte) element path
        out.add(m.group(1).decode("latin1"))
    i = 0  # UTF-16LE element path (non-ASCII / Cyrillic field names)
    while True:
        j = frame.find(_EF_UTF16, i)
        if j < 0:
            break
        k = frame.find(_RBRACKET_UTF16, j + len(_EF_UTF16))
        if k < 0:
            break
        try:
            out.add(frame[j + len(_EF_UTF16):k].decode("utf-16-le"))
        except UnicodeDecodeError:
            pass
        i = k + 2
    return out


def derive_write_template(
    capture_dir: Path, field: str, captured_value: str, default_value: str = "",
    commit_partner_field: str | None = None, commit_partner_value: str | None = None,
) -> "WriteTemplate":
    """Auto-derive a WriteTemplate from a genuine INPUT capture (generalizes off the hard-coded fixture
    ordinals). Locates: the SET frame (carries the length-prefixed captured value), the field's activate
    prefix (contiguous EditField[field] frames just before the SET), the focus-change (the first frames
    after the SET that touch a DIFFERENT EditField), and the later read-back frames (EditField[field] after
    the focus-change). Works for any field whose genuine input was captured this way.

    Card 86c — ``commit_partner_field`` (+ ``commit_partner_value``): when the field's genuine input had NO
    trailing focus-change (it was the LAST input, e.g. the number in the card-80 two-input capture), pass
    another field that DOES have a genuine INPUT in the capture (its activate frames move focus). Its activate
    (the frames just before its SET, found via ``commit_partner_value``) is appended as the synthesized
    focus-change (commit = "activate any other field"). write_block is then activate+SET only, with a separate
    ``commit_block`` (the partner's activate) and read-back drawn from the field's value-mode read sweep.
    NOTE: the partner's READ-sweep frames do NOT move focus — only its ACTIVATE frames do; hence the partner's
    captured value is required to locate the activate (the frames immediately before the partner's SET)."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    fb = field  # field NAME as str; editfields_in() decodes BOTH the ASCII and the UTF-16LE element path
    val_seq = encode_1c_length(len(captured_value.encode("utf-8"))) + captured_value.encode("utf-8")

    def fields_in(p: bytes) -> set[str]:
        return editfields_in(p)

    set_ord = next((i for i, p in enumerate(mgr) if val_seq in p), None)
    if set_ord is None:
        raise ValueError(f"captured value {captured_value!r} (length-prefixed) not found in any SET frame")

    # activate prefix: walk back while the frame references EditField[field]
    a = set_ord
    while a - 1 >= 0 and fb in fields_in(mgr[a - 1]):
        a -= 1
    activate_start = a

    if commit_partner_field is not None:
        # SYNTHESIZED commit: the field's input has no trailing focus-change. write_block = activate+SET only;
        # commit_block = the partner field's ACTIVATE frames (the frames just before the partner's SET — its
        # read-sweep frames do NOT move focus); read-back = the field's value-mode read sweep.
        if commit_partner_value is None:
            raise ValueError("commit_partner_value is required to locate the partner's activate frames")
        pb = commit_partner_field  # partner field NAME as str (matched via editfields_in, both encodings)
        pset_seq = encode_1c_length(len(commit_partner_value.encode("utf-8"))) + commit_partner_value.encode("utf-8")
        pset = next((i for i, p in enumerate(mgr) if pset_seq in p), None)
        if pset is None:
            raise ValueError(f"commit partner SET ({commit_partner_value!r}) not found in the capture")
        pa = pset
        while pa - 1 >= 0 and pb in fields_in(mgr[pa - 1]):
            pa -= 1
        if pa > pset - 1:
            raise ValueError(f"commit partner {commit_partner_field!r} has no activate frames before its SET")
        commit_block = (pa, pset - 1)  # the partner's activate frames (move focus -> commit the target)
        # the target's full input block = its contiguous {field} frames (activate + the duplicated SET pair)
        target_end = set_ord
        while target_end + 1 < len(mgr) and fields_in(mgr[target_end + 1]) == {fb}:
            target_end += 1
        # setup must end BEFORE the earliest input (partner or target) so neither input is in the replayed
        # prefix; the inputs are then sent out-of-capture-order in write(): target block -> partner activate.
        pre_input = min(activate_start, pa)
        read_frames = [i for i in range(0, pre_input) if fields_in(mgr[i]) == {fb}][:3]
        return WriteTemplate(
            capture_dir=capture_dir, field=field, captured_value=captured_value,
            read_frames=read_frames, stop_after=target_end, default_value=default_value,
            setup_end=pre_input - 1, write_block=(activate_start, target_end), commit_block=commit_block,
        )

    # focus-change: skip the same-field SET pair, then find the first frame touching a DIFFERENT field
    f = set_ord + 1
    while f < len(mgr) and (not fields_in(mgr[f]) or fields_in(mgr[f]) == {fb}):
        f += 1
    if f >= len(mgr):
        raise ValueError("no focus-change (other-field activate) found after the SET")
    other = next(iter(fields_in(mgr[f]) - {fb}))
    g = f
    while g + 1 < len(mgr) and other in fields_in(mgr[g + 1]):
        g += 1
    focus_end = g

    # read-back: EditField[field] frames after the focus-change (the later value read)
    read_frames = [i for i in range(focus_end + 1, len(mgr)) if fb in fields_in(mgr[i])][:2]

    return WriteTemplate(
        capture_dir=capture_dir, field=field, captured_value=captured_value,
        read_frames=read_frames, stop_after=focus_end, default_value=default_value,
        setup_end=activate_start - 1, write_block=(activate_start, focus_end),
    )


class WriteRetargetError(ValueError):
    """Raised when a native write frame that should address a target field cannot be safely retargeted."""

    def __init__(self, base_field: str, target_field: str, reason: str) -> None:
        self.base_field = base_field
        self.target_field = target_field
        self.reason = reason
        super().__init__(reason)


def _retarget_failed_result(exc: WriteRetargetError, *, field: str) -> dict[str, Any]:
    return {
        "field": field,
        "base_field": exc.base_field,
        "target_field": exc.target_field,
        "error": "retarget_failed",
        "reason": exc.reason,
        "committed": False,
        "readback_value": None,
    }


def _frame_addresses_editfield(frame: bytes, field: str) -> bool:
    return _frame_addresses_leaf(frame, f"EditField[{field}]")


def build_write_frame(
    frame: bytes,
    captured_value: str,
    value: str,
    *,
    base_field: str,
    target_field: str,
    seq: int,
    allow_missing_leaf: bool = True,
) -> bytes:
    """Card 86b — assemble one write-block/read wire frame: (1) if ``target_field`` differs from the
    template's ``base_field``, re-target the element-address path leaf (`EditField[base]` -> `EditField[target]`,
    no-op on frames that do not carry that leaf — e.g. the focus-change frame, which addresses a different
    field), (2) re-target the captured value to ``value`` (fixed-width aware), (3) set the offset-19 counter.
    This is what lifts the commit-write off a per-field capture: structure from the base template, address
    from the live field name. Pure (no I/O) so it is unit-testable offline."""
    out = frame
    if target_field != base_field:
        try:
            out, _ = retarget_element_leaf_reencode(out, base_field, target_field)
        except ValueError as exc:
            if not allow_missing_leaf:
                raise WriteRetargetError(base_field, target_field, str(exc)) from exc
            # This frame does not address base_field, for example a focus-change frame.
    out = retarget_value(out, captured_value, value)
    out = _set_seq(out, seq)
    return out


def _set_seq(frame: bytes, seq: int) -> bytes:
    if len(frame) < 21:
        return frame
    b = bytearray(frame)
    b[19:21] = (seq & 0xFFFF).to_bytes(2, "little")
    return bytes(b)


def _seq_of(frame: bytes) -> int:
    return int.from_bytes(frame[19:21], "little") if len(frame) >= 21 else 0


def _open_replay_session(
    capture_dir: Path,
    *,
    host: str,
    port: int,
    read_timeout_sec: float,
    idle_timeout_sec: float,
    connect_timeout_sec: float,
) -> ReplaySession:
    return ReplaySession(
        _read_chunks(capture_dir, MANAGER_TO_CLIENT),
        _read_chunks(capture_dir, CLIENT_TO_MANAGER),
        host=host,
        port=port,
        read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec,
        connect_timeout_sec=connect_timeout_sec,
        connect=connect_testclient,
    )


class NativeWriteSession:
    """Open the form ONCE, then write many values on the same connection (no re-open => no multi-write
    desync). Replays the setup prefix on enter; each ``write`` re-sends the write block + read with the
    message counter bumped. Use as a context manager."""

    def __init__(self, template: WriteTemplate, host: str = "127.0.0.1", port: int = 15381,
                 read_timeout_sec: float = 0.6, idle_timeout_sec: float = 0.15,
                 connect_timeout_sec: float = 10.0,
                 setup_retargets: list[tuple[str, str]] | None = None) -> None:
        self.t = template
        self.host, self.port = host, port
        self.rt, self.it, self.ct = read_timeout_sec, idle_timeout_sec, connect_timeout_sec
        self._mgr = _read_chunks(template.capture_dir, MANAGER_TO_CLIENT)
        self._cli = _read_chunks(template.capture_dir, CLIENT_TO_MANAGER)
        self._sock: socket.socket | None = None
        self._rebinder: GuidRebinder | None = None
        self._replay: ReplaySession | None = None
        self._seq = 0
        # Card 90 row-addressing: fixed-width value swaps applied to the SETUP frames (e.g. a row-select's
        # genuine search value "PF_ROW_002_TEXT" -> "PF_ROW_003_TEXT" selects a different row on replay).
        self._setup_retargets = list(setup_retargets or [])

    def __enter__(self) -> "NativeWriteSession":
        replay = ReplaySession(
            self._mgr,
            self._cli,
            host=self.host,
            port=self.port,
            read_timeout_sec=self.rt,
            idle_timeout_sec=self.it,
            connect_timeout_sec=self.ct,
            connect=connect_testclient,
        )
        try:
            replay.__enter__()
            self._replay = replay
            self._sock = replay.sock
            self._rebinder = replay.rebinder

            def _retarget_setup(_index: int, frame: bytes) -> bytes:
                for old, new in self._setup_retargets:
                    frame = retarget_value(frame, old, new)  # fixed-width; no-op where the value is absent
                return frame

            self._seq = replay.replay_setup(self.t.setup_end, frame_fn=_retarget_setup)
            return self
        except Exception:
            replay.__exit__()
            self._sock = None
            self._rebinder = None
            self._replay = None
            self._seq = 0
            raise

    def _apply_frame(self, payload: bytes) -> bytes:
        replay = getattr(self, "_replay", None)
        if replay is not None:
            return replay.apply(payload)
        assert self._rebinder is not None
        return self._rebinder.apply(payload)

    def _exchange_wire(self, wire: bytes) -> bytes:
        replay = getattr(self, "_replay", None)
        if replay is not None:
            return replay.exchange(wire)
        assert self._sock is not None and self._rebinder is not None
        _send_all(self._sock, wire)
        resp = read_protocol_available(self._sock, self.rt, self.it)
        observe = getattr(self._rebinder, "observe_response", None)
        if observe is not None:
            observe(resp)
        return resp

    def write(self, value: str, field: str | None = None) -> dict[str, Any]:
        """Write ``value`` and commit it. ``field`` (card 86b) optionally targets a DIFFERENT field than the
        template's captured field, capture-free: the element-address path leaf is re-targeted to ``field`` in
        the activate/SET/read frames (same enclosing group). Read-back is parsed at the target field."""
        assert self._sock is not None and self._rebinder is not None
        target = field or self.t.field
        lo, hi = self.t.write_block
        commit = list(range(*(self.t.commit_block[0], self.t.commit_block[1] + 1))) if self.t.commit_block else []
        readback: str | None = None
        # write block (activate+SET) -> commit block (synthesized focus-change, card 86c) -> read-back
        for i in list(range(lo, hi + 1)) + commit + list(self.t.read_frames):
            if i >= len(self._mgr):
                continue
            payload = self._mgr[i]
            expected_leaf = _frame_addresses_editfield(payload, self.t.field)
            wire = self._apply_frame(payload)
            try:
                wire = build_write_frame(
                    wire, self.t.captured_value, value,
                    base_field=self.t.field, target_field=target, seq=self._seq,
                    allow_missing_leaf=not expected_leaf,
                )
            except WriteRetargetError as exc:
                return {**_retarget_failed_result(exc, field=target), "requested_value": value}
            self._seq += 1
            resp = self._exchange_wire(wire)
            if i in self.t.read_frames:
                got = read_field_value_near(resp, target)
                if got is not None:
                    readback = got
        # committed: the field now holds the requested value. Tolerant only of documented type formatting, such as
        # a date field reading back WITH a time component ("25.12.2027" -> "25.12.2027 0:00:00").
        committed = _write_value_matches_readback(value, readback)
        return {"requested_value": value, "readback_value": readback,
                "committed": committed, "field": target}

    def switch_page(self, target_page: str, base_page: str = "PF_PAGE_B") -> dict[str, Any]:
        """Card 86d — switch the active tab page, capture-free. Reuses the genuine page-switch command frames
        in this session's capture (located by ``base_page``), re-targeting the page-`Group` leaf to
        ``target_page``. The form must already be open (it is, after __enter__/any write). Returns
        {base_page, target_page, accepted}. (A page-switch has no value read-back; verify visually if needed.)"""
        assert self._sock is not None and self._rebinder is not None
        lo, hi = _find_page_switch(self._mgr, base_page)
        accepted = False
        for i in range(lo, hi + 1):
            wire = self._apply_frame(self._mgr[i])
            if target_page != base_page:
                wire, _ = retarget_element_leaf(wire, base_page, target_page, kind="Group")
            wire = _set_seq(wire, self._seq)
            self._seq += 1
            resp = self._exchange_wire(wire)
            accepted = accepted or bool(resp)
        return {"base_page": base_page, "target_page": target_page, "accepted": accepted}

    def toggle_checkbox(self, target_field: str, base_field: str = "PF_CHECKBOX_FALSE") -> dict[str, Any]:
        """Card 90 — toggle a Boolean checkbox, capture-free. A checkbox commits with NO value buffer: the
        wire just ACTIVATES the EditField (`…EditField[NAME] … e0 4b 55`, byte-identical for set & clear) and
        the server flips the Boolean + fires ПриИзменении. So this reuses the genuine toggle frames in this
        session's capture (located by ``base_field``), re-targeting the EditField leaf to ``target_field`` —
        the EditField twin of ``switch_page`` (``kind="EditField"`` vs ``"Group"``). The form must already be
        open. Returns {base_field, target_field, accepted}. (A toggle has no ASCII value read-back — verify via
        a server side-effect field, e.g. PF_LAST_ACTION, or a screenshot.)"""
        assert self._sock is not None and self._rebinder is not None
        lo, hi = _find_checkbox_toggle(self._mgr, base_field)
        accepted = False
        for i in range(lo, hi + 1):
            wire = self._apply_frame(self._mgr[i])
            if target_field != base_field:
                wire, _ = retarget_element_leaf(wire, base_field, target_field, kind="EditField")
            wire = _set_seq(wire, self._seq)
            self._seq += 1
            resp = self._exchange_wire(wire)
            accepted = accepted or bool(resp)
        return {"base_field": base_field, "target_field": target_field, "accepted": accepted}

    def set_choice(self, variant: str, base_field: str = "PF_CHOICE_MODE",
                   captured_variant: str = "PF_CHOICE_A", target_field: str | None = None) -> dict[str, Any]:
        """Card 90 — set a radio (Переключатель) to ``variant``, capture-free. Unlike a checkbox (value-free
        toggle), a choice ACTIVATES the EditField and carries the selected variant as a length-prefixed string
        (`…EditField[NAME] … e0 4b 53 <0x9a><len><variant-value-name>`). So this re-targets the genuine choice
        block's EditField leaf (to ``target_field``) AND the variant string (``captured_variant`` -> ``variant``,
        same-length, via build_write_frame). The variant is addressed by its VALUE NAME (e.g. PF_CHOICE_C).
        Returns {base_field, target_field, variant, accepted}. (The choice value reads back as ASCII — verify
        with read_form_value/read_field_value_near.)"""
        assert self._sock is not None and self._rebinder is not None
        target = target_field or base_field
        lo, hi = _find_checkbox_toggle(self._mgr, base_field)  # same contiguous EditField[base] run
        accepted = False
        for i in range(lo, hi + 1):
            payload = self._mgr[i]
            expected_leaf = _frame_addresses_editfield(payload, base_field)
            wire = self._apply_frame(payload)
            try:
                wire = build_write_frame(wire, captured_variant, variant,
                                         base_field=base_field, target_field=target, seq=self._seq,
                                         allow_missing_leaf=not expected_leaf)
            except WriteRetargetError as exc:
                return {**_retarget_failed_result(exc, field=target), "variant": variant, "accepted": False}
            self._seq += 1
            resp = self._exchange_wire(wire)
            accepted = accepted or bool(resp)
        return {"base_field": base_field, "target_field": target, "variant": variant, "accepted": accepted}

    def set_table_cell(self, value: str, *, column: str | None = None, table: str | None = None,
                       base_table: str = "PF_TABLE_ITEMS") -> dict[str, Any]:
        """Card 90 / 86e — write ``value`` into a table cell (the ACTIVE row), capture-free. A table-cell SET
        is byte-identical to a plain string-field SET (decode 2026-06-17): only the element path differs — the
        column is the `EditField` leaf inside a `Table[<table>]` segment and there is NO row index, so the SET
        commits into the active/selected row. Reuses the card-86c commit machinery: this re-targets the genuine
        cell SET's column leaf (``column``, defaults to the captured column) + the value (fixed-width) + the
        offset-19 counter via ``build_write_frame``, optionally the `Table[…]` segment (``table``), then sends
        the synthesized focus-change (``commit_block``) to commit. The target row must already be active (the
        captured setup adds one row; select/add the target row first for other rows). Returns
        {requested_value, readback_value, committed, column, table}. The cell read-back IS reliable (card 90
        follow-up #3): the SET response echoes the committed cell value via the column EditField + value-SET tag,
        parsed by ``read_table_cell_value`` — so ``readback_value``/``committed`` reflect the actual write."""
        assert self._sock is not None and self._rebinder is not None
        target_col = column or self.t.field
        target_tbl = table or base_table
        lo, hi = self.t.write_block
        commit = list(range(self.t.commit_block[0], self.t.commit_block[1] + 1)) if self.t.commit_block else []
        readback: str | None = None
        for i in list(range(lo, hi + 1)) + commit + list(self.t.read_frames):
            if i >= len(self._mgr):
                continue
            payload = self._mgr[i]
            expected_leaf = _frame_addresses_editfield(payload, self.t.field)
            wire = self._apply_frame(payload)
            try:
                wire = build_write_frame(wire, self.t.captured_value, value,
                                         base_field=self.t.field, target_field=target_col, seq=self._seq,
                                         allow_missing_leaf=not expected_leaf)
            except WriteRetargetError as exc:
                return {**_retarget_failed_result(exc, field=target_col),
                        "requested_value": value, "column": target_col, "table": target_tbl}
            if target_tbl != base_table:
                try:
                    wire, _ = retarget_element_segment(wire, base_table, target_tbl, kind="Table")
                except ValueError:
                    pass  # this frame (e.g. the focus-change) does not address the table segment
            self._seq += 1
            resp = self._exchange_wire(wire)
            # Card 90 follow-up #3: the SET response echoes the committed cell value via the column EditField +
            # value-SET tag (grid read-back) — read_table_cell_value parses it (read_field_value_near misses it).
            got = read_table_cell_value(resp, target_col)
            if got is None and i in self.t.read_frames:
                got = read_field_value_near(resp, target_col)
            if got is not None:
                readback = got
        committed = _write_value_matches_readback(value, readback)
        return {"requested_value": value, "readback_value": readback, "committed": committed,
                "column": target_col, "table": target_tbl}

    def __exit__(self, *a: object) -> None:
        if self._replay is not None:
            self._replay.__exit__(*a)
            self._replay = None
            self._sock = None
            self._rebinder = None
        elif self._sock is not None:
            self._sock.close()
            self._sock = None
        self._rebinder = None


def _find_page_switch(mgr: list[bytes], base_page: str) -> tuple[int, int]:
    """Locate the genuine page-switch COMMAND for ``base_page``: the first frame whose element path leaf is
    exactly ``Group[base_page]`` (the page activated as the target), plus its contiguous run. Card 86d."""
    leaf = f"Group[{base_page}]"
    start = next((i for i, p in enumerate(mgr)
                  if any(path.endswith(leaf) for path in extract_element_paths(p))), None)
    if start is None:
        raise ValueError(f"no page-switch command (path leaf {leaf!r}) found in the capture")
    end = start
    while end + 1 < len(mgr) and any(path.endswith(leaf) for path in extract_element_paths(mgr[end + 1])):
        end += 1
    return start, end


@dataclass
class PageSwitchTemplate:
    """A genuine page-switch command in a capture (card 86d). ``setup_end`` opens the form; ``switch_block``
    is the genuine switch command for ``base_page`` (re-targeted to any page via the page-`Group` leaf)."""

    capture_dir: Path
    base_page: str
    setup_end: int
    switch_block: tuple[int, int]


def derive_page_switch(capture_dir: Path, base_page: str = "PF_PAGE_B") -> "PageSwitchTemplate":
    """Auto-derive a page-switch template from a genuine capture that switched to ``base_page``."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_page_switch(mgr, base_page)
    return PageSwitchTemplate(capture_dir=capture_dir, base_page=base_page, setup_end=lo - 1, switch_block=(lo, hi))


def switch_page(
    template: PageSwitchTemplate,
    target_page: str,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free page-switch (card 86d): open the form (replay setup) and send the genuine
    switch command re-targeted to ``target_page`` (page-`Group` leaf). Returns {base_page, target_page,
    accepted}."""
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        for i in range(template.switch_block[0], template.switch_block[1] + 1):
            wire = replay.apply(mgr[i])
            if target_page != template.base_page:
                wire, _ = retarget_element_leaf(wire, template.base_page, target_page, kind="Group")
            wire = _set_seq(wire, seq); seq += 1
            resp = replay.exchange(wire)
            accepted = accepted or bool(resp)
    return {"base_page": template.base_page, "target_page": target_page, "accepted": accepted}


def _find_checkbox_toggle(mgr: list[bytes], base_field: str) -> tuple[int, int]:
    """Locate the genuine checkbox TOGGLE command for ``base_field``: the first frame whose element path leaf
    is exactly ``EditField[base_field]``, plus its contiguous run (focus + the e0-4b-55 toggle + read). The
    EditField analog of ``_find_page_switch``. Card 90."""
    leaf = f"EditField[{base_field}]"
    start = next((i for i, p in enumerate(mgr)
                  if any(path.endswith(leaf) for path in extract_element_paths(p))), None)
    if start is None:
        raise ValueError(f"no checkbox toggle command (path leaf {leaf!r}) found in the capture")
    end = start
    while end + 1 < len(mgr) and any(path.endswith(leaf) for path in extract_element_paths(mgr[end + 1])):
        end += 1
    return start, end


@dataclass
class CheckboxToggleTemplate:
    """A genuine checkbox-toggle command in a capture (card 90). ``setup_end`` opens the form; ``toggle_block``
    is the genuine value-free toggle for ``base_field`` (re-targeted to any checkbox via the EditField leaf)."""

    capture_dir: Path
    base_field: str
    setup_end: int
    toggle_block: tuple[int, int]


def derive_checkbox_toggle(capture_dir: Path, base_field: str = "PF_CHECKBOX_FALSE") -> "CheckboxToggleTemplate":
    """Auto-derive a checkbox-toggle template from a genuine capture that toggled ``base_field``."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_checkbox_toggle(mgr, base_field)
    return CheckboxToggleTemplate(capture_dir=capture_dir, base_field=base_field, setup_end=lo - 1, toggle_block=(lo, hi))


def toggle_checkbox(
    template: CheckboxToggleTemplate,
    target_field: str,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free checkbox toggle (card 90): open the form (replay setup) and send the genuine
    value-free toggle command re-targeted to ``target_field`` (EditField leaf). Returns {base_field,
    target_field, accepted}. The EditField twin of ``switch_page``."""
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        for i in range(template.toggle_block[0], template.toggle_block[1] + 1):
            wire = replay.apply(mgr[i])
            if target_field != template.base_field:
                wire, _ = retarget_element_leaf(wire, template.base_field, target_field, kind="EditField")
            wire = _set_seq(wire, seq); seq += 1
            resp = replay.exchange(wire)
            accepted = accepted or bool(resp)
    return {"base_field": template.base_field, "target_field": target_field, "accepted": accepted}


@dataclass
class ChoiceSetTemplate:
    """A genuine radio choice-set in a capture (card 90). ``setup_end`` opens the form; ``choice_block`` is the
    genuine activate+choose block for ``base_field`` carrying ``captured_variant`` (re-targeted: the EditField
    leaf to any radio, the variant string to any value name)."""

    capture_dir: Path
    base_field: str
    captured_variant: str
    setup_end: int
    choice_block: tuple[int, int]


def derive_choice_set(capture_dir: Path, base_field: str = "PF_CHOICE_MODE",
                      captured_variant: str = "PF_CHOICE_A") -> "ChoiceSetTemplate":
    """Auto-derive a choice-set template from a genuine capture that set ``base_field`` to ``captured_variant``.
    The block is the first contiguous EditField[base_field] run (activate + the e0-4b-53 choose frames); it must
    carry the length-prefixed ``captured_variant`` string."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_checkbox_toggle(mgr, base_field)
    var_seq = encode_1c_length(len(captured_variant.encode())) + captured_variant.encode()
    if not any(var_seq in mgr[i] for i in range(lo, hi + 1)):
        raise ValueError(f"captured variant {captured_variant!r} not found in the EditField[{base_field}] block")
    return ChoiceSetTemplate(capture_dir=capture_dir, base_field=base_field, captured_variant=captured_variant,
                             setup_end=lo - 1, choice_block=(lo, hi))


def set_choice(
    template: ChoiceSetTemplate,
    variant: str,
    *,
    target_field: str | None = None,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free radio choice-set (card 90): open the form (replay setup) and send the genuine
    choose block re-targeted to ``target_field`` (EditField leaf) with the variant string swapped to
    ``variant`` (same-length, via build_write_frame). Returns {base_field, target_field, variant, accepted}."""
    target = target_field or template.base_field
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        for i in range(template.choice_block[0], template.choice_block[1] + 1):
            payload = mgr[i]
            expected_leaf = _frame_addresses_editfield(payload, template.base_field)
            wire = replay.apply(payload)
            try:
                wire = build_write_frame(wire, template.captured_variant, variant,
                                         base_field=template.base_field, target_field=target, seq=seq,
                                         allow_missing_leaf=not expected_leaf)
            except WriteRetargetError as exc:
                return {**_retarget_failed_result(exc, field=target), "variant": variant, "accepted": False}
            seq += 1
            resp = replay.exchange(wire)
            accepted = accepted or bool(resp)
    return {"base_field": template.base_field, "target_field": target, "variant": variant, "accepted": accepted}


def _find_open_list(mgr: list[bytes], base_link: str) -> tuple[int, int]:
    """Locate the genuine OPEN-LIST command for ``base_link``: the contiguous run of frames carrying the
    length-prefixed UTF-16LE nav link (`e1cib/list/<path>`). Card 90 §7 Step 4."""
    needle = base_link.encode("utf-16le")
    idxs = [i for i, p in enumerate(mgr) if needle in p]
    if not idxs:
        raise ValueError(f"no open-list command (nav link {base_link!r}) found in the capture")
    lo = idxs[0]
    hi = lo
    while hi + 1 in idxs:
        hi += 1
    return lo, hi


@dataclass
class OpenListTemplate:
    """A genuine open-list command in a capture (card 90 §7 Step 4). ``setup_end`` opens the fixture form;
    ``open_list_block`` is the genuine nav-link open command for ``base_link`` (re-targeted to any catalog via
    ``navigation.retarget_nav_link``)."""

    capture_dir: Path
    base_link: str
    setup_end: int
    open_list_block: tuple[int, int]


def derive_open_list(capture_dir: Path,
                     base_link: str = "e1cib/list/Справочник.Товары") -> "OpenListTemplate":
    """Auto-derive an open-list template from a genuine capture that opened the ``base_link`` list."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_open_list(mgr, base_link)
    return OpenListTemplate(capture_dir=capture_dir, base_link=base_link, setup_end=lo - 1, open_list_block=(lo, hi))


def open_list(
    template: OpenListTemplate,
    target_catalog: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free OPEN-LIST (card 90 §7 Step 4): open the fixture form (replay the genuine setup)
    and send the genuine nav-link open command, optionally re-targeted to ``target_catalog`` (e.g.
    ``"Справочник.Склады"``) via ``retarget_nav_link``. A separate list WINDOW opens — there is no value
    read-back, so verify visually (capture_screenshot). Returns {base_link, target_link, accepted}.
    Live-proven 2026-06-17 (the Товары catalog list window opened on a fresh native client)."""
    base_link = template.base_link
    target_link = f"e1cib/list/{target_catalog}" if target_catalog else base_link
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        for i in range(template.open_list_block[0], template.open_list_block[1] + 1):
            frame = mgr[i]
            if target_link != base_link:
                frame, _ = retarget_nav_link(frame, base_link, target_link)
            wire = _set_seq(replay.apply(frame), seq); seq += 1
            resp = replay.exchange(wire)
            accepted = accepted or bool(resp)
    return {"base_link": base_link, "target_link": target_link, "accepted": accepted}


def _frame_addresses_leaf(frame: bytes, leaf: str) -> bool:
    """True if ``frame`` carries the element-path leaf ``leaf`` (e.g. ``Button[Список]``) in EITHER encoding:
    ASCII/latin1 (fixture `PF_*` names) or UTF-16LE (Cyrillic names — the dynlist's auto-generated commands /
    any real config; card 98). The UTF-16 element path is not produced by the ASCII ``extract_element_paths``,
    so check the raw UTF-16 leaf bytes too."""
    if any(path.endswith(leaf) for path in extract_element_paths(frame)):
        return True
    return leaf.encode("utf-16-le") in frame


def _find_element_command(mgr: list[bytes], leaf: str) -> tuple[int, int]:
    """Locate the genuine COMMAND invoke addressed at element-path ``leaf`` (e.g. ``Button[PF_ADD_ROW]`` for a
    form-command button, ``Button[ДенамическийСписокИерархияСписок]`` for a Cyrillic view-mode command, or
    ``Table[PF_TABLE_ITEMS]`` for a table-level command like select-all): the LAST contiguous run of frames whose
    element-path leaf is ``leaf`` (the form-open render is an EARLIER run; the invoke — `…<leaf> 88 8x 81 20 20
    20` — is the last). Encoding-agnostic (ASCII or UTF-16LE). Card 90 follow-up #2 / card 97 #1 / change 4."""
    idxs = [i for i, p in enumerate(mgr) if _frame_addresses_leaf(p, leaf)]
    if not idxs:
        raise ValueError(f"no element command (path leaf {leaf!r}) found in the capture")
    runs: list[list[int]] = []
    for i in idxs:
        if runs and i == runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    last = runs[-1]
    return last[0], last[-1]


def _find_command_click(mgr: list[bytes], button: str) -> tuple[int, int]:
    """Locate the genuine COMMAND CLICK for ``button`` (the `Button[button]` leaf). Card 90 follow-up #2."""
    return _find_element_command(mgr, f"Button[{button}]")


@dataclass
class CommandClickTemplate:
    """A genuine form-command (button) click in a capture (card 90 follow-up #2). ``setup_end`` opens the form;
    ``click_block`` is the genuine click for ``base_button`` (re-targeted to any button via the `Button` leaf)."""

    capture_dir: Path
    base_button: str
    setup_end: int
    click_block: tuple[int, int]


def derive_command_click(capture_dir: Path, base_button: str = "PF_ADD_ROW") -> "CommandClickTemplate":
    """Auto-derive a command-click template from a genuine capture that clicked ``base_button``."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_command_click(mgr, base_button)
    return CommandClickTemplate(capture_dir=capture_dir, base_button=base_button, setup_end=lo - 1, click_block=(lo, hi))


def derive_table_command(capture_dir: Path, table: str = "PF_TABLE_ITEMS") -> "CommandClickTemplate":
    """Card 97 #1 (multi-select) — auto-derive a TABLE-level command template (e.g. genuine "select all rows"
    `…Table[<table>] 88 82 81 20 20 20`) from a capture whose first table action invoked it. The invoke is
    addressed at the `Table[<table>]` element (NOT a Button), so this is the table twin of
    ``derive_command_click``; ``click_command(template, None)`` replays the setup (form-open) + the invoke with
    NO leaf retarget. ``base_button`` is set to the `Table[…]` leaf so any retarget is a no-op for it."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_element_command(mgr, f"Table[{table}]")
    return CommandClickTemplate(capture_dir=capture_dir, base_button=f"Table[{table}]", setup_end=lo - 1, click_block=(lo, hi))


def click_command(
    template: CommandClickTemplate,
    target_button: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free FORM-COMMAND (button) click (card 90 follow-up #2): open the form (replay the
    genuine setup) and send the genuine click command re-targeted to ``target_button`` (the `Button` leaf — the
    Button twin of switch_page/toggle_checkbox). A click has no value read-back — verify via a server side-effect
    field (e.g. PF_LAST_ACTION) or capture_screenshot. Returns {base_button, target_button, accepted}.
    ``add_table_row`` is this clicking the fixture's `PF_ADD_ROW` command (server-side add a marked, active row;
    live-proven 2026-06-17)."""
    target = target_button or template.base_button
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        for i in range(template.click_block[0], template.click_block[1] + 1):
            wire = replay.apply(mgr[i])
            if target != template.base_button:
                wire, _ = retarget_element_leaf_any(wire, template.base_button, target, kind="Button")
            wire = _set_seq(wire, seq); seq += 1
            resp = replay.exchange(wire)
            accepted = accepted or bool(resp)
    return {"base_button": template.base_button, "target_button": target, "accepted": accepted}


_VIEW_MODE_SUFFIX = {
    "список": "Список", "list": "Список", "flat": "Список",
    "дерево": "Дерево", "tree": "Дерево",
    "иерархический": "ИерархическийСписок", "иерархическийсписок": "ИерархическийСписок",
    "hierarchical": "ИерархическийСписок", "hierarchy": "ИерархическийСписок",
}


def set_list_view(
    capture_dir: Path,
    mode: str,
    dynlist: str = "ДенамическийСписокИерархия",
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Switch a dynamic list's VIEW MODE (Список / Дерево / Иерархический) natively — card 97 change 4, the
    «Режим просмотра» grouping toggle (no Vanessa). These are standard FORM BUTTONS (`<dynlist>Список` /
    `…Дерево` / `…ИерархическийСписок`); clicking one is the `…Button[<name>] 88 82 81 20 20 20` command family
    (the same invoke as the row ops / close-window), with the Button leaf encoded **UTF-16LE** (Cyrillic name).
    Replays the genuine click from ``capture_dir`` (which clicked Список then ИерархическийСписок), re-targeting
    the Button leaf to the requested mode: **Дерево** is a same-char-length UTF-16 retarget of Список;
    **Список / Иерархический** are verbatim captured clicks. No value read-back — the list REPRESENTATION changes
    (tree vs flat vs hierarchy; verify by screenshot). Returns {mode, button, accepted}."""
    key = mode.strip().lower().replace(" ", "")
    if key not in _VIEW_MODE_SUFFIX:
        raise ValueError(f"unknown view mode {mode!r}; expected one of Список / Дерево / Иерархический")
    suffix = _VIEW_MODE_SUFFIX[key]
    target_button = dynlist + suffix
    # base = a CAPTURED button of the SAME char length: Список & Дерево share length (the verbatim Список click
    # drives both — Дерево via same-length UTF-16 retarget); Иерархический is its own captured click.
    base_button = dynlist + ("ИерархическийСписок" if suffix == "ИерархическийСписок" else "Список")
    template = derive_command_click(capture_dir, base_button)
    res = click_command(
        template, None if target_button == base_button else target_button,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    )
    return {"mode": suffix, "button": target_button, "accepted": res.get("accepted")}


def _find_choose_from_list(mgr: list[bytes], base_command: str, captured_value: str) -> tuple[int, int]:
    """Locate the genuine CHOOSE-FROM-LIST flow for ``base_command`` (the form command that raises
    ПоказатьВыборИзСписка): from the command-CLICK frame (path leaf ``Button[base_command]``, the last run —
    reusing ``_find_command_click``) through the PICK frame carrying the length-prefixed ``captured_value``
    after the choose tag ``e0 4b 53``. Card 96 (E2). The popup reuses the form window (the pick is addressed at
    the ManagedForm, NO new SecondaryFrame), so only the picked value is re-targeted — there is no element leaf."""
    click_lo, _ = _find_command_click(mgr, base_command)
    val_seq = encode_1c_length(len(captured_value.encode())) + captured_value.encode()
    picks = [i for i in range(click_lo, len(mgr)) if b"\xe0\x4b\x53" in mgr[i] and val_seq in mgr[i]]
    if not picks:
        raise ValueError(f"no choice pick (e0 4b 53 + {captured_value!r}) found after the "
                         f"Button[{base_command}] click in the capture")
    hi = picks[-1]
    # The pick's result is a user message (Сообщить); the client emits the `PF_CHOICE=...` frame only when the
    # manager polls the form AFTER the pick. So extend the block to the post-pick substantive read frames (the
    # message poll), stopping at the trailing 4-byte control frames. These reads carry no captured value, so the
    # value re-target is a no-op on them — they just elicit the result message for the commit check.
    while hi + 1 < len(mgr) and len(mgr[hi + 1]) > 16:
        hi += 1
    return click_lo, hi


@dataclass
class ChooseFromListTemplate:
    """A genuine choose-from-list flow in a capture (card 96 / E2). ``setup_end`` opens the form; ``choose_block``
    spans the command CLICK (raises ПоказатьВыборИзСписка) through the PICK of ``captured_value`` (re-targeted to
    any list item by value name). The popup reuses the form window — no new-window GUID bind needed."""

    capture_dir: Path
    base_command: str
    captured_value: str
    setup_end: int
    choose_block: tuple[int, int]


def derive_choose_from_list(capture_dir: Path, base_command: str = "PF_SHOW_CHOICE_LIST",
                            captured_value: str = "PF_CHOICE_B") -> "ChooseFromListTemplate":
    """Auto-derive a choose-from-list template from a genuine capture that clicked ``base_command`` and picked
    ``captured_value`` from the ПоказатьВыборИзСписка popup (card 96 / E2)."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    lo, hi = _find_choose_from_list(mgr, base_command, captured_value)
    return ChooseFromListTemplate(capture_dir=capture_dir, base_command=base_command,
                                  captured_value=captured_value, setup_end=lo - 1, choose_block=(lo, hi))


def choose_from_list(
    template: ChooseFromListTemplate,
    value: str,
    *,
    message_prefix: str = "PF_CHOICE=",
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free choose-from-list / -menu (card 96 / E2): open the form (replay the genuine
    setup), click the command that raises ПоказатьВыборИзСписка (or ПоказатьВыборИзМеню), and pick ``value``
    (a list/menu item VALUE NAME, e.g. PF_CHOICE_A / PF_MENU_1). The pick is the choose tag ``e0 4b 53`` + the
    length-prefixed value at the ManagedForm path (same ``e0 4b 53`` family as a radio ``set_choice``, but
    addressed at the form — the popup reuses the window); only the value is re-targeted (``captured_value`` ->
    ``value``, fixed-width). The result surfaces as a user message ``Сообщить(<message_prefix> + value)`` (e.g.
    "PF_CHOICE=PF_CHOICE_A" for a list, "PF_MENU=PF_MENU_1" for a menu), so commit is verified by scanning the
    responses for that ASCII marker (this also doubles as a first user-message read decode for E5). Returns
    {captured_value, value, accepted, committed, message}."""
    marker = f"{message_prefix}{value}".encode()
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        seq = replay.replay_setup(template.setup_end)
        accepted = False
        lo, hi = template.choose_block
        for i in range(lo, hi + 1):
            wire = replay.apply(mgr[i])
            wire = retarget_value(wire, template.captured_value, value)  # no-op on the click/control frames
            wire = _set_seq(wire, seq); seq += 1
            resp = replay.exchange(wire)
            seen += resp
            accepted = accepted or bool(resp)
        # drain the async Сообщить callback frame (it follows the pick by a beat)
        for _ in range(3):
            extra = replay.receive()
            if not extra:
                break
            seen += extra
            replay.observe_response(extra)
    committed = marker in seen
    messages = extract_user_messages(bytes(seen))  # card 96 / E5: the actual Сообщить text(s) emitted
    return {"captured_value": template.captured_value, "value": value,
            "accepted": accepted, "committed": committed,
            "message": f"{message_prefix}{value}" if committed else None,
            "messages": messages}


# Card 98 #2 — get_window_list_testclient query bodies (the command body AFTER the `cb 23 95` header marker).
# Decoded from the genuine manager capture genuine-card98-windowlist-20260620: a 2-frame request whose 2nd
# frame's response enumerates every open window. SESSION-INDEPENDENT — the leading 16-byte field is a query-id
# nonce the client echoes, NOT session-validated (proven by live splice replay across a fresh session). Replayed
# by grafting onto a live value-read frame's header (everything up to + incl. `cb 23 95`), so the live session
# GUIDs are inherited and the client accepts the command (a raw replay of the genuine session frame is rejected
# with «Сеанс работы завершен администратором»). The trailing `66 53 b2 a6` is the frame tail marker.
WINDOW_LIST_HEADER_MARKER = b"\xcb\x23\x95"
WINDOW_LIST_QUERY_BODIES = (
    bytes.fromhex("554d850d068aee499e292f8d0e7a9f0ed5cedc64c37131d44ca6873f4286de772a81888181e04b55202020206653b2a6"),
    bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d500a6934157a67f4fbdbb6adaa67093cc81888181e1828183818181812020206653b2a6"),
)


# Card 98 change-1 generalization — the get_form_analysis DESCRIPTOR query (enumerates every element of the live
# form). Decoded from genuine-card98-formanalysis-20260620 (chunk#44): body = <33B nonce> 9a 66 <form path
# SecondaryFrame[S].ManagedForm[F]> <opcode 88 81 81 e1 82 81 81 81 81 81 81 20 20 20> <tail>. SESSION-INDEPENDENT
# apart from the form path: spliced onto a live value-read header (live session GUIDs) with the form path
# retargeted to the live SecondaryFrame/ManagedForm, the client returns the full element-tree descriptor (a raw
# replay is rejected — the client validates the session GUID). The `9a 66` is the 0x9a string envelope + length
# 102 = len("SecondaryFrame[<36>].ManagedForm[<36>]"); GUIDs are fixed 36 chars so the length is constant.
DESCRIPTOR_QUERY_PREPATH = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d556b8b81da321984a897449a89068b3b89a66")
DESCRIPTOR_QUERY_POSTPATH = bytes.fromhex("888181e1828181818181812020206653b2a6")


# Card 98 change-1 — "resolve form by SecondaryFrame" query: input the window's SecondaryFrame (S only), the
# response returns the form's full SecondaryFrame[S].ManagedForm[F] — the way to learn a navigated form's
# ManagedForm F (the window list gives only S). Decoded from genuine-card98-formanalysis (mgr#2, the sweep's
# first query): body = <33B nonce> 9a 34 SecondaryFrame[S] <opcode 88 81 81 e1 81 81 81 81 81 81 81 20 20 20>
# <tail>. Note the opcode is `e1 81 81…` (resolve), distinct from the descriptor's `e1 82 81…`.
RESOLVE_QUERY_PREPATH = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d561c48a217a04ac4eb41f7524b252e4c59a34")
RESOLVE_QUERY_POSTPATH = bytes.fromhex("888181e1818181818181812020206653b2a6")

# Card 98 change-1 — the open-list NAVIGATE command (genuine-card90-openlist frame 14): body = <nonce> 9a 2f
# MainFrame[<desktop>] <opcode 88 82 81> f7 <char-count> <nav-link utf-16le> <pad><tail>. Opens the form at the
# nav-link as a new window/tab on the held session (the desktop MainFrame GUID is session-stable). Retarget the
# nav-link to any `e1cib/list|data|app/…` to open any form.
NAVIGATE_BODY = bytes.fromhex(
    "e3490553e2c8d04b881be98d27b886d1d5ed8b4c6ff37b244c8fb26d223bc724aa"
    "9a2f4d61696e4672616d655b36636137356535302d363261332d343834322d623663642d6234323966373539316566325d"
    "888281f71c650031006300690062002f006c006900730074002f0021043f044004300432043e0447043d0438043a042e0022043e043204300440044b042020206653b2a6"
)
NAVIGATE_GENUINE_LINK = "e1cib/list/Справочник.Товары"
# The genuine navigate's source frame is the desktop MainFrame. On the vanessa_client config this GUID is the
# same every session (deterministic), so the hardcoded value works without retarget; on ANOTHER config the
# desktop MainFrame GUID may differ, so ``splice_navigate(main_frame=…)`` retargets it to the LIVE desktop GUID
# (read from a window-list — card 98 change-5 config-agnostic open).
NAVIGATE_GENUINE_MAINFRAME = "6ca75e50-62a3-4842-b6cd-b429f7591ef2"


def splice_resolve_form_query(rendered_value_read_frame: bytes, secondary_frame: str) -> bytes:
    """Card 98 change-1 — build the resolve-form query (input ``SecondaryFrame[secondary_frame]`` only) by
    grafting it onto a live value-read header. The response returns the form's ``SecondaryFrame[S].ManagedForm[F]``
    — parse it to learn a navigated form's ManagedForm F (then ``splice_descriptor_query`` can introspect it)."""
    j = rendered_value_read_frame.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: j + len(WINDOW_LIST_HEADER_MARKER)]
    s_path = f"SecondaryFrame[{secondary_frame}]".encode("latin1")
    return header + RESOLVE_QUERY_PREPATH + s_path + RESOLVE_QUERY_POSTPATH


def splice_navigate(rendered_value_read_frame: bytes, nav_link: str, main_frame: str | None = None) -> list[bytes]:
    """Card 98 change-1 — build the navigate command (open the form at ``nav_link``, e.g.
    ``e1cib/list/Справочник.Контрагенты``) by grafting the genuine open-list navigate body onto a live header,
    with the nav-link retargeted (UTF-16, char-count prefix recomputed). The genuine navigate is a 2-frame
    request (opcode ``88 82 81`` then ``81 81 81``); BOTH are needed to actually open the form (one frame alone
    leaves no new window). Returns the two frames in order.

    The navigate's source is the desktop MainFrame. On the vanessa_client config its GUID is deterministic, so
    the genuine hardcoded value works as-is; pass ``main_frame`` (the LIVE desktop MainFrame GUID, e.g. from a
    window-list) to retarget it for a config-agnostic open where the desktop GUID may differ (card 98
    change-5)."""
    j = rendered_value_read_frame.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: j + len(WINDOW_LIST_HEADER_MARKER)]
    body = NAVIGATE_BODY
    if main_frame is not None and main_frame != NAVIGATE_GENUINE_MAINFRAME:
        body = body.replace(NAVIGATE_GENUINE_MAINFRAME.encode("latin1"), main_frame.encode("latin1"))
    body = body.replace(NAVIGATE_GENUINE_LINK.encode("utf-16-le"), nav_link.encode("utf-16-le"))
    body = re.sub(rb"\xf7.", b"\xf7" + bytes([len(nav_link)]), body, count=1)  # fix the nav-link char-count prefix
    body2 = body.replace(b"\x88\x82\x81\xf7", b"\x81\x81\x81\xf7", 1)          # the 2nd frame's opcode variant
    return [header + body, header + body2]


def splice_descriptor_query(rendered_value_read_frame: bytes, secondary_frame: str, managed_form: str) -> bytes:
    """Card 98 change-1 — build the live get_form_analysis descriptor query: graft the descriptor command body
    (form path retargeted to the live ``secondary_frame`` / ``managed_form``) onto the value-read frame's live
    header (everything up to + including the `cb 23 95` marker). Sending it returns the form's full element-tree
    descriptor — parse with ``responses.extract_descriptor_fields`` to enumerate every EditField with NO per-form
    capture."""
    j = rendered_value_read_frame.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: j + len(WINDOW_LIST_HEADER_MARKER)]
    form_path = f"SecondaryFrame[{secondary_frame}].ManagedForm[{managed_form}]".encode("latin1")
    return header + DESCRIPTOR_QUERY_PREPATH + form_path + DESCRIPTOR_QUERY_POSTPATH


# Card 98 — TABLE-CELL READ command (genuine-card98-tableread, chunk [73]). Reads the CURRENT ROW's value of a
# table column BY NAME. Body after `cb 23 95`: <33B nonce> <path block: SecondaryFrame[S].ManagedForm[F].(Group
# [g].)*Table[T]> 88 81 81 e0 4b 55 eb 53 <column-name block> 20 20 20 20 <tail>. The nonce is echoed (not
# session-validated — same as the descriptor/window-list splices), so it splices onto a live header. The response
# carries the cell value in the canonical `e0 4b 53 9a <len> <value>` envelope (extract_form_field_values decodes
# it). Both the path and the column ride the `9a <byte-len> <latin1>` (ASCII) / `97 <char-count> <utf-16le>`
# (Cyrillic) string envelope (encode_element_path_block).
TABLE_READ_NONCE = bytes.fromhex("49e435875c8d1b408e6db0b800402d80d57169d3613479a845ad5b8f42f5e21bec")
TABLE_READ_SUFFIX = bytes.fromhex("888181e04b55eb53")
TABLE_READ_PAD = b"\x20\x20\x20\x20"
TABLE_READ_TAIL = b"\x66\x53\xb2\xa6"


def splice_table_cell_read(
    rendered_value_read_frame: bytes, secondary_frame: str, managed_form: str,
    groups: list[str], table: str, column: str,
) -> bytes:
    """Card 98 — build the live table-cell read command: graft the genuine table-read body (the Table element
    path retargeted to the live ``secondary_frame``/``managed_form`` + enclosing ``groups`` + ``table``, the
    column addressed BY NAME) onto the value-read frame's live header (up to + incl. ``cb 23 95``). Sending it
    returns the CURRENT ROW's cell value in the `e0 4b 53 9a <len> <value>` envelope — parse with
    ``responses.extract_form_field_values``. Reads a dynlist column or a form table cell with NO per-form capture;
    path + column are dual-encoded (ASCII 0x9a / Cyrillic 0x97)."""
    from .element_ref import encode_element_path_block

    j = rendered_value_read_frame.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: j + len(WINDOW_LIST_HEADER_MARKER)]
    parts = [f"SecondaryFrame[{secondary_frame}]", f"ManagedForm[{managed_form}]"]
    parts += [f"Group[{g}]" for g in groups]
    parts.append(f"Table[{table}]")
    path_block = encode_element_path_block(".".join(parts))
    column_block = encode_element_path_block(column)
    return header + TABLE_READ_NONCE + path_block + TABLE_READ_SUFFIX + column_block + TABLE_READ_PAD + TABLE_READ_TAIL


@dataclass
class ReadListColumnTemplate:
    """A genuine dynlist (catalog list-form) column read in a capture (card 98). The genuine flow opens a REAL
    catalog LIST form by nav-link («Я открываю основную форму списка справочника …»), positions to the first row
    («перехожу к первой строке»), and reads a column of the standard dynlist table «Список». Unlike a form table
    (row 1 current on open — ``read_table_cell`` reads it by splice), a dynlist has NO current row until the list
    DATA loads + a row is positioned, and positioning is a TABLE-ACTION (the ``88 82 81`` family). A piecemeal
    splice cannot reach that state (the introspection open — window-list/resolve/descriptor queries — leaves a
    different active-form state, so positioning never takes; proven by 4 failed reconstructions). So the WHOLE
    manager stream is replayed FAITHFULLY (navigate → activate → render/data-load → position → read) with
    ``GuidRebinder`` rebinding the per-session window GUIDs; the nav-link + column are retargeted in-frame. The
    read frame's response carries the value in the canonical ``81 81 81 e0 4b 53`` envelope (live-verified
    «Обувь»). ``captured_value`` is the value the genuine read returned (a verbatim-replay reference)."""

    capture_dir: Path
    nav_link: str
    column: str
    captured_value: str
    table: str = "Список"


def derive_read_list_column(
    capture_dir: Path,
    nav_link: str = "e1cib/list/Справочник.Товары",
    column: str = "Наименование",
) -> "ReadListColumnTemplate":
    """Auto-derive a dynlist column-read template from a genuine list-form read capture (the flow opened the list
    at ``nav_link``, positioned to the first row, and read ``column`` of the «Список» table). Validates the
    nav-link (UTF-16) and the read command's column block (``eb 53 <column path-block>``) are present, and records
    the value the genuine read returned (for a verbatim-replay reference)."""
    from .element_ref import encode_element_path_block
    from .responses import extract_table_cell_value

    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    if not any(nav_link.encode("utf-16le") in b for b in mgr):
        raise ValueError(f"nav-link {nav_link!r} (utf-16) not found in the capture")
    col_block = b"\xeb\x53" + encode_element_path_block(column)  # the read command's `eb 53 <column>` block
    if not any(col_block in b for b in mgr):
        raise ValueError(f"read command for column {column!r} (eb 53 <block>) not found in the capture")
    captured_value = ""
    for chunk in _read_chunks(capture_dir, CLIENT_TO_MANAGER):
        value = extract_table_cell_value(chunk)
        if value is not None:
            captured_value = value
            break
    return ReadListColumnTemplate(
        capture_dir=capture_dir, nav_link=nav_link, column=column, captured_value=captured_value)


# Card 98 — GO-TO-ROW-BY-VALUE (row-select) command, decoded from genuine-card90-rowaddr mgr[19]/[22] (the
# «в таблице "T" я перехожу к строке: | col | value |» step, captured for row 2 then row 3 — byte-diff confirms
# only the search VALUE + per-command nonce/seq change). Body after the `cb 23 95` header:
#   <33B nonce> <path block: SecondaryFrame[S].ManagedForm[F].(Group[g].)*Table[T]>
#   88 81 81 e1 81 81 82  cb 23 95 <16B nonce>  c0 4b 53 <search-column block>  eb 53 <search-value block>
#   <7-space pad> <tail>
# Reads the row WHERE <search-column> == <search-value> and makes it the CURRENT row (then a table-cell read
# returns that row). The path-block prefix is IDENTICAL to the table-read command's, so build it by reusing a live
# rebound read frame's header+nonce+path and swapping the action suffix (``row_select_from_read_frame``). Both the
# column and value ride the 0x9a (ASCII) / 0x97 (UTF-16) string envelope.
ROW_SELECT_OPCODE = bytes.fromhex("888181e1818182")
ROW_SELECT_MID = bytes.fromhex("cb2395") + bytes.fromhex("aefe483dc6a95a4ca0999eb6477630c6")  # cb2395 + echoed nonce
ROW_SELECT_SEP_COLUMN = bytes.fromhex("c04b53")  # before the search-column block (cf. read's e0 4b 55)
ROW_SELECT_SEP_VALUE = bytes.fromhex("eb53")     # before the search-value block
ROW_SELECT_PAD = b"\x20" * 7
ROW_SELECT_TAIL = bytes.fromhex("6653b2a6")
_READ_ACTION = bytes.fromhex("888181e04b55")  # the table-read action opcode (marks where the read suffix begins)


def row_select_from_read_frame(read_frame: bytes, search_column: str, search_value: str) -> bytes:
    """Card 98 — build a go-to-row-by-value (row-select) command by reusing a live rebound table-read frame's
    header + nonce + path-block prefix (identical between the two commands) and appending the row-select action
    suffix (``c0 4b 53 <search-column> eb 53 <search-value>``). Column + value are dual-encoded (ASCII 0x9a /
    Cyrillic 0x97).

    ⚠ DECODED but NOT live-functional cross-form: this suffix is decoded from a genuine FORM-table «перехожу к
    строке» (genuine-card90-rowaddr); splicing it onto a live DYNLIST read frame does NOT reposition the current
    row (live-tested 2026-06-20 on Товары: still read row 1 «Обувь», not the WHERE match). Reproducing a dynlist
    row-select needs a genuine DYNLIST «перехожу к строке» capture (the proven recipe). Kept for that follow-up
    (the byte-shape is correct + unit-tested); not wired into ``read_list_row_replay``."""
    from .element_ref import encode_element_path_block

    cut = read_frame.find(_READ_ACTION)  # the read action start; everything before it = header + nonce + path-block
    if cut < 0:
        raise ValueError("read_frame is not a table-read command (no 88 81 81 e0 4b 55)")
    return (read_frame[:cut] + ROW_SELECT_OPCODE + ROW_SELECT_MID
            + ROW_SELECT_SEP_COLUMN + encode_element_path_block(search_column)
            + ROW_SELECT_SEP_VALUE + encode_element_path_block(search_value)
            + ROW_SELECT_PAD + ROW_SELECT_TAIL)


def retarget_list_read_frame(
    wire: bytes, *, old_nav: str, new_nav: str, old_col_block: bytes, new_col_block: bytes,
    old_table: str | None = None, new_table: str | None = None,
) -> bytes:
    """Retarget ONE frame of the list-read full-replay (card 98). On a navigate frame: swap the nav-link
    (UTF-16LE) and fix its ``f7 <char-count>`` prefix precisely (by position, not a blind ``re.sub`` that could
    hit an ``f7`` byte in the nonce/GUIDs) — the navigate command tolerates the resize. On the read frame: swap
    the read column block (``eb 53 <path-block>``). No-op on every other frame (neither marker present)."""
    if old_nav != new_nav:
        old_b, new_b = old_nav.encode("utf-16le"), new_nav.encode("utf-16le")
        if old_b in wire:
            wire = wire.replace(old_b, new_b)
            pos = wire.find(new_b)
            if pos >= 2 and wire[pos - 2] == 0xF7:
                wire = wire[: pos - 2] + b"\xf7" + bytes([len(new_nav)]) + wire[pos:]
    if old_col_block != new_col_block and old_col_block in wire:
        wire = wire.replace(old_col_block, new_col_block)
    if old_table and new_table and old_table != new_table:
        wire = retarget_list_table_segment(wire, old_table=old_table, new_table=new_table)
    return wire


def retarget_list_table_segment(wire: bytes, *, old_table: str, new_table: str) -> bytes:
    """Retarget Table[old] inside any encoded element path in a list replay frame.

    List-read captures were recorded against table ``Список``. Real catalog list
    forms can expose a dynlist table named after the object, so the full replay
    must retarget the mid-path Table segment without disturbing the column leaf.
    """
    if old_table == new_table:
        return wire
    old_seg = f"Table[{old_table}]"
    new_seg = f"Table[{new_table}]"
    out = wire
    for path in [*extract_element_paths(wire), *extract_element_paths_utf16(wire)]:
        if old_seg not in path:
            continue
        old_block = encode_element_path_block(path)
        new_block = encode_element_path_block(path.replace(old_seg, new_seg))
        out = out.replace(old_block, new_block)
    return out


def read_list_column_replay(
    template: ReadListColumnTemplate,
    open_link: str | None = None,
    column: str | None = None,
    table: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Read the CURRENT ROW's value of a dynamic-list (dynlist) column natively — card 98 (no Vanessa) — via a
    FAITHFUL FULL-SEQUENCE replay of a genuine catalog list-form read. The whole manager stream replays in the
    genuine order (navigate the list form → activate → render/data-load → position to the first row → read the
    column), so the dynlist reaches the interaction-ready state a piecemeal splice cannot; ``GuidRebinder`` rebinds
    the per-session window GUIDs by first-appearance (the open_card/set_reference_field machinery). The nav-link is
    re-targeted to ``open_link`` (any ``e1cib/list/Справочник.X`` — opens a DIFFERENT list; the navigate command
    tolerates the resize) and the read column to ``column`` (the read frame's ``eb 53 <block>``), each defaulting
    to the captured list/column (a verbatim replay → the captured value). The value is parsed from the read
    frame's response with ``extract_table_cell_value`` (the canonical ``81 81 81 e0 4b 53`` envelope; None when
    the list has no row / the column is not addressable). Returns {nav_link, column, value, captured_value}.

    Live-verified (vanessa_client, 4/4 cold): Товары/Наименование to «Обувь», Товары/Код to «000000001»,
    Контрагенты/Наименование to «Покупатели», Валюты/Наименование to «EUR» (all vs OData ground truth). COLD-CLIENT
    BOUNDARY: this works as the FIRST full-replay against a fresh client. A SECOND replay against the SAME client
    process returns None — the warm on-disk form cache answers the render/data-load with a reduced response so the
    dynlist's current-row DATA is not materialised and the read echoes the command (``88 81 81 e0 4b 55``) with no
    value. The COLD-CLIENT BOUNDARY (one full-replay per fresh client) still applies; to read SEVERAL columns of
    the SAME (first) row, use ``read_list_row_replay`` — it reads them all inside the one cold session this
    function would otherwise spend on a single column."""
    nav = open_link or template.nav_link
    col = column or template.column
    tbl = table or template.table
    out = read_list_row_replay(
        template, open_link=open_link, columns=[col], table=tbl, host=host, port=port,
        read_timeout_sec=read_timeout_sec, idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec)
    return {"table": tbl, "nav_link": nav, "column": col, "value": out["row"].get(col),
            "captured_value": template.captured_value}


def read_list_row_replay(
    template: ReadListColumnTemplate,
    open_link: str | None = None,
    columns: list[str] | None = None,
    table: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Read SEVERAL columns of a dynamic-list's current (first) row in ONE cold session — card 98 (no Vanessa).
    The cold-client boundary is per-CLIENT-PROCESS, so this reads every requested column INSIDE the single cold
    full-replay where the row data is materialised (instead of one read per fresh client): faithful full-replay of
    the genuine list-form read THROUGH the captured read (the proven cold path, nav-link re-targeted to
    ``open_link``), then — on the SAME socket — one extra table-cell read per requested ``column``, reusing the
    rebound read frame with the column block re-targeted, **keeping its message-id (offset 2)** and bumping the
    sequence (offset 19) per command. Live-verified: keeping the message-id is required — regenerating it returns a
    481-byte error (offset 2 is a session-validated correlation id), while keeping it + a bumped sequence reads any
    column («Код»→«000000001», «Наименование»→«Обувь»). ``columns`` defaults to the captured column. Returns
    {nav_link, row: {column: value}}.

    Reads the FIRST row. A specific row (by value / by index) and iterating all rows are NOT here: the
    go-to-row-by-value command is decoded (``row_select_from_read_frame``) but splicing it from the captured FORM
    table onto a live DYNLIST does NOT reposition the current row (live-tested: still reads row 1), and a «next
    row» command isn't captured — both need a genuine DYNLIST row-navigation capture (separate follow-up)."""
    from .element_ref import encode_element_path_block
    from .responses import extract_table_cell_value

    nav = open_link or template.nav_link
    cols = list(columns) if columns else [template.column]
    tbl = table or template.table
    old_col = b"\xeb\x53" + encode_element_path_block(template.column)
    row: dict[str, str | None] = {}
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        read_idx = next((i for i, b in enumerate(mgr) if old_col in b), len(mgr) - 1)  # the captured read frame
        read_tmpl = b""
        for i in range(read_idx + 1):  # cold full-replay THROUGH the captured read (the proven materialising path)
            wire = retarget_list_read_frame(
                replay.apply(mgr[i]), old_nav=template.nav_link, new_nav=nav,
                old_col_block=old_col, new_col_block=old_col,
                old_table=template.table, new_table=tbl)  # nav/table retarget only; captured read keeps its column here
            replay.exchange(wire)
            if i == read_idx:
                read_tmpl = wire  # the rebound read frame: live GUIDs + the captured message-id, column=template.column
        base_seq = int.from_bytes(read_tmpl[19:21], "little")
        for offset, col in enumerate(cols):  # extra reads on the SAME socket — keep message-id, bump sequence
            new_col = b"\xeb\x53" + encode_element_path_block(col)
            frame = bytearray(read_tmpl.replace(old_col, new_col))
            frame[19:21] = ((base_seq + 1 + offset) & 0xFFFF).to_bytes(2, "little")
            resp = replay.exchange(bytes(frame))
            row[col] = extract_table_cell_value(resp)
    return {"table": tbl, "nav_link": nav, "row": row}


def read_list_row_by_value_replay(
    capture_dir: Path,
    where_value: str,
    open_link: str | None = None,
    where_column: str = "Наименование",
    columns: list[str] | None = None,
    *,
    captured_value: str = "Сапоги",
    captured_where_column: str = "Наименование",
    captured_read_column: str = "Код",
    nav_default: str = "e1cib/list/Справочник.Товары",
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Position a dynamic list to the row WHERE ``where_column`` == ``where_value`` and read ``columns`` — card 98
    (no Vanessa), the «в таблице "Список" я перехожу к строке: | <col> | <value> |» equivalent. A FAITHFUL
    FULL-SEQUENCE replay of a genuine DYNLIST go-to-row-by-value capture (``rowbyvalue``: open the
    Товары list → switch to flat «Список» view → «перехожу к строке Наименование=Сапоги» → read Код → …). The
    whole manager stream replays in the genuine order so the dynlist reaches the interaction-ready state — a splice
    of the FORM-table «перехожу к строке» onto a live dynlist did NOT reposition the current row (see
    ``row_select_from_read_frame``), but the full-sequence replay does. ``GuidRebinder`` rebinds the per-session
    window GUIDs; the go-to-row frame's MATCH VALUE (``eb 53 <block>``) is retargeted ``captured_value`` ->
    ``where_value`` and its WHERE COLUMN (``c0 4b 53 <block>``) ``captured_where_column`` -> ``where_column``; the
    read frame's column (``eb 53 <block>``) ``captured_read_column`` -> the requested column(s). Values/columns are
    dual-encoded (ASCII ``0x9a`` / Cyrillic ``0x97``). Returns {nav_link, where, row: {column: value}}.

    ⚠ COLD-CLIENT BOUNDARY (as the dynlist read): one positioning+read per fresh ``launch_test_client``; reads
    SEVERAL columns of the WHERE row inside the one materialised session (message-id kept, sequence bumped)."""
    from .element_ref import encode_element_path_block
    from .responses import extract_table_cell_value

    nav = open_link or nav_default
    cols = list(columns) if columns else [captured_read_column]
    old_val = b"\xeb\x53" + encode_element_path_block(captured_value)         # the go-to-row MATCH value
    new_val = b"\xeb\x53" + encode_element_path_block(where_value)
    old_wcol = b"\xc0\x4b\x53" + encode_element_path_block(captured_where_column)  # the WHERE column
    new_wcol = b"\xc0\x4b\x53" + encode_element_path_block(where_column)
    old_rcol = b"\xeb\x53" + encode_element_path_block(captured_read_column)  # the READ column (on the read frame)
    first_rcol = b"\xeb\x53" + encode_element_path_block(cols[0])

    row: dict[str, str | None] = {}
    with _open_replay_session(
        capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        read_idxs = [i for i, b in enumerate(mgr) if b"\x88\x81\x81\xe0\x4b\x55\xeb\x53" in b]
        if not read_idxs:
            raise ValueError("rowbyvalue capture has no table-read frame (88 81 81 e0 4b 55 eb 53)")
        r1 = read_idxs[0]
        read_tmpl = b""
        first_resp = b""
        for i in range(r1 + 1):  # cold full-replay through open + flat-view + go-to-row(value) + the first read
            wire = retarget_list_read_frame(
                replay.apply(mgr[i]), old_nav=nav_default, new_nav=nav,
                old_col_block=old_rcol, new_col_block=first_rcol)  # the read column on the read frame
            if old_wcol != new_wcol:
                wire = wire.replace(old_wcol, new_wcol)            # the WHERE column on the go-to-row frame
            wire = wire.replace(old_val, new_val)                  # the WHERE value on the go-to-row frame
            resp = replay.exchange(wire)
            if i == r1:
                read_tmpl, first_resp = wire, resp
        row[cols[0]] = extract_table_cell_value(first_resp)
        base_seq = int.from_bytes(read_tmpl[19:21], "little")
        for offset, col in enumerate(cols[1:]):  # extra read columns on the SAME socket (message-id kept, seq bumped)
            new_rcol = b"\xeb\x53" + encode_element_path_block(col)
            frame = bytearray(read_tmpl.replace(first_rcol, new_rcol))
            frame[19:21] = ((base_seq + 1 + offset) & 0xFFFF).to_bytes(2, "little")
            resp = replay.exchange(bytes(frame))
            row[col] = extract_table_cell_value(resp)
    return {"nav_link": nav, "where": {where_column: where_value}, "row": row}


# Card 98 — the dynlist NEXT-ROW (advance current row) action GUID, decoded from nextrow: the
# go-to-row 2-frame block carries a 16-byte action GUID at offset 53 of its `… e1 …` frame — `3e312772…` =
# go-to-FIRST-row, `d267315b…` = go-to-NEXT-row (constant across invocations; the read after it advances
# Обувь→Продукты→Услуги). The next-row block is replayed (rebound) rather than synthesised, so this GUID is
# documentation; the genuine block frames carry it.
NEXT_ROW_ACTION_GUID = "d267315b-1d90-0041-8c4e-c1ff077822d5"
FIRST_ROW_ACTION_GUID = "3e312772-a733-f14a-928d-66945ecff123"


def read_list_grid_replay(
    template: ReadListColumnTemplate,
    open_link: str | None = None,
    columns: list[str] | None = None,
    table: str | None = None,
    *,
    max_rows: int = 25,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Read MANY ROWS × columns of a dynamic list (the whole visible grid) in ONE cold session — card 98 (no
    Vanessa). Uses a genuine NEXT-ROW capture (``nextrow``: open list → first row → read → «перехожу
    к следующей строке» → read → …): cold full-replay through the first read, then a loop of — replay the genuine
    NEXT-ROW block (the 4-frame `88 82 81`/`88 82 81 e1` go-to-row pair carrying the next-row action GUID
    ``d267315b…``, rebound + sequence-bumped) to advance the current row, then one table-cell read per requested
    ``column`` (read frame column-retargeted, **message-id kept**, sequence bumped). All on the SAME socket (the
    cold-client materialised session). Stops at ``max_rows`` or when a row reads empty (end of list); adjacent
    duplicate row values are returned as legitimate data.

    ``columns`` defaults to the captured column; ``open_link`` re-targets the list (nav-link). Returns
    {nav_link, row_count, rows: [{column: value}, …], stop_reason, truncated}. Live-verified the cursor advances
    (Обувь→Продукты→Услуги…). Reads the rows in the list's current view/sort order; one grid read per fresh
    ``launch_test_client``."""
    from .element_ref import encode_element_path_block
    from .responses import extract_table_cell_value

    nav = open_link or template.nav_link
    cols = list(columns) if columns else [template.column]
    tbl = table or template.table
    old_col = b"\xeb\x53" + encode_element_path_block(template.column)
    rows: list[dict[str, str | None]] = []
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        read_idxs = [i for i, b in enumerate(mgr) if b"\x88\x81\x81\xe0\x4b\x55\xeb\x53" in b]  # the read frames
        if len(read_idxs) < 2:
            raise ValueError("nextrow capture must contain >=2 reads (first row + a next-row read)")
        r1, r2 = read_idxs[0], read_idxs[1]
        nextrow_block = list(range(r1 + 1, r2))  # the genuine go-to-next-row frames between read#1 and read#2
        read_tmpl = b""
        for i in range(r1 + 1):  # cold full-replay THROUGH the first read (setup + open + first-row position)
            wire = retarget_list_read_frame(
                replay.apply(mgr[i]), old_nav=template.nav_link, new_nav=nav,
                old_col_block=old_col, new_col_block=old_col,
                old_table=template.table, new_table=tbl)
            replay.exchange(wire)
            if i == r1:
                read_tmpl = wire
        seq = int.from_bytes(read_tmpl[19:21], "little")

        def _send_seqd(frame: bytes) -> bytes:
            nonlocal seq
            seq += 1
            b = bytearray(frame)
            b[19:21] = (seq & 0xFFFF).to_bytes(2, "little")  # keep message-id (off2), bump sequence (off19)
            resp = replay.exchange(bytes(b))
            return resp

        stop_reason = "max_rows"
        truncated = max_rows > 0
        for rownum in range(max_rows):
            if rownum > 0:  # advance the current row: replay the genuine next-row block (rebound, seq-bumped)
                for bi in nextrow_block:
                    _send_seqd(retarget_list_table_segment(
                        replay.apply(mgr[bi]), old_table=template.table, new_table=tbl))
            rowvals: dict[str, str | None] = {}
            row_responses: list[bytes] = []
            for col in cols:
                new_col = b"\xeb\x53" + encode_element_path_block(col)
                response = _send_seqd(read_tmpl.replace(old_col, new_col))
                row_responses.append(response)
                rowvals[col] = extract_table_cell_value(response)
            if all(v is None for v in rowvals.values()):
                stop_reason = "row_read_timeout" if any(not response for response in row_responses) else "empty_row"
                truncated = stop_reason == "row_read_timeout"
                break  # end of list or incomplete row; duplicate rows are legitimate data
            rows.append(rowvals)
        else:
            stop_reason = "max_rows"
            truncated = max_rows > 0
    return {"table": tbl, "nav_link": nav, "row_count": len(rows), "rows": rows,
            "truncated": truncated, "stop_reason": stop_reason}


def splice_window_list_queries(rendered_value_read_frame: bytes) -> list[bytes]:
    """Card 98 #2 — build the live get_window_list_testclient query frames by grafting each window-list command
    body onto the live header of a rendered value-read frame (everything up to + including the `cb 23 95`
    marker — the session GUIDs + seq the engine already rebound). The value-read frame and the genuine
    window-list query share that header, so the splice yields a session-live window-list command. Returns the
    two query frames in order."""
    j = rendered_value_read_frame.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: j + len(WINDOW_LIST_HEADER_MARKER)]
    return [header + body for body in WINDOW_LIST_QUERY_BODIES]


def _all_secondary_frames(chunks: list[bytes]) -> dict[bytes, int]:
    """Count each distinct SecondaryFrame GUID across a chunk list (card 96 / E1 dialog decode)."""
    counts: dict[bytes, int] = {}
    for b in chunks:
        for m in re.findall(rb"SecondaryFrame\[([0-9a-f-]{36})\]", b):
            counts[m] = counts.get(m, 0) + 1
    return counts


def _find_dialog_close(mgr: list[bytes], cli: list[bytes]) -> tuple[str, int]:
    """Locate the dialog ANSWER (close) command (card 96 / E1). A `ПоказатьВопрос`/`ПоказатьПредупреждение`
    dialog opens a NEW top-level window (a fresh `SecondaryFrame` GUID, distinct from the form's most-common
    one); the genuine answer is a WINDOW-LEVEL command on that dialog SF — `…SecondaryFrame[<dlg>] 88 82 81`
    (the window's default action = ОК/Да), NOT a `Button` activate. Returns (dialog_sf, close_frame_idx)."""
    counts = _all_secondary_frames(mgr + cli)
    if not counts:
        raise ValueError("no SecondaryFrame GUIDs in the capture")
    form_sf = max(counts, key=lambda g: counts[g])  # the form window is by far the most referenced
    for i, b in enumerate(mgr):
        if b"\x88\x82\x81" in b:
            for g in counts:
                if g != form_sf and g in b:
                    return g.decode(), i
    raise ValueError("no dialog close command (88 82 81 on a non-form SecondaryFrame) found in the capture")


@dataclass
class AnswerDialogTemplate:
    """A genuine dialog open+answer flow in a capture (card 96 / E1). The whole manager stream is replayed
    (the dialog's fresh SecondaryFrame is a per-open GUID that GuidRebinder learns from the live open response
    and rebinds in the close command — the same mechanism as the form window). ``close_frame`` and
    ``dialog_sf`` document the decoded answer; ``result_marker`` is the fixture field the answer commits."""

    capture_dir: Path
    raise_command: str
    result_marker: str
    dialog_sf: str
    close_frame: int


def derive_answer_dialog(capture_dir: Path, raise_command: str = "PF_V4_WARNING",
                         result_marker: str = "PF_V4_WARNING_ACK") -> "AnswerDialogTemplate":
    """Auto-derive a dialog answer template from a genuine capture that raised a real dialog (clicking
    ``raise_command``) and answered it. Validates that a dialog window + a window-level close command exist."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    dialog_sf, close = _find_dialog_close(mgr, cli)
    return AnswerDialogTemplate(capture_dir=capture_dir, raise_command=raise_command,
                               result_marker=result_marker, dialog_sf=dialog_sf, close_frame=close)


def answer_dialog(
    template: AnswerDialogTemplate,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free dialog ANSWER (card 96 / E1): faithfully replay the genuine dialog session
    (open form → raise the dialog → window-level answer command → read-back), no Vanessa. A dialog opens a
    NEW SecondaryFrame whose GUID is fresh per open; ``GuidRebinder`` learns the LIVE dialog GUID from the live
    open response and rebinds the captured one in the close command — the same first-appearance rebinding as
    the form window, so a faithful full-stream replay answers it. Commit is confirmed by the ``result_marker``
    (the fixture answer field, e.g. PF_V4_WARNING_ACK) appearing in the post-answer read-sweep responses.
    Returns {raise_command, result_marker, dialog_sf, committed}."""
    marker = template.result_marker.encode()
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])  # rebinds the form SF AND the dialog SF (learned from the open response)
            resp = replay.exchange(wire)
            seen += resp
    committed = marker in seen
    return {"raise_command": template.raise_command, "result_marker": template.result_marker,
            "dialog_sf": template.dialog_sf, "committed": committed}


def retarget_ref_value(frame: bytes, old: str, new: str) -> bytes:
    """Card 96 / E2 — retarget a UTF-16LE reference "choice-by-string" value (`<char-count><utf-16le name>
    <space pad>`), FIXED-WIDTH aware. A CatalogRef InputField resolves a TYPED name to a ref (выбор по строке);
    the wire carries the name as `e0 41 81 81 b7 <char-count:varint><utf-16le name><ASCII-space padding>` — the
    value-SET family (tag `b7` vs the plain string's `ba`) but UTF-16 with a CHAR-count length prefix. Swaps the
    name and grows/shrinks the trailing space padding to keep the frame size constant. No-op if ``old`` is
    absent. ``new`` must be a valid catalog element NAME (the field resolves it on commit)."""
    ob = old.encode("utf-16le")
    nb = new.encode("utf-16le")
    needle = encode_1c_length(len(old)) + ob          # length prefix = CHAR count (not byte count)
    idx = frame.find(needle)
    if idx < 0:
        return frame
    vend = idx + len(needle)
    pad = 0
    while vend + pad < len(frame) and frame[vend + pad] == 0x20:
        pad += 1
    region = len(needle) + pad
    new_prefix = encode_1c_length(len(new))
    new_pad = region - len(new_prefix) - len(nb)
    if new_pad < 0:
        raise ValueError(f"reference name {new!r} ({len(nb)} bytes) exceeds the choice buffer")
    return frame[:idx] + new_prefix + nb + b"\x20" * new_pad + frame[idx + region:]


@dataclass
class SetReferenceFieldTemplate:
    """A genuine reference-field input in a capture (card 96 / E2). ``field`` is the CatalogRef field; the
    captured name was typed into it (resolved by the field to a ref on commit). The whole manager stream is
    replayed (the input + its focus-change commit + the read-back); the typed name is re-targeted to any other
    valid catalog element name."""

    capture_dir: Path
    field: str
    captured_value: str


def derive_set_reference_field(capture_dir: Path, field: str = "Контрагент",
                               captured_value: str = "Корнет ЗАО") -> "SetReferenceFieldTemplate":
    """Auto-derive a reference-set template from a genuine capture that typed ``captured_value`` into the
    CatalogRef field ``field`` (resolved to a ref). Validates the UTF-16 choice value is present."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    needle = encode_1c_length(len(captured_value)) + captured_value.encode("utf-16le")
    if not any(needle in b for b in mgr):
        raise ValueError(f"captured reference value {captured_value!r} (utf-16 choice) not found in the capture")
    return SetReferenceFieldTemplate(capture_dir=capture_dir, field=field, captured_value=captured_value)


def set_reference_field(
    template: SetReferenceFieldTemplate,
    value: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free reference selection (card 96 / E2): set a CatalogRef field to ``value`` (a catalog
    element NAME, e.g. "Пантера АО"), no Vanessa. A reference InputField resolves a typed name to a ref (выбор по
    строке) on focus-change; this faithfully replays the genuine reference-input session (open form → type the
    name into ``field`` → focus-change commit → read-back), re-targeting the typed UTF-16 name to ``value``
    (``retarget_ref_value``, fixed-width). Commit is confirmed by the resolved presentation ``value`` reading
    back. ``value`` defaults to the captured name (a verbatim replay). Returns {field, value, committed}."""
    target = value or template.captured_value
    marker = target.encode("utf-16le")
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])
            wire = retarget_ref_value(wire, template.captured_value, target)  # no-op where the name is absent
            resp = replay.exchange(wire)
            seen += resp
    committed = marker in seen
    return {"field": template.field, "value": target, "committed": committed}


@dataclass
class SearchListTemplate:
    """A genuine dynamic-list SEARCH-STRING input in a capture (card 97 change 4). The user typed a search
    string into a dynamic list's search-string addition (``search_field``, e.g.
    ``ДенамическийСписокИерархияСтрокаПоиска``); the list filters incrementally (searchOnInput=Auto). The search
    SET rides the SAME UTF-16 value buffer as a reference-name SET
    (``e0 41 81 81 b7 <char-count><utf-16le value><ASCII-space pad>``) — only the addressed element differs (the
    SearchStringAddition leaf vs a CatalogRef InputField). ``stop_after`` is the last manager ordinal to replay
    (the end of the FIRST captured search's SET block) so a two-search decode capture replays as ONE search."""

    capture_dir: Path
    search_field: str
    captured_value: str
    stop_after: int


def derive_search_list(
    capture_dir: Path,
    search_field: str = "ДенамическийСписокИерархияСтрокаПоиска",
    captured_value: str = "Молоко",
) -> "SearchListTemplate":
    """Auto-derive a dynamic-list search template from a genuine capture that typed ``captured_value`` into the
    list's search-string addition. Locates the FIRST captured search's SET block (the contiguous run of manager
    frames carrying the UTF-16 ``b7`` value buffer) and sets ``stop_after`` to its last frame, so the replay
    applies ONE search even though a decode capture types two different strings (for the byte-diff)."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    needle = encode_1c_length(len(captured_value)) + captured_value.encode("utf-16le")
    hits = [i for i, b in enumerate(mgr) if needle in b]
    if not hits:
        raise ValueError(f"captured search value {captured_value!r} (utf-16 b7 buffer) not found in the capture")
    stop = hits[0]  # first contiguous run of value-bearing frames = the first search's SET block
    while stop + 1 in hits:
        stop += 1
    return SearchListTemplate(capture_dir=capture_dir, search_field=search_field,
                              captured_value=captured_value, stop_after=stop)


def search_list(
    template: SearchListTemplate,
    value: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Filter a dynamic list by a SEARCH STRING natively — card 97 change 4 (no Vanessa). Types ``value`` into
    the list's search-string addition; the list filters incrementally. A dynlist search rides the SAME UTF-16
    value-SET buffer as a reference-name input (``e0 41 81 81 b7 <char-count><utf-16le><space pad>``), addressed
    at the SearchStringAddition element, so this faithfully replays the genuine search session (open form →
    activate the dynlist → SET the search string) through the FIRST captured search (``template.stop_after``),
    re-targeting the UTF-16 search string to ``value`` (``retarget_ref_value``, fixed-width — bounded by the
    captured value length). ``value`` defaults to the captured string (a verbatim replay). The list-filter has
    no clean value read-back (the visible rows narrow — confirm with capture_screenshot); ``echoed`` reports the
    search value being echoed back in the client responses. Returns {search_field, value, echoed}."""
    target = value or template.captured_value
    marker = target.encode("utf-16le")
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        last = min(template.stop_after, len(mgr) - 1)
        for i in range(last + 1):
            wire = replay.apply(mgr[i])
            wire = retarget_ref_value(wire, template.captured_value, target)  # no-op where the value is absent
            resp = replay.exchange(wire)
            seen += resp
    return {"search_field": template.search_field, "value": target, "echoed": marker in seen}


@dataclass
class AdvancedSearchTemplate:
    """A genuine dynamic-list «Расширенный поиск» (advanced-search) flow in a capture (card 97 change 4). The
    flow drives a MODAL dialog: click «Расширенный поиск» (`<dynlist>Найти`) → the standard
    `UniversalListFindExtForm` opens (a NEW window) → SET its `Pattern` field → click `Find`. The Pattern rides
    the UTF-16 `b7` value buffer (the same as a ref/search value); the whole stream replays with GuidRebinder
    rebinding the new dialog window, and the Pattern is re-targeted."""

    capture_dir: Path
    search_command: str
    captured_value: str


def derive_advanced_search(
    capture_dir: Path,
    search_command: str = "ДенамическийСписокИерархияНайти",
    captured_value: str = "Молоко",
) -> "AdvancedSearchTemplate":
    """Auto-derive an advanced-search template from a genuine capture that opened the «Расширенный поиск» dialog
    and typed ``captured_value`` into its Pattern field. Validates the UTF-16 ``b7`` Pattern value is present."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    needle = encode_1c_length(len(captured_value)) + captured_value.encode("utf-16le")
    if not any(needle in b for b in mgr):
        raise ValueError(f"captured advanced-search value {captured_value!r} (utf-16 b7 buffer) not found")
    return AdvancedSearchTemplate(capture_dir=capture_dir, search_command=search_command, captured_value=captured_value)


def advanced_search(
    template: AdvancedSearchTemplate,
    value: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Filter a dynamic list via the «Расширенный поиск» (advanced-search) DIALOG natively — card 97 change 4
    (no Vanessa). This is the reusable "drive a MODAL dialog" pattern: faithfully replay the genuine flow (open
    the form → click «Расширенный поиск» which opens the standard `UniversalListFindExtForm` in a NEW window →
    SET its `Pattern` field → click `Find`), with `GuidRebinder` rebinding the new dialog window's GUID by
    first-appearance (the answer_dialog / open_card machinery) and the Pattern value re-targeted to ``value``
    (UTF-16 `b7` buffer, fixed-width — bounded by the captured length). The dialog searches its default field
    (the capture left FieldSelector at «Код»; targeting another field is a refinement = set FieldSelector). No
    clean value read-back — the list narrows (verify by screenshot); ``echoed`` reports the Pattern echoed in
    the responses. Returns {search_command, value, echoed}."""
    target = value or template.captured_value
    marker = target.encode("utf-16le")
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])
            wire = retarget_ref_value(wire, template.captured_value, target)  # no-op where the value is absent
            resp = replay.exchange(wire)
            seen += resp
    return {"search_command": template.search_command, "value": target, "echoed": marker in seen}


def retarget_cell_address(frame: bytes, old: str, new: str) -> bytes:
    """Card 97 change 3 — re-target the cell ADDRESS in a spreadsheet «перейти к ячейке» navigate command. The
    command carries the address as a length-prefixed ``\\xfa<len><utf-8 address>`` (R1C1 notation) followed by a
    FIXED 3-space structural suffix; swap the address and let the FRAME RESIZE by the address-length delta (keep
    the trailing bytes). Unlike a value-SET frame (which desyncs on resize — card 80), the navigate frame
    TOLERATES resize: proven live that consuming the trailing spaces is ignored (the navigate silently no-ops)
    but growing/shrinking the frame navigates correctly — so this supports an ARBITRARY-length address (R1C1,
    R12C12, R100C99 …), not just same-length. No-op where the address is absent (every non-navigate frame).
    ``new`` must be a valid R1C1 cell address (≤ 255 bytes for the 1-byte ``\\xfa`` length prefix)."""
    if old == new:
        return frame
    if len(new.encode("utf-8")) > 255:
        raise ValueError(f"cell address {new!r} exceeds the 1-byte length prefix")
    ob = bytes([0xfa, len(old)]) + old.encode("utf-8")  # fa <len> <old address>
    nb = bytes([0xfa, len(new)]) + new.encode("utf-8")  # fa <len> <new address>  (frame resizes by the delta)
    if ob not in frame:
        return frame
    return frame.replace(ob, nb)


@dataclass
class ReadSpreadsheetCellTemplate:
    """A genuine spreadsheet (ТабличныйДокумент) cell read in a capture (card 97 change 3). Reading a cell is an
    IN-CLIENT operation — the client evaluates a 1C method on the live ТабличныйДокумент object and returns the
    value as a small PLAIN string; the binary form-render blob never carries the cells. The genuine flow is
    open form → run the report → «перейти к ячейке <addr>» (navigate, addr as ``\\xfa<len><utf-8>``) → the client
    echoes the current cell value at ``EditField[<field>] \\x81\\x81\\x81 … \\x9a<len><value>`` (the card-79
    value-read shape). The whole stream replays; the address is re-targeted, the value is read from the response."""

    capture_dir: Path
    field: str
    captured_address: str
    captured_value: str


def derive_read_spreadsheet_cell(
    capture_dir: Path,
    field: str = "PF_REPORT",
    captured_address: str = "R1C1",
) -> "ReadSpreadsheetCellTemplate":
    """Auto-derive a spreadsheet cell-read template from a genuine capture that ran the report and read cell
    ``captured_address`` of the ТабличныйДокумент field ``field``. Validates the navigate command (the address
    ``\\xfa<len><addr>``) is present, and records the captured value (for a verbatim-replay reference)."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    addr_block = bytes([0xfa, len(captured_address)]) + captured_address.encode("utf-8")
    if not any(addr_block in b for b in mgr):
        raise ValueError(f"captured cell address {captured_address!r} (navigate command) not found in the capture")
    seen = b"".join(_read_chunks(capture_dir, CLIENT_TO_MANAGER))
    captured_value = read_field_value_near(seen, field) or ""
    return ReadSpreadsheetCellTemplate(
        capture_dir=capture_dir, field=field, captured_address=captured_address, captured_value=captured_value)


def read_spreadsheet_cell(
    template: ReadSpreadsheetCellTemplate,
    address: str | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Read a spreadsheet (ТабличныйДокумент) CELL by address natively — card 97 change 3 (no Vanessa). Reading
    a cell is an IN-CLIENT method on the live object (NOT a binary .mxl wire-decode): the genuine flow replays
    in full (open form → run the report → «перейти к ячейке <addr>» → the client returns the current cell value),
    with the navigate ADDRESS re-targeted to ``address`` (``retarget_cell_address``, same-length R1C1 notation)
    and the value parsed from the client response with the card-79 ``read_field_value_near`` (the cell value
    rides the wire as the SAME ``\\x9a<len><utf-8>`` value-read shape — confirmed: the manager NEVER receives the
    cell text in the binary form-render; only a targeted in-client read returns it). ``address`` defaults to the
    captured cell. Returns {field, address, value}."""
    target = address or template.captured_address
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])
            wire = retarget_cell_address(wire, template.captured_address, target)  # no-op off the navigate frame
            resp = replay.exchange(wire)
            seen += resp
    value = read_field_value_near(bytes(seen), template.field)
    return {"field": template.field, "address": target, "value": value}


@dataclass
class OpenCardTemplate:
    """A genuine open-card navigation in a capture (card 96 / E3). Drilling into a list row opens the record's
    form in a NEW window. ``result_marker`` is a card-specific UTF-16 string (the opened form's metadata id or
    caption, e.g. "ФормаГруппы") that appears only once the card window is realised."""

    capture_dir: Path
    result_marker: str


def derive_open_card(capture_dir: Path, result_marker: str = "ФормаГруппы") -> "OpenCardTemplate":
    """Auto-derive an open-card template from a genuine capture that opened a record card from a list (open the
    catalog list → «Изменить»/double-click a row → the card form opens in a new window). Validates that the
    capture has multiple windows and the card marker is present (UTF-16)."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    if len(_all_secondary_frames(mgr + cli)) < 2:
        raise ValueError("expected multiple windows (fixture form + list + card) in the open-card capture")
    if not any(result_marker.encode("utf-16le") in b for b in cli):
        raise ValueError(f"card marker {result_marker!r} (utf-16) not found in the capture")
    return OpenCardTemplate(capture_dir=capture_dir, result_marker=result_marker)


def open_card(
    template: OpenCardTemplate,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free open-card navigation (card 96 / E3): drill into a list row to open its record
    card, no Vanessa. Faithfully replays the genuine navigation session from ``capture`` (open form → open the
    catalog list → «Изменить»/open the active row → the card form opens in a NEW window). Each new window's
    fresh SecondaryFrame GUID is rebound by `GuidRebinder` automatically (first-appearance, like the dialog
    window). Opening is confirmed by the card marker (``result_marker``, e.g. the card form id "ФормаГруппы")
    reading back. Verified live 2026-06-18. Returns {result_marker, opened}. (Opens the captured active row's
    card; to open a SPECIFIC row's card, precede with a row-select — compose with select_table_row.)"""
    marker = template.result_marker.encode("utf-16le")
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])  # rebinds the form / list / card window GUIDs as they appear
            resp = replay.exchange(wire)
            seen += resp
    opened = marker in seen
    return {"result_marker": template.result_marker, "opened": opened}


def _window_sf_for_ref(chunks: list[bytes], ref: str) -> str | None:
    """The SecondaryFrame GUID that co-occurs with a window's identifying nav ref (UTF-16LE) — e.g. a card's
    ``e1cib/data/…`` record ref, a list's ``e1cib/list/…`` ref, or the fixture's ``e1cib/app/…`` ref. Card 96 /
    E3 (close/activate decode). Returns the most-frequently co-occurring GUID, or None if the ref is absent."""
    refb = ref.encode("utf-16le")
    counts: dict[bytes, int] = {}
    for b in chunks:
        if refb in b:
            for g in re.findall(rb"SecondaryFrame\[([0-9a-f-]{36})\]", b):
                counts[g] = counts.get(g, 0) + 1
    return max(counts, key=lambda g: counts[g]).decode() if counts else None


def _find_window_close(mgr: list[bytes], window_sf: str) -> int:
    """Index of the genuine window-CLOSE command for ``window_sf``: the window-level `88 82 81` command (the
    SAME family as the dialog close in answer_dialog, applied to any window) referencing that window's
    SecondaryFrame. Card 96 / E3."""
    sfb = window_sf.encode()
    for i, b in enumerate(mgr):
        if b"\x88\x82\x81" in b and sfb in b:
            return i
    raise ValueError(f"no window-close (88 82 81 on SecondaryFrame[{window_sf}]) in the capture")


def _next_sf_close_after(mgr: list[bytes], idx: int, all_sfs: dict[bytes, int]) -> int:
    """Index of the next window-level `88 82 81` close (after ``idx``) targeting ANY SecondaryFrame. The replay
    stops BEFORE it so close_window closes only the target window — the windows capture closes the card and
    THEN the fixture, so closing just the card means truncating before the second close. Card 96 / E3."""
    for i in range(idx + 1, len(mgr)):
        if b"\x88\x82\x81" in mgr[i] and any(g in mgr[i] for g in all_sfs):
            return i
    return len(mgr)


@dataclass
class CloseWindowTemplate:
    """A genuine window-CLOSE in a capture (card 96 / E3). Drilling into a list opens a record card in a NEW
    window; «И я закрываю текущее окно» closes that active card via a window-level command — the same
    `…SecondaryFrame[<window>] 88 82 81` family as the dialog close, applied to a top-level window. The whole
    manager stream is replayed (GuidRebinder rebinds the list/card window GUIDs as they appear, like open_card),
    TRUNCATED just before any subsequent window-close so only the target window (``window_ref``) is closed."""

    capture_dir: Path
    window_ref: str
    window_sf: str
    close_frame: int
    stop_after: int


def derive_close_window(capture_dir: Path,
                        window_ref: str = "e1cib/data/Справочник.Контрагенты") -> "CloseWindowTemplate":
    """Auto-derive a close-window template from a genuine capture that opened a record card (drill a list row)
    and closed it. ``window_ref`` identifies the window being closed (default the card's record data ref); its
    SecondaryFrame is located, then the `88 82 81` close command on it. Validates both exist."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    sfs = _all_secondary_frames(mgr + cli)
    window_sf = _window_sf_for_ref(mgr + cli, window_ref)
    if not window_sf:
        raise ValueError(f"window ref {window_ref!r} (utf-16) not found in the capture")
    close = _find_window_close(mgr, window_sf)
    stop_after = _next_sf_close_after(mgr, close, sfs) - 1  # replay up to (excl.) the next window-close
    return CloseWindowTemplate(capture_dir=capture_dir, window_ref=window_ref, window_sf=window_sf,
                               close_frame=close, stop_after=stop_after)


def close_window(
    template: CloseWindowTemplate,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free window CLOSE (card 96 / E3): faithfully replay the genuine navigation (open form
    → open list → drill a row → the card opens) then the window-level close command on the active card, no
    Vanessa. close/activate are window-level commands (`…SecondaryFrame[<window>] 88 82 81`, the same family as
    the dialog close); a faithful full-stream replay reproduces them, GuidRebinder rebinding the list/card window
    GUIDs as they appear (first-appearance, same machinery as open_card / answer_dialog). The replay is truncated
    just before any subsequent close so ONLY the target window is closed.

    Verified by the closed window's (live, rebound) SecondaryFrame being reported by the client BEFORE the close
    but gone AFTER it (``closed``), plus ``accepted`` (the close command got a response, no divergence). Returns
    {window_ref, window_sf, live_window_sf, accepted, closed, active_window_after}."""
    before = bytearray()  # responses BEFORE the close (the card window is open here)
    after = bytearray()   # responses AFTER the close (the card window should be gone)
    close_resp = b""
    diverged: int | None = None
    send_timeout_at: int | None = None
    consec_empty = 0
    live_sf: str | None = None
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        rebinder = replay.rebinder
        assert rebinder is not None
        last = min(len(mgr) - 1, template.stop_after)
        for i in range(last + 1):
            wire = replay.apply(mgr[i])  # rebinds the list / card window GUIDs as they appear
            try:
                replay.send(wire)
            except ProtocolSendTimeout:
                send_timeout_at = i
                break
            except OSError:
                diverged = diverged if diverged is not None else i
                break
            resp = replay.receive()
            replay.observe_response(resp)
            if i < template.close_frame:
                before += resp
            elif i == template.close_frame:
                close_resp = resp
            else:
                after += resp
            if not resp and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8 and diverged is None:
                    diverged = i
            elif resp:
                consec_empty = 0
        live_sf = rebinder.guid_map.get(template.window_sf)
    accepted = send_timeout_at is None and diverged is None and bool(close_resp)
    closed = bool(live_sf) and live_sf.encode() in before and live_sf.encode() not in after
    active_after = next((r for r in ("e1cib/app/", "e1cib/list/", "e1cib/data/")
                         if r.encode("utf-16le") in after), None)
    return {"window_ref": template.window_ref, "window_sf": template.window_sf, "live_window_sf": live_sf,
            "accepted": accepted, "closed": closed, "active_window_after": active_after,
            "send_timeout_at": send_timeout_at,
            "failure_reason": SEND_TIMEOUT_REASON if send_timeout_at is not None else None}


@dataclass
class ActivateWindowTemplate:
    """A genuine window ACTIVATE in a capture (card 96 / E3). «И я активизирую окно "Заголовок"» brings a
    BURIED top-level window to the front. Decode (2026-06-18): activate and close are the SAME window-level
    command `…SecondaryFrame[<window>] 88 82 81` — the effect is contextual on z-order: applied to the active
    (topmost) window it closes it; applied to a BACKGROUND window it brings it forward. The whole manager stream
    is replayed (GuidRebinder rebinds the list/card/target window GUIDs as they appear, like open_card)."""

    capture_dir: Path
    window_ref: str
    window_sf: str
    activate_frame: int


def derive_activate_window(capture_dir: Path,
                           window_ref: str = "e1cib/app/Обработка.ФикстураПротоколаTestClient"
                           ) -> "ActivateWindowTemplate":
    """Auto-derive an activate-window template from a genuine capture that opened other windows on top of a
    target and then brought the target back to front by title. ``window_ref`` identifies the activated window
    (default the fixture form's app ref); its SecondaryFrame is located, then the `88 82 81` window-level command
    on it (the same command family as the close — its effect on a buried window is activate). Validates both."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    window_sf = _window_sf_for_ref(mgr + cli, window_ref)
    if not window_sf:
        raise ValueError(f"window ref {window_ref!r} (utf-16) not found in the capture")
    frame = _find_window_close(mgr, window_sf)  # the window-level 88 82 81 command on the target SF
    return ActivateWindowTemplate(capture_dir=capture_dir, window_ref=window_ref, window_sf=window_sf,
                                  activate_frame=frame)


def activate_window(
    template: ActivateWindowTemplate,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free window ACTIVATE (card 96 / E3): faithfully replay the genuine navigation (open
    form → open list → drill a row → other windows cover the target) then the window-level command that brings
    the BURIED target window to the front, no Vanessa. activate/close are the same `…SecondaryFrame[<window>]
    88 82 81` command — on a background window it activates (brings forward). A faithful full-stream replay
    reproduces it, GuidRebinder rebinding the window GUIDs as they appear (same machinery as open_card /
    close_window).

    Verified by the target window becoming the ACTIVE (last-reported) window: its (live, rebound) SecondaryFrame
    is referenced in the final window-bearing client response (``activated``) — the inverse of close_window,
    where the closed window's SF is gone and a DIFFERENT window is active. Returns {window_ref, window_sf,
    live_window_sf, accepted, activated, target_in_activate_resp}."""
    activate_resp = b""
    after = bytearray()           # responses strictly after the activate command
    last_window_resp = b""        # the last client response that reports a top-level window (its active window)
    diverged: int | None = None
    send_timeout_at: int | None = None
    consec_empty = 0
    live_sf: str | None = None
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        rebinder = replay.rebinder
        assert rebinder is not None
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])  # rebinds the list / card / target window GUIDs as they appear
            try:
                replay.send(wire)
            except ProtocolSendTimeout:
                send_timeout_at = i
                break
            except OSError:
                diverged = diverged if diverged is not None else i
                break
            resp = replay.receive()
            replay.observe_response(resp)
            if i == template.activate_frame:
                activate_resp = resp
            elif i > template.activate_frame:
                after += resp
            if b"SecondaryFrame[" in resp:
                last_window_resp = resp  # track the final active-window report
        # one extra read to let the client settle on the now-active window
        tail = replay.receive()
        if b"SecondaryFrame[" in tail:
            last_window_resp = tail
        after += tail
        live_sf = rebinder.guid_map.get(template.window_sf)
    accepted = send_timeout_at is None and diverged is None and bool(activate_resp)
    sfb = live_sf.encode() if live_sf else b"\x00"
    # the target is the active window iff its live SF is the one reported in the final window-bearing response
    activated = bool(live_sf) and sfb in last_window_resp
    return {"window_ref": template.window_ref, "window_sf": template.window_sf, "live_window_sf": live_sf,
            "accepted": accepted, "activated": activated,
            "target_in_activate_resp": bool(live_sf) and sfb in activate_resp,
            "send_timeout_at": send_timeout_at,
            "failure_reason": SEND_TIMEOUT_REASON if send_timeout_at is not None else None}


@dataclass
class ReadUserMessagesTemplate:
    """A genuine flow that emits user messages (`Сообщить`) in a capture (card 96 / E5). The whole manager
    stream is replayed and the client→manager responses are scanned for the user-message envelope; this turns
    the messages-to-user panel into a readable assertion source (no Vanessa). ``expected`` documents a message
    the capture is known to emit (for validation)."""

    capture_dir: Path
    expected: str | None = None


def derive_read_user_messages(capture_dir: Path, expected: str | None = None) -> "ReadUserMessagesTemplate":
    """Auto-derive a read-user-messages template from a genuine capture whose flow raised a `Сообщить`. Validates
    that the capture's client responses contain at least one user-message envelope (`cb 53 9a`)."""
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    if not any(b"\xcb\x53\x9a" in c for c in cli):
        raise ValueError("no user-message envelope (cb 53 9a) in the capture's client responses")
    return ReadUserMessagesTemplate(capture_dir=capture_dir, expected=expected)


def read_user_messages(
    template: ReadUserMessagesTemplate,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free user-message READ (card 96 / E5): faithfully replay the genuine flow from
    ``capture`` (whatever raises `Сообщить` — e.g. the choose-from-list/menu callbacks) and return the
    messages-to-user text the form emits, no Vanessa. This is the capture-free ASSERTION read for «нет сообщений
    пользователю» / reading `Сообщить` output: the client reports the message panel as `cb 53 9a <byte-len>
    <UTF-8>` in its responses; `extract_user_messages` decodes them. Returns {messages, count, expected_found}."""
    seen = bytearray()
    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for i in range(len(mgr)):
            wire = replay.apply(mgr[i])
            resp = replay.exchange(wire)
            seen += resp
        for _ in range(3):  # drain the async Сообщить callback frames (they follow the action by a beat)
            extra = replay.receive()
            if not extra:
                break
            seen += extra
            replay.observe_response(extra)
    messages = extract_user_messages(bytes(seen))
    return {"messages": messages, "count": len(messages),
            "expected_found": (template.expected in messages) if template.expected else None}


def derive_table_cell_write(
    capture_dir: Path,
    column: str = "PF_TABLE_TEXT",
    captured_value: str = "CELLAA",
    *,
    commit_partner_field: str = "PF_EDIT_STRING",
    commit_partner_value: str = "C90CMT",
    default_value: str = "",
) -> "WriteTemplate":
    """Card 90 / 86e — derive a table-cell WRITE template from a genuine capture that edited a table cell.
    A table cell commits via the SAME value-SET as a plain string field (decode 2026-06-17): only the element
    path differs — the column is the `EditField` leaf inside a `Table[<table>]` segment, with NO row index (the
    edit hits the ACTIVE row). So this is exactly the card-86c commit-partner ``derive_write_template``: the
    cell's genuine input (the contiguous ``EditField[column]`` block carrying ``captured_value``) is the
    write-block, and the commit is the focus-change synthesized from ``commit_partner_field`` (its genuine
    activate, located via ``commit_partner_value``). The returned ``WriteTemplate`` is consumed by
    ``NativeWriteSession.set_table_cell`` / the standalone ``set_table_cell``."""
    return derive_write_template(
        capture_dir, field=column, captured_value=captured_value, default_value=default_value,
        commit_partner_field=commit_partner_field, commit_partner_value=commit_partner_value,
    )


def set_table_cell(
    template: WriteTemplate,
    value: str,
    *,
    target_column: str | None = None,
    target_table: str | None = None,
    base_table: str = "PF_TABLE_ITEMS",
    row_match: str | None = None,
    captured_row_match: str = "PF_ROW_002_TEXT",
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free table-cell write (card 90 / 86e): open the form ONCE, then write ``value`` into
    the ACTIVE row's cell. A cell SET is the plain string SET addressed at the column ``EditField`` leaf inside a
    ``Table[…]`` segment (no row index). Re-targets the column leaf (``target_column``) and optionally the
    ``Table[…]`` segment (``target_table``) and commits via the synthesized focus-change.

    Card 90 row-addressing: if the capture's SETUP includes a genuine row-select (its search value =
    ``captured_row_match``), pass ``row_match`` to select a DIFFERENT row by value — the search value is
    re-targeted (fixed-width) in the setup so the active row becomes the one whose column equals ``row_match``,
    and the cell SET lands there (live-proven 2026-06-17: PF_ROW_002_TEXT->PF_ROW_003_TEXT wrote into row 3).
    Returns {requested_value, readback_value, committed, column, table}."""
    retargets = [(captured_row_match, row_match)] if row_match and row_match != captured_row_match else None
    with NativeWriteSession(template, host=host, port=port, read_timeout_sec=read_timeout_sec,
                            idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
                            setup_retargets=retargets) as s:
        return s.set_table_cell(value, column=target_column, table=target_table, base_table=base_table)


def select_table_row(
    template: WriteTemplate,
    row_match: str,
    *,
    captured_row_match: str = "PF_ROW_002_TEXT",
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Standalone capture-free ROW-SELECT by value (card 90 follow-up #1). A row-select is "find the row where
    <column> = <value>" — both length-prefixed strings in the genuine command; re-targeting the VALUE
    (fixed-width) selects a different row. This replays the capture's setup with the search value
    ``captured_row_match`` -> ``row_match`` so the matching row becomes ACTIVE. Returns {row_match, accepted}.
    Verify the selection via the fixture's `PF_SELECTED_ROW_MARKER` (read_form_value → `PF_ROW_IDX_<n>:<marker>`,
    updated by the OnActivateRow handler) or by a subsequent `set_table_cell(row_match=…)` (writes into the
    selected row — live-proven 2026-06-17: PF_ROW_002_TEXT->PF_ROW_003_TEXT selected + wrote row 3)."""
    retargets = [(captured_row_match, row_match)] if row_match != captured_row_match else None
    with NativeWriteSession(template, host=host, port=port, read_timeout_sec=read_timeout_sec,
                            idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
                            setup_retargets=retargets) as s:
        # __enter__ replayed the setup (incl. the re-targeted row-select); the matching row is now active.
        return {"row_match": row_match, "accepted": s._sock is not None}


def write_form_value(
    template: WriteTemplate,
    new_value: str,
    *,
    host: str = "127.0.0.1",
    port: int = 15381,
    read_timeout_sec: float = 0.6,
    idle_timeout_sec: float = 0.15,
    connect_timeout_sec: float = 10.0,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Replay the template capture in full with live GUID rebind, retarget the value to ``new_value``, and
    read the field back. Returns a result dict; ``committed`` is True when the read-back shows ``new_value``
    and neither the captured value nor the default."""
    new_b = new_value.encode("utf-8")
    new16 = new_value.encode("utf-16-le")
    cap_b = template.captured_value.encode("utf-8")
    cap16 = template.captured_value.encode("utf-16-le")
    def_b = template.default_value.encode("utf-8") if template.default_value else b"\x00\x00\x00NONE"

    read_responses: dict[int, bytes] = {}
    set_resp = b""
    consec_empty = 0
    real_divergence: int | None = None
    send_timeout_at: int | None = None

    with _open_replay_session(
        template.capture_dir,
        host=host, port=port, read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec, connect_timeout_sec=connect_timeout_sec,
    ) as replay:
        mgr = replay.manager_chunks
        for index, payload in enumerate(mgr):
            if index > template.stop_after:
                break
            wire = replay.apply(payload)
            wire = retarget_value(wire, template.captured_value, new_value)
            try:
                replay.send(wire)
            except ProtocolSendTimeout:
                send_timeout_at = index
                break
            except OSError:
                real_divergence = index
                break
            response = replay.receive()
            replay.observe_response(response)
            if index in template.read_frames:
                read_responses[index] = response
            # the SET frame is the one whose ORIGINAL payload carried the captured value
            if cap_b in payload or cap16 in payload:
                set_resp += response
            if not response and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8:
                    real_divergence = index
                    break
            elif response:
                consec_empty = 0

        # Read the field back RIGHT AFTER the commit, not ~200 frames downstream: send any read_frame that
        # is beyond stop_after out-of-order on the still-open socket (a value-READ is a stateless query; the
        # form is open + GUID-rebound). Short replay => multi-write on one client does not accumulate desync
        # between the SET and a far-downstream read.
        if real_divergence is None and send_timeout_at is None:
            for rf in template.read_frames:
                if rf > template.stop_after and rf < len(mgr):
                    try:
                        replay.send(replay.apply(mgr[rf]))
                    except ProtocolSendTimeout:
                        send_timeout_at = rf
                        break
                    except OSError:
                        break
                    read_responses[rf] = replay.receive()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "set_resp.bin").write_bytes(set_resp)
        for i, r in read_responses.items():
            (output_dir / f"read_resp_{i}.bin").write_bytes(r)

    read_blob = b"".join(read_responses.values())
    readback = next(
        (read_field_value_near(r, template.field) for r in read_responses.values()
         if read_field_value_near(r, template.field)), None,
    )
    committed = _write_value_matches_readback(new_value, readback)
    return {
        "field": template.field,
        "requested_value": new_value,
        "readback_value": readback,
        "set_response_echoes_new": new_b in set_resp or new16 in set_resp,
        "new_in_readback": new_b in read_blob or new16 in read_blob,
        "captured_in_readback": cap_b in read_blob or cap16 in read_blob,
        "default_in_readback": def_b in read_blob,
        "real_divergence_at": real_divergence,
        "send_timeout_at": send_timeout_at,
        "failure_reason": SEND_TIMEOUT_REASON if send_timeout_at is not None else None,
        "committed": committed,
    }
