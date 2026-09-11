#!/usr/bin/env python3
"""Card 86 step 0 — element-addressing spike (reproducible).

Decodes HOW a manager command frame addresses its target form element, from EXISTING captures (no new
genuine runs). Method: in one rich genuine capture, manager->client command frames that reference exactly
one EditField are the single-element-targeted commands. Diffing two equal-length, same-TYPE such frames for
DIFFERENT fields isolates the address; probing the bytes before the element path reveals the length prefix.

Finding (genuine-commit-conn): the only differences between two equal-length single-field commands are the
offset-19 counter, the 16-byte nonce, and the element NAME — i.e. the address is the literal element PATH
string `SecondaryFrame[S].ManagedForm[F].Group[..].EditField[NAME]`, length-prefixed (1 byte after a 0x9a
tag). No hidden per-element id/GUID. Run: `uv run --frozen python tools/protocol-research/element_addressing_spike.py`.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_write import _EDITFIELD_RE, _read_chunks  # noqa: E402

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"


def _ascii(b: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def load() -> list[bytes]:
    if not (CAPTURE / "traffic.jsonl").exists():
        sys.exit(f"capture not found (lab-local, gitignored): {CAPTURE}")
    return _read_chunks(CAPTURE, MANAGER_TO_CLIENT)


def single_field_frames(mgr: list[bytes]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = defaultdict(list)
    for i, p in enumerate(mgr):
        fs = {m.group(1).decode("latin1") for m in _EDITFIELD_RE.finditer(p)}
        if len(fs) == 1:
            out[next(iter(fs))].append(i)
    return out


def diff_two_fields(mgr: list[bytes], field_a: str, field_b: str, length: int) -> None:
    def pick(field: str) -> int:
        fb = field.encode()
        for i, p in enumerate(mgr):
            if {m.group(1) for m in _EDITFIELD_RE.finditer(p)} == {fb} and len(p) == length:
                return i
        raise SystemExit(f"no len-{length} single-field frame for {field}")

    ia, ib = pick(field_a), pick(field_b)
    fa, fb = mgr[ia], mgr[ib]
    diffs = [i for i in range(min(len(fa), len(fb))) if fa[i] != fb[i]]
    ranges: list[list[int]] = []
    for i in diffs:
        if ranges and i == ranges[-1][1] + 1:
            ranges[-1][1] = i
        else:
            ranges.append([i, i])
    print(f"\n== diff {field_a}@{ia} vs {field_b}@{ib} (both len {length}) — {len(ranges)} differing ranges ==")
    for s, e in ranges:
        print(f"  [{s:>3}..{e:<3}] {fa[s:e+1].hex():<26} | {fb[s:e+1].hex():<26} | {_ascii(fa[s:e+1])!r} -> {_ascii(fb[s:e+1])!r}")
    print("  (expect: offset-19 counter, 16-byte nonce, and the element-name bytes — nothing else)")


def decode_path(mgr: list[bytes], field: str) -> None:
    fb = field.encode()
    p = next(mgr[i] for i, q in enumerate(mgr) if {m.group(1) for m in _EDITFIELD_RE.finditer(q)} == {fb})
    n = p.find(b"EditField[")
    s = n
    while s > 0 and 32 <= p[s - 1] < 127:
        s -= 1
    path = p[s:n + len(b"EditField[") + len(field) + 1]
    print(f"\n== element path for {field} ==")
    print(f"  2 bytes before path: {p[s-2:s].hex()}  (tag={p[s-2]:#04x}, len-byte={p[s-1]} == path len {len(path)}? {p[s-1] == len(path)})")
    print(f"  path ({len(path)}): {path.decode('latin1')!r}")


def main() -> None:
    mgr = load()
    print(f"genuine-commit-conn: {len(mgr)} manager->client command frames")
    singles = single_field_frames(mgr)
    print(f"single-field-targeted commands cover {len(singles)} distinct fields (~8 frames each)")
    diff_two_fields(mgr, "PF_EDIT_STRING", "PF_EDIT_NUMBER", 273)  # same name length (14), same type
    for field in ("PF_EDIT_DATE", "PF_EDIT_NUMBER", "PF_EDIT_READONLY"):  # 12 / 14 / 16 chars, same group
        decode_path(mgr, field)


if __name__ == "__main__":
    main()
