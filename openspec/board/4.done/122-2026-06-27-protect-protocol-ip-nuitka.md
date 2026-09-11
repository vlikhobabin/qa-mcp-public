# 122. Protect the protocol IP — Nuitka-compile the protocol engine + encrypt the bundled data

## Status
4.done

## Order Index
122

## Owner
unassigned

## OpenSpec Stage
artifacts

## Change Set
Ordered, apply-ready (validated `--strict`). 121 and 122 are COUPLED — build 1
here, then card 121 Change 1 (gate), then 122 Change 2, etc. (see the handoff
implementation order):
1. `openspec/changes/nuitka-protocol-build-stage/` — multi-stage `Dockerfile.thin`,
   per-module compile `protocol/*.py → .so`, no `protocol/*.py` in the image.
2. `openspec/changes/encrypt-bundled-data/` — build-time AES-GCM encrypt of
   `_bundled`; runtime decrypt in compiled code (key in the `.so`).
3. `openspec/changes/ci-nuitka-release/` — wire compile + encrypt into
   `release.yml` (key from a CI secret).
4. `openspec/changes/neutralize-capture-names/` — rename the 13 bundled capture
   dirs + their code defaults to neutral-descriptive (the only in-repo source
   change; lands any time).

## Progress (per change)
- **Ch1 `nuitka-protocol-build-stage`** — DONE (image-buildable), committed `d828f53`.
  **ARCHIVED 2026-06-29** (`changes/archive/2026-06-29-nuitka-protocol-build-stage`;
  spec-synced into `qa-mcp-protocol-lab`). Lab e2e (task 4.2) DEFERRED to the shared
  card-121 Windows-lab gate — non-blocking.
- **Ch2 `encrypt-bundled-data`** — DONE (image-buildable), committed `d828f53`.
  **ARCHIVED 2026-06-29** (`changes/archive/2026-06-29-encrypt-bundled-data`). Lab
  e2e DEFERRED (shared gate) — non-blocking.
- **Ch3 `ci-nuitka-release`** — **DONE + ARCHIVED 2026-06-29**
  (`changes/archive/2026-06-29-ci-nuitka-release`). `release.yml` injects the AES key
  from the `BUNDLED_DATA_KEY` secret (fail-closed without it), builds + loads the
  protected `Dockerfile.thin`, runs `docker/verify_protected_image.py` as a pre-publish
  integrity gate (no readable protocol `.py`; 62 tools; `_bundled` ciphertext), then
  pushes. CI-RUN verification (task 3.1) DEFERRED to the first tagged release.
- **Ch4 `neutralize-capture-names`** — **DONE + committed `8cc5696` + ARCHIVED
  2026-06-29** (`changes/archive/2026-06-29-neutralize-capture-names`). 12/13 bundled
  dirs renamed to neutral names (`tm-v1-ro-batchQ3` left as-is, D3); all `src/` +
  tests + `docker/encrypt_bundled.py` refs updated; offline `pytest` **546 passed**;
  grep proof clean. Evidence at
  `.artifacts/openspec/neutralize-capture-names/20260628-card122-change4/`.

## Result
- **✅ DONE 2026-06-29 — all four changes implemented + archived** (spec-synced into
  `qa-mcp-protocol-lab`, 164→168 reqs). Ch1 compiles `protocol/*.py → .so` (Nuitka,
  per-module), Ch2 encrypts `_bundled` at rest (AES-GCM, key embedded in the compiled
  `.so`), Ch4 neutralized the bundled capture names, and Ch3 wired the protected build
  + key-secret + a pre-publish integrity gate into `release.yml`. The dev repo stays
  full-source — the protection is a build-time transform on the IMAGE only.
- **Deferred external-gate verifications (non-blocking):** the Windows-lab model-B e2e
  (Ch1/Ch2 task 4.2) and the first tagged-release CI run (Ch3 task 3.1).
- Commits: `d828f53` (Ch1/Ch2 impl) + `8cc5696` (Ch4 impl) + the 2026-06-29
  archive/CI commits.

## Next
- Card 122 is DONE. The license **gate is compiled (non-removable) but still OFF by
  default** (`QA_MCP_LICENSE_GATE`). Turning it ON + shipping the broker is card **121**
  (`license-broker-in-image` + `license-activation-bootstrap`) — PAUSED pending the 121
  decisions (broker-binary delivery + live `:8791` activation + Windows lab). The live
  license-server connection facts are recorded in 121-Ch3 `design.md`.

## Source
- 2026-06-27 public-delivery prep. The most expensive, hardest-won IP is the **reverse-engineered 1C
  TestClient/TestManager protocol** (officially undocumented). User wants it **not shipped as open Python source**
  in the public delivery. Memory [[qa-mcp-public-delivery-prep]]; continues the delivery-hygiene audit (card 119/
  120 productization, the GHCR+dist channel).
- Decision basis: a **Nuitka spike was run and is GREEN** (see "Spike result" below) — Nuitka was chosen over a
  Go rewrite because it gives the same native-binary protection class with **zero rewrite risk to the crown-jewel
  logic** (a Go rewrite of 7.5K LOC of the hardest, most-debugged code is high-effort + high-risk for no extra
  protection).

## Threat model + honest framing (scope the investment)
Anything that **executes on the user's machine** can be reverse-engineered — protection RAISES THE COST, it is
not absolute. The real commercial/legal lever is the **product license** (card 121) + ToS; compilation +
encryption stop casual lifting of the source and the wire format. Pure server-side hiding is **not viable**: the
protocol engine must reach the user's TestClient over local TCP, so it must run on the user's machine. Therefore
the protection is client-side hardening of two surfaces:
1. **The protocol CODE** — `src/qa_mcp/protocol/` (18 files, ~7,565 LOC, stdlib-only) → compile to native `.so`.
2. **The protocol DATA** — `src/qa_mcp/_bundled/` (2.2 MB: 13 genuine capture `traffic.jsonl` + 3 templates +
   accepted-mappings) which **literally encodes the wire format** → encrypt at rest in the image.

## Spike result (2026-06-27) — Nuitka PROVEN on the real protocol code ✅
Ran Nuitka 4.1.3 (gcc 15.2) against `src/qa_mcp/protocol/`:
- Compiles the whole package to native `.so` — **both** a single-package `.so` AND **per-module** `.so`.
- **Submodule imports work** from the compiled output (`from qa_mcp.protocol.native_write import …`), and the
  **relative imports** inside (`from .frames`, `from .native_mutation`, …) compile + resolve.
- Compiled logic **executes correctly** (`calendar_month_cell(8) == (985,474)`, frame constants, etc.).
- The `.py` **source is gone** — only machine-code `.so` ships.
- **Per-module compile keeps the protocol DATA reachable**: the `protocol/` dir survives (with
  `bootstrap_frames_1to3.json` + `assets/calendar_button.png`), so `Path(__file__)`-relative loads still work
  (verified `calendar_button.png exists=True`). A **single-package `.so` BREAKS** the read path because
  `bootstrap_synth.TEMPLATE_PATH = Path(__file__).parent / "bootstrap_frames_1to3.json"` no longer resolves.

## Design decisions (from the spike)
**D1 — Per-module Nuitka compile, keep the `protocol/` dir.** Each `protocol/*.py → *.so` in place; the dir (and
its `bootstrap_frames_1to3.json` + `assets/`) is preserved so `__file__`-relative data loads keep working.
(Single-package `.so` rejected: breaks the synth-bootstrap read path.)

**D2 — Compile in a `python:3.13` Docker build stage.** A `.so` is Python-version + arch specific; the thin image
is `python:3.13-slim` / linux-amd64 only, so a build-stage compile matches exactly (Nuitka itself recommends 3.13
over the spike's local 3.14). Multi-stage: builder (`pip install nuitka` + gcc, compile) → final (copy the
package with `.so`, no `.py`).

**D3 — `mcp_server.py` stays `.py`.** It is orchestration (the MCP tool wiring), not the RE crown jewel; the
boundary is clean (`from .protocol …` ×45). (Compiling it has marginal IP value: its tool docstrings are
runtime-exposed to the agent by FastMCP regardless of compilation — that is the separate, deferred R&D-refs
cleanup, NOT this card.)

**D4 — Encrypt the bundled data + decrypt in the compiled loader.** Encrypt each `_bundled` data file at build
time (AES-GCM); the runtime loaders (`resolve_capture_dir`, the `_bundled` template/accepted-mappings loaders)
decrypt in memory. The key lives **inside the compiled `.so`** (machine code), so it is not plaintext in the
image — extracting it requires reversing the binary. The `_bundled` loader currently lives partly OUTSIDE
`protocol/` (`qa_mcp/_bundled/__init__.py`); fold the decrypt path into the compiled protocol package (or compile
`_bundled/__init__.py` too) so the key + decrypt logic are never shipped as readable `.py`.

**D5 — Scope: the thin (model-B) image first.** That is the public delivery. Model A (Linux all-in-container) can
adopt the same build stage later. The dev repo keeps full `.py` source (private); only the IMAGE ships `.so`.

**D6 — Protection is a BUILD-TIME transform; the dev repo stays research-complete (future R&D is NOT hampered).**
Compilation + encryption happen in the image build, NOT by editing the source. Consequence (deliberate): Nuitka
**drops `.py` comments from the compiled output**, so the protocol findings/root-causes written in `protocol/*.py`
comments are removed from the IMAGE automatically while staying intact in the dev `.py`. New-platform support
(e.g. 8.6), optimization and refactoring proceed in the dev `.py` (with all comments + the version-keyed
`_bundled/<8.3|8.5>` layout) exactly as today; the build just recompiles the current source. The deep research
memory — `docs/protocol-research/`, `openspec/`, `evidence/`, the board, git history — is **never shipped**
(`.dockerignore`) and is **not touched** by this card. Only one small source change is in scope here: renaming the
capture dirs (Change 4) to neutral-descriptive names (the card-number/date moves to git + the board; the
descriptive meaning is kept, so research lookup is unaffected).

## Proposed Change Set (for `$opsx-ff`; ordered)
1. **`nuitka-protocol-build-stage`** — multi-stage `docker/Dockerfile.thin`: a `python:3.13` builder installs
   Nuitka + gcc and per-module-compiles `src/qa_mcp/protocol/*.py → *.so` (keeping the dir + data files); the
   final image copies the installed package with the `.so` and **no `protocol/*.py`**. Verify on the built image:
   MCP server starts, 61 tools listed, `read_form_descriptor` drives a client, and `find … -name 'protocol/*.py'`
   is empty. Capability: compiled-protocol delivery.
2. **`encrypt-bundled-data`** — build-time AES-GCM encrypt of `_bundled` captures/templates/mappings; runtime
   decrypt folded into the compiled package (key embedded in the `.so`). Verify: the image's `_bundled` files are
   ciphertext, the engine still opens a form (decrypt works), and tests pass. Capability: encrypted-at-rest
   protocol data.
3. **`ci-nuitka-release`** — wire the compile (+ encrypt) into `.github/workflows/release.yml` so the published
   GHCR image is the protected build; keep the local `docker build` path working; document the added build time.
   Capability: protected release pipeline.
4. **`neutralize-capture-names`** — rename the `_bundled` capture dirs from `genuine-cardNN-<topic>-<date>` to
   neutral-descriptive (`<topic>`, e.g. `demo-write`, `listform-read`, `cellread`) + update the code defaults that
   reference them (`resolve_capture_dir`, the tool `capture=` defaults). Research-safe: the descriptive meaning is
   kept; the card number + date live in git + the board. This is the only in-repo source change in this card.
   Capability: neutral bundled-capture identity.

(Build 1 first — it lands the proven compile + an image-level verification with zero new crypto. Build 2 adds the
data encryption. Build 3 ships it through CI. Build 4 (the small rename) can land any time.)

## Acceptance
- The published thin image contains **no `protocol/*.py`** (only `*.so`); `mcp_server.py` stays `.py` and still
  imports/works against the compiled protocol.
- MCP server starts, exposes the full tool surface, and **drives a real client** (read/assert/scenario) from the
  compiled build — functional parity with the `.py` build.
- `_bundled` data ships **encrypted** in the image; the engine decrypts at runtime; the decrypt key is only in the
  compiled `.so`, never in readable `.py`/plaintext.
- The `release.yml` workflow produces the protected image; dev repo source is unchanged (`.py`, private).
- Offline `pytest` stays green (the dev `.py` source path), and an image-level smoke verifies the compiled path.

## Open questions / notes
- Build-time cost: Nuitka compiling 18 modules adds minutes to the image build — acceptable in CI; measure +
  consider `ccache` (the spike warned ccache was absent) to speed re-builds.
- AES key management: embedded-in-`.so` is "good enough" cost-raising (RE-able, like any client-side key). A
  future option is per-release key rotation; out of scope for v1.
- NOT in scope: the deferred **354 R&D-ref docstring scrub** (separate, runtime-exposed concern); compiling the
  orchestration layer; a Go rewrite (rejected — equal protection, far higher risk).

## Pointers
- Sensitive surfaces: `src/qa_mcp/protocol/` (code), `src/qa_mcp/_bundled/` (data, loaded via
  `protocol/bootstrap.py:resolve_capture_dir` + `qa_mcp/_bundled/__init__.py`).
- Data-file-in-package paths to preserve (D1): `protocol/bootstrap_frames_1to3.json`
  (`bootstrap_synth.TEMPLATE_PATH`), `protocol/assets/calendar_button.png` (`native_xtest`).
- Delivery to modify: `docker/Dockerfile.thin`, `.github/workflows/release.yml`. The MCP boundary:
  `src/qa_mcp/mcp_server.py` (`from .protocol …`).
- Spike env (reproduce): `pip install nuitka`; `cd src && python -m nuitka --module qa_mcp/protocol/<mod>.py
  --include-package=qa_mcp` → `<mod>.cpython-<ver>-<arch>.so`.
- Related: card 121 (product license — the commercial lever this pairs with).

## Log
- 2026-06-27 created. Nuitka spike GREEN on the real protocol code (compiles, submodule + relative imports work,
  logic runs, source gone; per-module keeps the in-dir data files). Decisions fixed: per-module compile in a
  python:3.13 build stage, mcp_server stays .py, encrypt _bundled with the key in the compiled .so, thin image
  first. 3-change set recorded; Nuitka chosen over a Go rewrite (same protection, no crown-jewel rewrite risk).
- 2026-06-27 `$opsx-ff`: decomposed into 4 apply-ready OpenSpec changes (all valid `--strict`):
  `nuitka-protocol-build-stage`, `encrypt-bundled-data`, `ci-nuitka-release`, `neutralize-capture-names`.
  Card → 2.todo, stage → artifacts. Audit during planning: `_bundled/__init__.py` is a SIBLING of `protocol/`
  (decrypt must fold into the compiled package — D4); `capture=` defaults are runtime-exposed via the tool
  schemas (mcp_server stays .py), and only the 13 BUNDLED captures ship — the `genuine-card90/96/97-…` defaults
  resolve from the dev `runtime/` tree (not shipped), so Change 4 scopes to the bundled set; the broader
  runtime-string scrub is card 123. Next = `$opsx-do` Change 1.
