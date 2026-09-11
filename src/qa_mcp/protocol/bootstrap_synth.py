"""Synthesize TestClient session bootstrap frames 1..3 without captured bytes.

Card 62. Frames 1..3 are ~99% static across sessions (see
docs/protocol-research/evidence/session-bootstrap-frames-1-3/analysis.md). The only
per-session dynamic fields are:

  1. a decimal message counter in the ASCII header (offset 43, length 5), manager-chosen
     base, +1 per frame;
  2. frame 3 only: a 16-byte ACK GUID embedded (base64) in an 82-byte ticket token
     (b64 at offset 333, length 112; GUID at decoded offset 66).

The static layout is stored in repo (`bootstrap_frames_1to3.json`, derived once from a
capture). At session time NO capture is read: the template's static bytes are reused and the
two dynamic fields are injected from freshly generated values. The session/manager GUID
`e23134a2-…` and `7f58f27d-…` token remain template constants (lab/config-invariant — the
documented portability caveat).
"""

from __future__ import annotations

import base64
import json
import re
import secrets
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ..config import effective_env
from ..versioning import DEFAULT_PLATFORM_ROOT, PLATFORM_VERSION_ENV, platform_version_from_root

TEMPLATE_PATH = Path(__file__).resolve().parent / "bootstrap_frames_1to3.json"

# The platform version the in-repo synth template was captured on. The synthesized bootstrap frames declare this
# version to the client; the client REJECTS a major-version mismatch ("Различаются версии клиента и сервера") — so
# on a different platform (e.g. 8.5) the synth must declare the LIVE version instead. This is the only change the
# 8.5 handshake needs — the frame structure is otherwise identical (epic 112 P2/P3 vertical-slice finding).
SYNTH_TEMPLATE_VERSION = "8.3.27.2130"
_FULL_VERSION_RE = re.compile(r"\d+\.\d+\.\d+\.\d+")


def resolve_synth_platform_version() -> str:
    """Full live platform version the synth should declare (matches the live client to avoid version rejection).

    Priority: ``QA_MCP_PLATFORM_VERSION`` (only if a full ``x.y.z.w``) → ``PLATFORM_ROOT`` env → the package
    default platform root. Returns the template version when nothing resolves (preserving the 8.3 default).
    """
    values = effective_env()
    override = values.get(PLATFORM_VERSION_ENV, "")
    if _FULL_VERSION_RE.fullmatch(override):
        return override

    root = values.get("PLATFORM_ROOT") or DEFAULT_PLATFORM_ROOT
    return platform_version_from_root(root) or SYNTH_TEMPLATE_VERSION


def _inject_platform_version(frame: bytes, platform_version: str) -> bytes:
    """Replace the template platform version in a synth frame with the live one (tail-marker framed → length-safe)."""
    if not platform_version or platform_version == SYNTH_TEMPLATE_VERSION:
        return frame
    return frame.replace(SYNTH_TEMPLATE_VERSION.encode("ascii"), platform_version.encode("ascii"))


@dataclass(frozen=True)
class SynthesizedBootstrap:
    """Synthesized manager bootstrap frames 1..3 plus the static 4..7 templates.

    Frames 1..3 are pre-rendered (no ack needed). Frames 4..7 carry the static template
    bytes (`templates_4to7`); they are rendered on demand during the handshake once the
    client's ACK GUID is known — see `frame4_text` / `frame4_sequence` / and the session's
    use of BootstrapFrameRenderer for 5..7.
    """

    frames: dict[int, bytes]
    counter_base: int
    ticket_guid: bytes
    templates_4to7: dict[int, bytes]

    def frame(self, index: int) -> bytes:
        return self.frames[index]

    def template_frame(self, index: int) -> bytes:
        """Static template bytes for frames 4..7 (dynamic offsets overwritten by renderers)."""
        return self.templates_4to7[index]

    @property
    def frame4_sequence(self) -> int:
        """The single message counter value carried by frame 4 (= base + delta)."""
        spec = _template()["frame4"]
        return self.counter_base + int(spec["counter_delta"])

    def render_frame4(self, ack_guid: str) -> bytes:
        """Render frame 4 from the static template: inject the ACK GUID + the counter."""
        spec = _template()["frame4"]
        body = bytearray(self.templates_4to7[4])
        g_off = int(spec["ack_guid_offset"])
        g_len = int(spec["ack_guid_len"])
        body[g_off : g_off + g_len] = ack_guid.encode("ascii")
        c_off = int(spec["counter_offset"])
        c_len = int(spec["counter_len"])
        counter_text = str(self.frame4_sequence)
        if len(counter_text) != c_len:
            raise ValueError(f"frame4 counter {counter_text} does not fit {c_len} digits")
        body[c_off : c_off + c_len] = counter_text.encode("ascii")
        return bytes(body)


@lru_cache(maxsize=1)
def _template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def _render_counter(frame_hex_bytes: bytearray, counter_value: int, spec: dict) -> None:
    offset = int(spec["offset"])
    length = int(spec["length"])
    text = str(counter_value)
    if len(text) != length:
        raise ValueError(
            f"counter {counter_value} does not fit the fixed {length}-digit field "
            f"(pick a base in [{10 ** (length - 1)}, {10 ** length - 1}])"
        )
    frame_hex_bytes[offset : offset + length] = text.encode("ascii")


def _render_frame3_ticket(frame_hex_bytes: bytearray, ticket_guid: bytes, spec: dict) -> None:
    b64_offset = int(spec["b64_offset"])
    b64_length = int(spec["b64_length"])
    decoded_len = int(spec["decoded_len"])
    guid_off = int(spec["guid_decoded_offset"])
    guid_len = int(spec["guid_length"])
    if len(ticket_guid) != guid_len:
        raise ValueError(f"ticket_guid must be {guid_len} bytes, got {len(ticket_guid)}")

    current_b64 = bytes(frame_hex_bytes[b64_offset : b64_offset + b64_length]).decode("ascii")
    token = bytearray(base64.b64decode(current_b64))
    if len(token) != decoded_len:
        raise ValueError(f"frame3 token decoded to {len(token)} bytes, expected {decoded_len}")
    token[guid_off : guid_off + guid_len] = ticket_guid
    new_b64 = base64.b64encode(bytes(token))
    if len(new_b64) != b64_length:
        raise ValueError(f"re-encoded token length {len(new_b64)} != {b64_length}")
    frame_hex_bytes[b64_offset : b64_offset + b64_length] = new_b64


def _apply_constants(body: bytearray, frame_index: int, overrides: dict[str, str]) -> None:
    """Replace lab/config-constant GUIDs in a frame with fresh per-session values."""
    for name, spec in _template().get("constants", {}).items():
        if frame_index not in spec["frames"] or name not in overrides:
            continue
        off = int(spec["offset"])
        length = int(spec["length"])
        body[off : off + length] = overrides[name].encode("ascii")


def _max_generated_counter_delta(tmpl: dict) -> int:
    """Largest counter offset generated from ``counter_base`` by the synth template."""
    counter_spec = tmpl["counter"]
    per_frame_delta = int(counter_spec["per_frame_delta"])
    max_delta = 0
    for key in tmpl.get("frames", {}):
        idx = int(key)
        if idx in (1, 2, 3):
            max_delta = max(max_delta, per_frame_delta * (idx - 1))
    if "frame4" in tmpl:
        max_delta = max(max_delta, int(tmpl["frame4"]["counter_delta"]))
    return max_delta


def synthesize_bootstrap(
    counter_base: int | None = None,
    ticket_guid: bytes | None = None,
    randomize_constants: bool | list[str] = False,
    platform_version: str | None = None,
) -> SynthesizedBootstrap:
    """Render frames 1..3 from the in-repo template with fresh dynamic fields.

    counter_base: 5-digit message-counter base (default: a fresh random in range).
    ticket_guid: 16-byte frame-3 ACK GUID (default: a fresh random).
    randomize_constants: True = randomize ALL config-constant GUIDs (session_guid, token_7f in
        frames 1..3; guid2 in frame 4); a list of names = randomize only those — used to pin
        down which constants the client validates vs. which are manager-free-choice.
    platform_version: the full platform version the synth declares to the client (default: the LIVE version
        via ``resolve_synth_platform_version`` — so an 8.5 client is not rejected for a version mismatch).
    """
    if platform_version is None:
        platform_version = resolve_synth_platform_version()
    tmpl = _template()
    counter_spec = tmpl["counter"]
    length = int(counter_spec["length"])
    delta = int(counter_spec["per_frame_delta"])
    if counter_base is None:
        min_base = 10 ** (length - 1)
        max_base = 10 ** length - 1 - _max_generated_counter_delta(tmpl)
        if max_base < min_base:
            raise ValueError(f"template counter delta does not fit the fixed {length}-digit field")
        counter_base = secrets.randbelow(max_base - min_base + 1) + min_base
    if ticket_guid is None:
        ticket_guid = secrets.token_bytes(int(tmpl["frame3_token"]["guid_length"]))

    constant_overrides: dict[str, str] = {}
    if randomize_constants:
        all_names = list(tmpl.get("constants", {}))
        names = all_names if randomize_constants is True else [n for n in all_names if n in randomize_constants]
        constant_overrides = {name: str(uuid.uuid4()) for name in names}

    frames: dict[int, bytes] = {}
    for idx in (1, 2, 3):
        spec = tmpl["frames"][str(idx)]
        body = bytearray(bytes.fromhex(spec["hex"]))
        _render_counter(body, counter_base + delta * (idx - 1), counter_spec)
        if idx == 3:
            _render_frame3_ticket(body, ticket_guid, tmpl["frame3_token"])
        if constant_overrides:
            _apply_constants(body, idx, constant_overrides)
        frames[idx] = bytes(body)

    templates_4to7 = {idx: bytes.fromhex(tmpl["frames"][str(idx)]["hex"]) for idx in (4, 5, 6, 7)}
    if constant_overrides:
        block4 = bytearray(templates_4to7[4])
        _apply_constants(block4, 4, constant_overrides)
        templates_4to7[4] = bytes(block4)

    if platform_version and platform_version != SYNTH_TEMPLATE_VERSION:
        # Declare the live platform version (not the 8.3 template version) so a newer client (8.5) accepts the
        # handshake instead of rejecting a major-version mismatch. Done last so offset-based rendering is intact.
        frames = {i: _inject_platform_version(f, platform_version) for i, f in frames.items()}
        templates_4to7 = {i: _inject_platform_version(f, platform_version) for i, f in templates_4to7.items()}

    return SynthesizedBootstrap(
        frames=frames,
        counter_base=counter_base,
        ticket_guid=ticket_guid,
        templates_4to7=templates_4to7,
    )
