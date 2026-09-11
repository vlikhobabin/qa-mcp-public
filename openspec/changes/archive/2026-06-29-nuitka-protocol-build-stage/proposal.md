## Why

The most expensive, hardest-won IP in qa-mcp is the **reverse-engineered 1C
TestClient/TestManager protocol** (officially undocumented). The public thin
(model-B) delivery image currently ships it as **open Python source** —
`src/qa_mcp/protocol/` (18 files, ~7,565 LOC, stdlib-only) — so anyone who pulls
the image can read the wire format directly. The user wants the protocol engine
**not shipped as readable source**.

A **Nuitka spike was run and is GREEN** (card 122): per-module compilation of
`src/qa_mcp/protocol/*.py → *.so` works — submodule imports (`from
qa_mcp.protocol.native_write import …`) and the relative imports inside
(`from .frames`, `from .native_mutation`, …) compile and resolve, the compiled
logic executes correctly, and the `.py` source is gone. Nuitka was chosen over a
Go rewrite: same native-binary protection class with **zero rewrite risk** to
the crown-jewel logic.

This change lands the proven compile as the first, self-contained build-time
transform: it ships the `.so` and produces an image-level verification with **no
new crypto** (the `_bundled` data encryption is the adjacent change
`encrypt-bundled-data`).

This change touches **delivery/runtime build config only** (`docker/Dockerfile.thin`);
it requires **only offline capture evidence** plus an image-level smoke (no live
1C runtime, no Vanessa MCP, no EDT/meta snapshots). The dev `src/` source is
unchanged — protection is a build-time transform, not a source edit (the D6
principle), so future protocol R&D, refactor and debug work on the readable `.py`
is unaffected.

## What Changes

- `docker/Dockerfile.thin` becomes **multi-stage**: a `python:3.13` builder
  installs Nuitka + gcc and **per-module-compiles** `src/qa_mcp/protocol/*.py →
  *.so` **in place** (keeping the `protocol/` directory and its data files); the
  final image copies the installed package carrying the `.so` and **no
  `protocol/*.py`**.
- **Per-module compile, keep the `protocol/` dir** (decision D1): the dir and its
  in-package data files survive so `Path(__file__)`-relative loads keep working
  (`bootstrap_frames_1to3.json` for `bootstrap_synth.TEMPLATE_PATH`,
  `assets/calendar_button.png` for `native_xtest`). A single-package `.so` is
  **rejected** — it breaks the synth-bootstrap read path.
- `mcp_server.py` **stays `.py`** (decision D3): it is orchestration (the MCP tool
  wiring), not the RE crown jewel, and the boundary is clean (`from .protocol …`).
- **Scope = the thin (model-B) image only** (decision D5); model A can adopt the
  same stage later.
- **No `src/` code changes.** The dev repo keeps full readable `.py`; only the
  IMAGE ships `.so`. Nuitka also drops `.py` comments from the compiled output, so
  the protocol findings written in `protocol/*.py` comments leave the IMAGE
  automatically while staying intact in dev.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: the thin delivery image ships the protocol engine as
  **compiled native `.so`** (no readable `protocol/*.py`) with full functional
  parity — the MCP server starts, exposes the complete tool surface and drives a
  real client from the compiled build, while the in-package protocol data files
  stay reachable.

## Impact

- **Delivery/build config:** `docker/Dockerfile.thin` (multi-stage builder + final
  copy of the `.so` package). Build-time cost: Nuitka compiling ~18 modules adds
  minutes to the image build (acceptable in CI; `ccache` is a later optimization).
- **No `src/` code; no API/schema change.** The offline `pytest` suite runs the dev
  `.py` path and stays green; an image-level smoke verifies the compiled path.
- **Preserved (out of scope here):** `_bundled` data encryption (`encrypt-bundled-data`),
  the CI wiring (`ci-nuitka-release`), the capture-dir rename (`neutralize-capture-names`),
  the license gate (card 121) and the runtime-docstring scrub (card 123).
