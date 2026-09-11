# 123. Scrub R&D references from the SHIPPED surface (dev research source preserved)

## Status
4.done

## Order Index
123

## Owner
unassigned

## OpenSpec Stage
artifacts

## Change Set
Ordered, apply-ready. Independent of cards 121/122 except where noted (Change 2
extends the card-122 Nuitka stage). Change 1 is a real in-repo source edit (tool
docstrings); Change 2 is a build-time transform (compile = no source deletion).
1. `openspec/changes/product-facing-tool-descriptions/` — rewrite all
   `mcp_server.py` tool docstrings product-facing (no card/vanessa/evidence);
   relocate any card trace to `#` comments. Capability `qa-mcp-clean-tool-surface`.
2. `openspec/changes/compile-shipped-nonprotocol-modules/` — extend the card-122
   Nuitka build stage to compile `mcp_server.py` + `license_gate.py` + the other
   shipped non-protocol modules so their `#` comments leave the image (and the
   gate-bearing modules become non-removable `.so`). Capability
   `qa-mcp-comment-free-image`.

## Next
- PUBLISHED 2026-06-28 in commit `5712049` (on `main`). Delivery-protection remaining:
  121 Ch2 (broker-in-image), 121 Ch3 (activation + turn gate ON), 122 Ch3 (CI) — see
  `docs/program-delivery-protection-handoff.md`.

## Result
DONE 2026-06-27. Both changes implemented, verified and archived:
- **Change 1 `product-facing-tool-descriptions`** (`4.done` archive
  `2026-06-27-product-facing-tool-descriptions`): rewrote 57 of 62 `mcp_server.py`
  tool docstrings product-facing (156 token hits → 0), applied by AST line-span
  (AST-identical with docstrings normalized = zero logic change); new gate test
  `tests/test_clean_tool_surface.py`. Cap `qa-mcp-clean-tool-surface` synced.
- **Change 2 `compile-shipped-nonprotocol-modules`** (`4.done` archive
  `2026-06-27-compile-shipped-nonprotocol-modules`): `docker/compile_modules.sh` +
  `docker/strip_source.py` + `Dockerfile.thin` extension — compile the 16 non-protocol
  leaf modules (incl. `mcp_server.py`+`license_gate.py` → gate non-removable) to `.so`,
  strip the `__init__.py` docstrings, drop the dev `python -m qa_mcp.regression` CLI.
  Cap `qa-mcp-comment-free-image` synced.
- **Verified on `qa-mcp-thin:c123` (359MB):** image grep `card [0-9]|[Vv]anessa|evidence/`
  = 0; 0 readable leaf `.py`; gate ships `.so`-only (nuitka loader); MCP HTTP serves
  **62 tools, 0 runtime-description leaks**; offline `pytest` **546 passed**. Evidence
  `.artifacts/openspec/compile-shipped-nonprotocol-modules/20260627-card123-change2/`.

## Source
- 2026-06-27 public-delivery audit. After the hygiene fixes (commit `a5b2f45`) and the IP-protection card 122
  (Nuitka + encrypt), the remaining "research data in free access" is the **internal R&D references** that ship in
  the readable + runtime-exposed surface. Memory [[qa-mcp-public-delivery-prep]].
- User initially deferred this ("пока не трогаем") but then asked to raise it with the right scope — because one
  channel (runtime tool descriptions) is exposed to **every** connecting agent **without any reverse-engineering**,
  so it is arguably the LEAST-protected of all the research leaks.

## What leaks (measured 2026-06-27)
- **Channel C — runtime MCP tool descriptions (highest exposure):** FastMCP sends the `mcp_server.py` tool
  **docstrings** to every agent on `tools/list`. They contain **185** card/vanessa/evidence references, incl.
  **68 mentions of "Vanessa"** ("card 98 #3, the search_for_steps-equivalent (vanessa-mcp parity, no Vanessa)",
  "replaces vanessa-mcp's …", …). Visible in normal use, no `docker cp` needed.
- **Channel A — readable shipped `.py` (outside `protocol/`):** `mcp_server.py` + the other non-protocol modules
  ship as `.py` with internal comments (card refs, findings). (The `protocol/` crown-jewel comments are already
  removed from the image by the card-122 Nuitka compile, which drops comments; the deep findings there stay in
  dev.)

## Design — preserve dev research; clean only the SHIPPED surface (the D6 principle of card 122)
**The dev repo stays research-complete. We do NOT delete research knowledge from the source.** The deep research
memory — `docs/protocol-research/`, `openspec/`, `evidence/`, the board, git history, and the `protocol/*.py`
comments — is **never shipped** (`.dockerignore` / dropped by compilation) and is **out of scope here**. Future
R&D (new platform, optimization, refactor) is unaffected: it works on the dev `.py` + docs as today.

**D1 — Tool descriptions become product-facing (required: they are runtime-exposed).** Rewrite each
`mcp_server.py` tool docstring to describe **what the tool does** for the user/agent, with **no** card numbers,
"Vanessa"/"vanessa-mcp", or `evidence/` paths. Where a card trace is useful for maintenance, move it to a
`#` comment above the function (dev-only context) — NOT the docstring. Clean tool descriptions are also just
better product UX. (The deep findings are not in the tool docstrings; they live in `protocol/` comments + docs +
the board — untouched — so research value lost here is minimal.)

**D2 — Drop the readable internal comments from the IMAGE via build-time compile, not source deletion.** Extend
the card-122 Nuitka stage to also compile `mcp_server.py` + the other shipped non-protocol modules (lifecycle,
scenario, regression, …) so their `.py` comments are removed from the image while the dev source keeps them.
(Alternative if a module must stay `.py`: a build-time comment-strip pass. Either way the source is not edited.)
Note: compilation does NOT hide the runtime-exposed docstrings — that is why D1 is still required. Compiling
`mcp_server.py` + `license_gate.py` also makes the card-121 startup gate **non-removable** (you cannot edit the
`check` call out of a `.so`) — this is the coupling-correction prerequisite before `license-activation-bootstrap`
turns the gate ON.

**D3 — Out of scope (explicitly preserved):** `docs/`, `openspec/`, `evidence/`, `board/`, git, and all
`protocol/` comments/findings. The `_bundled` capture **dir-name** neutralization is owned by card 122 (Change 4).

## Change 1: `product-facing-tool-descriptions`

### Why
Channel C is the highest-exposure leak: FastMCP ships the `mcp_server.py` tool docstrings to **every** connecting
agent on `tools/list` — 185 card/vanessa/evidence refs (68 "Vanessa") visible in normal use with **zero**
reverse-engineering. This is the least-protected research leak and the cheapest to misuse. Cleaning the docstrings
is also straight-up better product UX. Compilation (Change 2) does NOT hide runtime-exposed docstrings, so this
source rewrite is required on its own.

### Goal
Every shipped tool docstring in `src/qa_mcp/mcp_server.py` is product-facing: it describes **what the tool does**
for the user/agent, with **zero** card numbers (`card N`), `Vanessa`/`vanessa-mcp`, or `evidence/` path tokens.
Any maintenance-useful card trace is relocated to a `#` comment above the function (dev-only), not the docstring.
Functional accuracy of every description is preserved.

### Scope
- `src/qa_mcp/mcp_server.py` — the ~60 `@mcp.tool()` docstrings (and any tool-description strings) only.
- This is a genuine in-repo **source edit** (unlike the card-122 build-time transforms): the cleaned docstrings
  are the product surface and stay in dev too.
- Relocate (do not delete) any card-trace context worth keeping to `#` comments above the function.
- Preserve each tool's parameter docs, argument names, return-shape notes and behavioral accuracy.
- Do NOT touch `protocol/` comments, `docs/`, `openspec/`, `evidence/`, the board, or non-docstring logic.

### Acceptance
- Connect an MCP client to the running server; assert every entry in `tools/list` has a `description` containing
  **zero** case-insensitive `card \d`, `vanessa`, or `evidence` tokens.
- A repo-side `grep` over the `@mcp.tool` docstrings confirms the same zero count (an offline check that does not
  need a running server is acceptable as the gating test).
- Offline `pytest` stays green (no behavior change; tool count unchanged at 62).
- Spot-read: descriptions read as clean product documentation and keep functional accuracy.

### Depends On
- none

### Related
- `openspec/changes/product-facing-tool-descriptions/`

### Notes For `$openspec-ff-change`
- Capability `qa-mcp-clean-tool-surface`: the shipped runtime tool-description surface is product-facing and free
  of internal R&D references (card numbers, Vanessa/vanessa-mcp, evidence paths).
- ~60 docstrings / 185 refs — a careful, mechanical reword that must keep functional accuracy. A fan-out workflow
  can parallelize (reword + verify each description) if the operator opts in; default is a single foreground pass.
- The gating test is an offline assertion over the tool docstrings/descriptions (token count == 0); an
  MCP-client `tools/list` check is the equivalent runtime confirmation.

## Change 2: `compile-shipped-nonprotocol-modules`

### Why
Even after Change 1 cleans the runtime-exposed docstrings, the **readable shipped `.py`** outside `protocol/`
(`mcp_server.py` + ~16 non-protocol modules) still carry internal `#` comments (card refs, findings) in the
image. Build-time compilation drops those comments from the image without editing the dev source. Compiling
`mcp_server.py` + `license_gate.py` additionally makes the card-121 startup gate **non-removable** (the `check`
call cannot be edited out of a `.so`) — the coupling-correction prerequisite before the gate is turned ON.

### Goal
Extend the card-122 Nuitka build stage (`docker/compile_protocol.sh` + `docker/Dockerfile.thin`) to per-module
compile the shipped non-protocol modules — `mcp_server.py`, `license_gate.py`, and the `data/`, `debug/`,
`regression/`, `scenario/` modules — to native `.so`, so their `#` comments are absent from the image and the
gate-bearing modules ship only as machine code. The dev source and the MCP entrypoint keep working.

### Scope
- `docker/compile_protocol.sh` (or a sibling/extended compile script) + `docker/Dockerfile.thin`.
- Per-module compile the non-protocol shipped modules: `mcp_server.py`, `license_gate.py`,
  `data/odata.py`, `debug/{gates,measure}.py`, `regression/{checks,harness,__main__,versioning}.py`,
  `scenario/{actions,autofill,gherkin,model,replay,reporting,runner,smoke}.py`.
- Keep package `__init__.py` files as source where needed for package/data resolution (same rule the card-122
  per-module protocol compile used), and keep the MCP **entrypoint launchable** (the server must still start as
  it does today after `mcp_server.py` becomes a `.so`).
- Keep the `_bundled` data files reachable (card-122 encryption read path stays intact).
- This is a **build-time transform only** — no dev-source edits, no logic change.

### Acceptance
- Build `qa-mcp-thin:protected`; `find <image qa_mcp> -path '*qa_mcp*' -name '*.py' -not -name '__init__.py'`
  shows **no** `mcp_server.py` / `license_gate.py` / the listed non-protocol modules as `.py` (they are `.so`).
- `grep -rIE 'card [0-9]|[Vv]anessa|evidence' <image qa_mcp>` returns **zero** (docstrings already cleaned by
  Change 1; comments dropped by compilation).
- The image still starts the MCP server, lists **62 tools**, and `read_form_descriptor` drives a client
  (read path intact); `license_gate.py` is importable from its `.so`.
- Offline `pytest` (dev `.py` path) stays green.

### Depends On
- Change 1 (`product-facing-tool-descriptions`) — the `grep == 0` acceptance assumes docstrings are already clean.
- Card 122 `nuitka-protocol-build-stage` (this extends that build stage; already implemented + in the image).

### Related
- `openspec/changes/compile-shipped-nonprotocol-modules/`

### Notes For `$openspec-ff-change`
- Capability `qa-mcp-comment-free-image`: the shipped image carries no internal R&D references in any readable
  form, and the gate-bearing + non-protocol modules ship as native `.so`.
- Mirror the card-122 per-module compile pattern (keep the package dir + `__init__.py` for data/import resolution;
  only the leaf modules become `.so`). Verify the entrypoint still launches and the 62-tool surface + read path
  are intact before trusting the grep.

## Acceptance (card-level)
- A fresh agent connecting to the shipped image sees **zero** card/vanessa/evidence references in any tool
  description.
- `grep` over the shipped `qa_mcp` in the image returns **zero** internal R&D references (card/vanessa/evidence).
- The dev repo source is **unchanged in research value**: `protocol/` comments, `docs/`, `openspec/`, `evidence/`,
  board, and git history are untouched; new-platform / refactor workflows are unaffected.
- Offline `pytest` stays green; the product README + tool descriptions read as a clean product.

## Open questions / notes
- Volume: ~60 tool docstrings to reword (185 refs) — a careful, mechanical pass; a fan-out workflow can parallelize
  it (reword + verify each tool description keeps its functional accuracy). NOT a logic change.
- Priority: Channel C (runtime) is the most exposed leak and the cheapest to misuse → consider sequencing this
  **before** or alongside card 122, despite the earlier deferral.

## Pointers
- Surface to clean: `src/qa_mcp/mcp_server.py` (tool docstrings + comments). Other shipped `.py`:
  `src/qa_mcp/data/odata.py`, `debug/`, `regression/`, `scenario/`, `license_gate.py`
  (the `protocol/` modules `lifecycle.py`/`screenshot.py`/`windows.py` are already compiled by card 122).
- Build stage to extend: the card-122 Nuitka stage in `docker/Dockerfile.thin` + `docker/compile_protocol.sh`.
- Pairs with: card 122 (compile/encrypt; D6 build-time-not-source principle), card 121 (license — Change 2's
  compile of the gate modules is the prerequisite before the gate is turned ON).

## Log
- 2026-06-27 created. Scope set to the SHIPPED surface only (runtime tool descriptions + readable non-protocol
  `.py`), with the dev research source explicitly preserved. Measured leak: 185 refs / 68 "Vanessa" in
  `mcp_server.py` docstrings (runtime-exposed). Design: rewrite tool docstrings product-facing (D1, required for
  the runtime channel) + extend the Nuitka compile to drop comments from the image (D2); deep research memory
  (docs/openspec/evidence/board/protocol-comments) untouched.
- 2026-06-27 `$opsx-ff`: decomposed into 2 apply-ready changes (`product-facing-tool-descriptions`,
  `compile-shipped-nonprotocol-modules`); caps `qa-mcp-clean-tool-surface`, `qa-mcp-comment-free-image`. Moved to
  `2.todo`. Change 2 carries the card-121/123 coupling correction (compile gate modules → gate non-removable).
- 2026-06-27 `$opsx-do`: both changes implemented, verified on image `qa-mcp-thin:c123` and archived
  (`2026-06-27-product-facing-tool-descriptions`, `2026-06-27-compile-shipped-nonprotocol-modules`). Caps
  `qa-mcp-clean-tool-surface` + `qa-mcp-comment-free-image` synced. Moved to `4.done`. Implementation refinements:
  image grep uses `evidence/` (the bare `protocol.evidence` submodule import is a legit code identifier); the gate
  is asserted non-removable by `.py`-absence + `nuitka_module_loader` (Nuitka reports `__file__` as the `.py`);
  `regression/__main__.py` dropped from the image (the design's documented alternative, not a product surface).
- 2026-06-28 `$opsx-pub`: handoff doc updated; scoped commit `5712049` on `main` (mcp_server docstrings, docker compile/strip, both archived changes + synced specs, gate test, uv.lock follow-on); pushing.
