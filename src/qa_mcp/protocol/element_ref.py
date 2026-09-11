"""Card 86a — capture-free element addressing.

The element-addressing spike (docs/protocol-research/evidence/card86-element-addressing-spike-2026-06-16)
decoded how a manager command frame names its target element: a **length-prefixed hierarchical path string**
(latin1), `<tag 0x9a><len:1><path>`, where

    path = SecondaryFrame[<S>].ManagedForm[<F>].Group[<g1>]…​.<Kind>[<NAME>]

and there is NO hidden per-element id/GUID. Every component is already in hand: the SecondaryFrame `S` /
ManagedForm `F` GUIDs from the handshake (`GuidRebinder`), and the group path + leaf name from
`read_form_summary` introspection. This module builds that path (`ElementRef`) and, crucially, RE-TARGETS the
path inside an existing command frame to a different element (`retarget_element_path`) — recomputing the
1-byte length prefix, since frames are tail-marker delimited (no total-length field), so the frame just
grows/shrinks by the path-length delta. This is the foundation that lifts actions off per-flow captures: the
command structure comes from a per-element-TYPE template, the address from the live form descriptor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as _field

# An element path is a run of `Kind[token].Kind[token]…` segments starting at SecondaryFrame.
_PATH_RE = re.compile(
    rb"SecondaryFrame\[[^\]]+\](?:\.[A-Za-z0-9_]+\[[^\]]*\])+"
)
# A single `Kind[NAME]` segment (for leaf swaps).
_SEGMENT_RE = re.compile(r"([A-Za-z0-9_]+)\[([^\]]*)\]")


@dataclass(frozen=True)
class ElementRef:
    """A form element addressed by its hierarchical path. `secondary_frame` / `managed_form` are the live
    session GUIDs; `groups` is the ordered list of enclosing Group names; `kind`/`name` is the leaf
    (e.g. EditField/PF_EDIT_STRING, CommandBarButton/FormCommandSave, TableBox/PF_TABLE)."""

    secondary_frame: str
    managed_form: str
    groups: list[str] = _field(default_factory=list)
    kind: str = "EditField"
    name: str = ""

    def path(self) -> str:
        parts = [f"SecondaryFrame[{self.secondary_frame}]", f"ManagedForm[{self.managed_form}]"]
        parts += [f"Group[{g}]" for g in self.groups]
        parts.append(f"{self.kind}[{self.name}]")
        return ".".join(parts)

    def with_leaf(self, name: str, kind: str | None = None) -> "ElementRef":
        return ElementRef(self.secondary_frame, self.managed_form, list(self.groups), kind or self.kind, name)


def build_element_path(
    secondary_frame: str, managed_form: str, groups: list[str], name: str, kind: str = "EditField"
) -> str:
    """Build the wire element path from its components (the live GUIDs + the introspected group/leaf)."""
    return ElementRef(secondary_frame, managed_form, list(groups), kind, name).path()


def parse_element_path(path: str) -> ElementRef:
    """Inverse of `build_element_path`: split a path string back into an `ElementRef`."""
    segs = _SEGMENT_RE.findall(path)
    if len(segs) < 3 or segs[0][0] != "SecondaryFrame" or segs[1][0] != "ManagedForm":
        raise ValueError(f"not a SecondaryFrame.ManagedForm…leaf path: {path!r}")
    secondary, managed = segs[0][1], segs[1][1]
    groups = [name for kind, name in segs[2:-1] if kind == "Group"]
    leaf_kind, leaf_name = segs[-1]
    return ElementRef(secondary, managed, groups, leaf_kind, leaf_name)


def extract_element_paths(frame: bytes) -> list[str]:
    """All `SecondaryFrame[…]…<Kind>[NAME]` element paths in a command frame (latin1), de-duplicated in
    first-appearance order. Use to read the captured path out of a template frame before retargeting."""
    seen: list[str] = []
    for m in _PATH_RE.finditer(frame):
        p = m.group(0).decode("latin1")
        if p not in seen:
            seen.append(p)
    return seen


def retarget_element_path(frame: bytes, old_path: str, new_path: str) -> tuple[bytes, int]:
    """Replace the length-prefixed element path ``old_path`` -> ``new_path`` in ``frame`` and recompute the
    1-byte length prefix. Frames are tail-marker delimited (no frame total-length field — proven for the
    value field in `native_write`), so the frame simply grows/shrinks by the path-length delta. Returns
    ``(frame, substitutions)``; raises if the length-prefixed path is absent or the new path exceeds 255."""
    ob, nb = old_path.encode("latin1"), new_path.encode("latin1")
    if len(nb) > 255:
        raise ValueError(f"element path is {len(nb)} bytes; the 1-byte length prefix supports up to 255")
    old_block = bytes([len(ob)]) + ob
    new_block = bytes([len(nb)]) + nb
    count = frame.count(old_block)
    if count == 0:
        raise ValueError(f"length-prefixed element path not found (len {len(ob)} + {old_path!r})")
    return frame.replace(old_block, new_block), count


def retarget_element_leaf(frame: bytes, old_name: str, new_name: str, *, kind: str = "EditField") -> tuple[bytes, int]:
    """Convenience: re-target every element path in ``frame`` whose leaf is ``kind[old_name]`` to
    ``kind[new_name]`` (same enclosing groups), recomputing each length prefix. Returns ``(frame, paths_changed)``."""
    old_leaf, new_leaf = f"{kind}[{old_name}]", f"{kind}[{new_name}]"
    changed = 0
    out = frame
    for path in extract_element_paths(frame):
        if path.endswith(old_leaf):
            out, _ = retarget_element_path(out, path, path[: -len(old_leaf)] + new_leaf)
            changed += 1
    if changed == 0:
        raise ValueError(f"no element path with leaf {old_leaf!r} found")
    return out, changed


def retarget_element_leaf_any(frame: bytes, old_name: str, new_name: str, *, kind: str = "Button") -> tuple[bytes, int]:
    """Re-target ``kind[old_name]`` -> ``kind[new_name]`` whether the element path is encoded **ASCII** (latin1,
    the `<0x9a><byte-len:1>` form used for ASCII names like the fixture `PF_*`) or **UTF-16LE** (Cyrillic names
    on a real config / the dynlist's auto-generated commands — card 98). Tries the ASCII retarget
    (``retarget_element_leaf``) first; if the leaf is not present as ASCII, does a UTF-16LE byte-replace of
    ``kind[old]`` -> ``kind[new]``. The UTF-16 branch requires the **same character length** (a direct
    byte-replace that leaves the path's char-count length prefix untouched — resizing a UTF-16 path's varint
    char-count prefix is a documented refinement). Returns ``(frame, leaves_changed)``."""
    try:
        return retarget_element_leaf(frame, old_name, new_name, kind=kind)  # ASCII (latin1, 1-byte len)
    except ValueError:
        pass
    old_u16 = f"{kind}[{old_name}]".encode("utf-16-le")
    new_u16 = f"{kind}[{new_name}]".encode("utf-16-le")
    count = frame.count(old_u16)
    if count == 0:
        raise ValueError(f"no element path with leaf {kind}[{old_name}] (ASCII or UTF-16LE)")
    if len(new_u16) != len(old_u16):
        raise ValueError(
            f"UTF-16 leaf retarget needs the same char length: {old_name!r} ({len(old_name)}) -> "
            f"{new_name!r} ({len(new_name)}) — resizing the UTF-16 char-count prefix is a refinement")
    return frame.replace(old_u16, new_u16), count


def retarget_element_leaf_reencode(frame: bytes, old_name: str, new_name: str, *, kind: str = "EditField") -> tuple[bytes, int]:
    """Re-target ``kind[old_name]`` -> ``kind[new_name]`` by replacing whole element-path string blocks.

    Unlike ``retarget_element_leaf_any``'s raw UTF-16 fallback, this helper can resize and re-encode the path
    envelope because it operates on complete ``SecondaryFrame...<Kind>[name]`` paths. It handles ASCII->ASCII,
    ASCII->UTF-16, UTF-16->UTF-16 and UTF-16->ASCII when the frame carries a normal element-path block.
    """
    changed = 0
    out = frame
    old_leaf = f"{kind}[{old_name}]"
    new_leaf = f"{kind}[{new_name}]"
    for path in [*extract_element_paths(frame), *extract_element_paths_utf16(frame)]:
        if not path.endswith(old_leaf):
            continue
        new_path = path[: -len(old_leaf)] + new_leaf
        old_block = encode_element_path_block(path)
        new_block = encode_element_path_block(new_path)
        count = out.count(old_block)
        if count:
            out = out.replace(old_block, new_block)
            changed += count
    if changed == 0:
        raise ValueError(f"no element path with leaf {kind}[{old_name}] (ASCII or UTF-16LE)")
    return out, changed


# --- Card 98 #1: UTF-16 element paths (Cyrillic group/leaf names) ---
#
# An ASCII element path rides as ``0x9a <byte-len:1> <latin1 path>``; a path containing a non-latin1
# (Cyrillic) component — a Group or leaf name on a real config, or the fixture's `Группа1` / `Контрагент`
# fields — rides as ``0x97 <char-count:1> <utf-16le path>`` (the same 0x9a/0x97 single-byte/UTF-16 string
# envelopes seen on field values). The whole path string is one encoding: if ANY component is Cyrillic the
# entire path (GUIDs included) is UTF-16. So enumerating and retargeting a Cyrillic field needs the 0x97 form.
_SECONDARYFRAME_UTF16 = "SecondaryFrame[".encode("utf-16-le")


def path_is_latin1(path: str) -> bool:
    """True when ``path`` encodes as latin1 (the ASCII 0x9a wire envelope); False when it carries a
    non-latin1 (Cyrillic) component and so must ride as the 0x97 UTF-16 envelope."""
    try:
        path.encode("latin1")
        return True
    except UnicodeEncodeError:
        return False


def encode_element_path_block(path: str) -> bytes:
    """Encode an element path as its on-wire ``<tag><len:1><bytes>`` string block: an ASCII path as
    ``0x9a <byte-len> <latin1>``, a path with a Cyrillic component as ``0x97 <char-count> <utf-16le>``
    (char-count = UTF-16 code units). The 1-byte length caps a path at 255 bytes (ASCII) / 255 code units
    (UTF-16) — beyond that a multi-byte length is a generalization refinement (real configs, card 98 #3)."""
    if path_is_latin1(path):
        b = path.encode("latin1")
        if len(b) > 255:
            raise ValueError(f"element path is {len(b)} bytes; the 1-byte length prefix supports up to 255")
        return b"\x9a" + bytes([len(b)]) + b
    b = path.encode("utf-16-le")
    char_count = len(b) // 2
    if char_count > 255:
        raise ValueError(f"element path is {char_count} chars; the 1-byte char-count prefix supports up to 255")
    return b"\x97" + bytes([char_count]) + b


def extract_element_paths_utf16(frame: bytes) -> list[str]:
    """All UTF-16LE-encoded ``SecondaryFrame[…]…<Kind>[NAME]`` element paths in a command/query frame
    (the ``0x97 <char-count:1> <utf-16le>`` envelope — Cyrillic group/leaf names), de-duplicated in
    first-appearance order. The UTF-16 twin of ``extract_element_paths`` (which sees only the ASCII 0x9a
    form). Card 98 #1: use to enumerate the Cyrillic-named fields the form-analysis sweep queries
    (e.g. ``Group[Группа1].EditField[Контрагент]``)."""
    seen: list[str] = []
    start = 0
    while True:
        i = frame.find(_SECONDARYFRAME_UTF16, start)
        if i < 0:
            break
        start = i + 2
        if i < 2 or frame[i - 2] != 0x97:      # require the UTF-16 string tag right before the path
            continue
        char_count = frame[i - 1]
        raw = frame[i:i + 2 * char_count]
        if len(raw) < 2 * char_count:
            continue
        try:
            p = raw.decode("utf-16-le")
        except UnicodeDecodeError:
            continue
        if p.endswith("]") and "[" in p and p not in seen:
            seen.append(p)
    return seen


def retarget_element_path_reencode(frame: bytes, old_path: str, new_path: str) -> tuple[bytes, int]:
    """Replace the on-wire element-path block ``old_path`` -> ``new_path``, **re-encoding the string
    envelope** when the encoding changes. The captured value-read query addresses an ASCII leaf
    (``0x9a``); retargeting it to a Cyrillic-named field needs the ``0x97`` UTF-16 envelope, so the tag
    byte itself changes — ``retarget_element_path`` keeps the tag and only works ASCII->ASCII. Locates the
    ASCII block ``0x9a <byte-len> <old_path>`` and swaps the whole block (tag included) for
    ``encode_element_path_block(new_path)``. Returns ``(frame, count)``; raises if the ASCII block is absent
    (card 98 #1)."""
    ob = old_path.encode("latin1")
    old_inner = bytes([len(ob)]) + ob
    idx = frame.find(old_inner)
    if idx < 1 or frame[idx - 1] != 0x9A:
        raise ValueError(f"ASCII element-path block (0x9a) not found for {old_path!r}")
    old_block = b"\x9a" + old_inner
    new_block = encode_element_path_block(new_path)
    return frame.replace(old_block, new_block), frame.count(old_block)


def retarget_element_segment(frame: bytes, old_name: str, new_name: str, *, kind: str = "Table") -> tuple[bytes, int]:
    """Re-target a MID-path element SEGMENT ``kind[old_name]`` (not the leaf) to ``kind[new_name]`` in every
    element path that contains it, recomputing each length prefix. The table-cell analog of
    ``retarget_element_leaf`` for the enclosing ``Table[<name>]`` (TableBox) segment: a cell path is
    ``…Group[…].Table[<table>].EditField[<column>]``, so the table is a segment and the column is the leaf
    (card 90 / 86e). Returns ``(frame, paths_changed)``; raises if no path contains the segment."""
    old_seg, new_seg = f"{kind}[{old_name}]", f"{kind}[{new_name}]"
    changed = 0
    out = frame
    for path in extract_element_paths(frame):
        if old_seg in path:
            out, _ = retarget_element_path(out, path, path.replace(old_seg, new_seg))
            changed += 1
    if changed == 0:
        raise ValueError(f"no element path with segment {old_seg!r} found")
    return out, changed
