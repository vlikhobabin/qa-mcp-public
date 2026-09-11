"""Card 86a: capture-free element addressing — path build/parse/extract + length-prefixed retarget."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.element_ref import (  # noqa: E402
    ElementRef,
    build_element_path,
    encode_element_path_block,
    extract_element_paths,
    extract_element_paths_utf16,
    parse_element_path,
    path_is_latin1,
    retarget_element_leaf,
    retarget_element_path,
    retarget_element_path_reencode,
)

S = "782a8ba8-d60a-4fec-809a-4e2339cf9e31"
F = "bf814b58-5d69-4ccf-b58d-9a4e23a01f05"


def _path(leaf: str, kind: str = "EditField", groups=("PF_GROUP_MAIN", "PF_GROUP_EDITS")) -> str:
    return ElementRef(S, F, list(groups), kind, leaf).path()


def _framed(path: str, *, tag: int = 0x9A) -> bytes:
    """A synthetic command frame: header + <tag><len><path> + tail marker."""
    pb = path.encode("latin1")
    return b"HDR" + bytes([16] * 16) + bytes([tag, len(pb)]) + pb + b"\xa1\x81\x81TAIL"


def _framed_block(block: bytes) -> bytes:
    """A synthetic command frame wrapping an already-encoded <tag><len><path> block."""
    return b"HDR" + bytes([16] * 16) + block + b"\xa1\x81\x81TAIL"


def test_build_and_path_roundtrip() -> None:
    ref = ElementRef(S, F, ["PF_GROUP_MAIN", "PF_GROUP_EDITS"], "EditField", "PF_EDIT_STRING")
    assert ref.path() == (
        f"SecondaryFrame[{S}].ManagedForm[{F}].Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING]"
    )
    assert build_element_path(S, F, ["PF_GROUP_MAIN", "PF_GROUP_EDITS"], "PF_EDIT_STRING") == ref.path()


def test_parse_element_path() -> None:
    ref = parse_element_path(_path("PF_EDIT_STRING"))
    assert (ref.secondary_frame, ref.managed_form) == (S, F)
    assert ref.groups == ["PF_GROUP_MAIN", "PF_GROUP_EDITS"]
    assert (ref.kind, ref.name) == ("EditField", "PF_EDIT_STRING")


def test_extract_element_paths() -> None:
    frame = _framed(_path("PF_EDIT_STRING"))
    assert extract_element_paths(frame) == [_path("PF_EDIT_STRING")]


def test_retarget_element_path_recomputes_length_and_resizes() -> None:
    old = _path("PF_EDIT_STRING")              # 14-char leaf
    new = _path("PF_V4_SUPPORTED_SCENARIOS")   # longer leaf -> longer path
    frame = _framed(old)
    out, n = retarget_element_path(frame, old, new)
    assert n == 1
    # new path present with its OWN correct 1-byte length prefix; old gone
    assert bytes([len(new.encode())]) + new.encode("latin1") in out
    assert old.encode("latin1") not in out
    # frame grew by exactly the path-length delta
    assert len(out) - len(frame) == len(new.encode()) - len(old.encode())


def test_retarget_leaf_same_group() -> None:
    frame = _framed(_path("PF_EDIT_STRING"))
    out, changed = retarget_element_leaf(frame, "PF_EDIT_STRING", "PF_EDIT_NUMBER")
    assert changed == 1
    assert extract_element_paths(out) == [_path("PF_EDIT_NUMBER")]


def test_retarget_absent_path_raises() -> None:
    with pytest.raises(ValueError):
        retarget_element_path(_framed(_path("PF_EDIT_STRING")), _path("PF_NOT_THERE"), _path("PF_X"))
    with pytest.raises(ValueError):
        retarget_element_leaf(_framed(_path("PF_EDIT_STRING")), "PF_NOPE", "PF_Y")


def test_retarget_rejects_oversized_path() -> None:
    old = _path("PF_EDIT_STRING")
    huge = _path("X" * 250)  # path well over 255 bytes
    with pytest.raises(ValueError):
        retarget_element_path(_framed(old), old, huge)


# --- grounded on a real capture when present (lab-local, gitignored) ---
_CAP = REPO_ROOT / "runtime/protocol-research/captures/tm-v1-ro-batchQ3"


@pytest.mark.skipif(not (_CAP / "traffic.jsonl").exists(), reason="capture tm-v1-ro-batchQ3 not present")
def test_retarget_leaf_on_real_value_read_frame() -> None:
    from qa_mcp.protocol.frames import MANAGER_TO_CLIENT
    from qa_mcp.protocol.native_write import _read_chunks

    mgr = _read_chunks(_CAP, MANAGER_TO_CLIENT)
    frame = mgr[218]  # PF_EDIT_STRING value-read frame
    paths = extract_element_paths(frame)
    assert any(p.endswith("EditField[PF_EDIT_STRING]") for p in paths)
    out, changed = retarget_element_leaf(frame, "PF_EDIT_STRING", "PF_EDIT_NUMBER")
    assert changed >= 1
    assert any(p.endswith("EditField[PF_EDIT_NUMBER]") for p in extract_element_paths(out))
    # the recomputed length prefix keeps the frame self-consistent (grew by 0: same-length leaf names)
    assert len(out) == len(frame)  # PF_EDIT_STRING and PF_EDIT_NUMBER are both 14 chars


# --- Card 98 #1: UTF-16 element paths (Cyrillic group/leaf names) ---

CYR = "SecondaryFrame[{}].ManagedForm[{}].Group[Группа1].EditField[Контрагент]".format(S, F)


def test_path_is_latin1() -> None:
    assert path_is_latin1(_path("PF_EDIT_STRING")) is True
    assert path_is_latin1(CYR) is False


def test_encode_element_path_block_ascii_and_utf16() -> None:
    ascii_block = encode_element_path_block(_path("PF_EDIT_STRING"))
    pb = _path("PF_EDIT_STRING").encode("latin1")
    assert ascii_block == b"\x9a" + bytes([len(pb)]) + pb       # 0x9a byte-len latin1

    u16_block = encode_element_path_block(CYR)
    body = CYR.encode("utf-16-le")
    assert u16_block[0] == 0x97 and u16_block[1] == len(body) // 2  # 0x97 char-count
    assert u16_block[2:] == body
    # the char-count is code units, not bytes
    assert u16_block[1] == len(CYR)


def test_encode_element_path_block_rejects_oversized() -> None:
    with pytest.raises(ValueError):
        encode_element_path_block(_path("X" * 250))                # >255 bytes (ASCII)
    with pytest.raises(ValueError):
        encode_element_path_block(_path("Я" * 250))                # >255 code units (UTF-16)


def test_extract_element_paths_utf16() -> None:
    frame = _framed_block(encode_element_path_block(CYR))
    assert extract_element_paths_utf16(frame) == [CYR]
    # the ASCII extractor does NOT see a UTF-16 path, and vice-versa
    assert extract_element_paths(frame) == []
    assert extract_element_paths_utf16(_framed(_path("PF_EDIT_STRING"))) == []


def test_retarget_reencode_ascii_to_utf16() -> None:
    old = _path("PF_EDIT_STRING")
    frame = _framed(old)                                           # ASCII 0x9a block
    out, n = retarget_element_path_reencode(frame, old, CYR)
    assert n == 1
    # the result now carries the UTF-16 (0x97) path; the ASCII path is gone
    assert extract_element_paths_utf16(out) == [CYR]
    assert old.encode("latin1") not in out
    # frame grew by exactly the block-size delta (UTF-16 block vs ASCII block)
    delta = len(encode_element_path_block(CYR)) - len(encode_element_path_block(old))
    assert len(out) - len(frame) == delta


def test_retarget_reencode_absent_block_raises() -> None:
    with pytest.raises(ValueError):
        retarget_element_path_reencode(_framed(_path("PF_EDIT_STRING")), _path("PF_NOT_HERE"), CYR)


@pytest.mark.skipif(not (_CAP / "traffic.jsonl").exists(), reason="capture tm-v1-ro-batchQ3 not present")
def test_utf16_path_on_real_cyrillic_read_frame() -> None:
    """The genuine form-analysis sweep queries the Cyrillic fields with a 0x97 UTF-16 path (frames 296-303);
    extract + encode must round-trip the on-wire block byte-exactly, and retargeting the ASCII PF_EDIT_STRING
    read (frame 218) to that Cyrillic path must reproduce the genuine frame's length."""
    from qa_mcp.protocol.frames import MANAGER_TO_CLIENT
    from qa_mcp.protocol.native_write import _read_chunks

    mgr = _read_chunks(_CAP, MANAGER_TO_CLIENT)
    # frame 300 = the genuine Контрагент value-read (UTF-16 path)
    cyr_paths = extract_element_paths_utf16(mgr[300])
    assert any(p.endswith("EditField[Контрагент]") and "Group[Группа1]" in p for p in cyr_paths)
    cyr = cyr_paths[0]
    # encode round-trips the genuine on-wire block byte-exactly
    su = "SecondaryFrame[".encode("utf-16-le")
    i = mgr[300].find(su)
    genuine_block = mgr[300][i - 2 : i + 2 * mgr[300][i - 1]]
    assert encode_element_path_block(cyr) == genuine_block
    # retargeting the ASCII read (218) to the Cyrillic path yields the genuine frame length (375 b)
    old = next(p for p in extract_element_paths(mgr[218]) if p.endswith("EditField[PF_EDIT_STRING]"))
    # rebuild with frame-218's live GUIDs (already in the path) + the Cyrillic group/leaf
    ref = parse_element_path(old)
    new = ElementRef(ref.secondary_frame, ref.managed_form, ["Группа1"], "EditField", "Контрагент").path()
    out, _ = retarget_element_path_reencode(mgr[218], old, new)
    assert len(out) == len(mgr[300])
