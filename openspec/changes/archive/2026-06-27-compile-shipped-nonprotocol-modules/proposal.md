## Why

After the sibling change cleans the runtime-exposed tool docstrings, the **readable shipped `.py`** outside
`protocol/` (`mcp_server.py` + ~16 non-protocol modules) still carry internal `#` comments (card refs, findings)
in the image. Build-time compilation drops those comments from the image **without editing the dev source**.
Compiling `mcp_server.py` + `license_gate.py` additionally makes the card-121 startup gate **non-removable** — the
`check` call cannot be edited out of a native `.so` — which is the coupling-correction prerequisite before
`license-activation-bootstrap` turns the gate ON.

## What Changes

- Extend the card-122 Nuitka build stage (`docker/compile_protocol.sh` + `docker/Dockerfile.thin`) to per-module
  compile the shipped **non-protocol** modules to native `.so`: `mcp_server.py`, `license_gate.py`,
  `data/odata.py`, `debug/{gates,measure}.py`, `regression/{checks,harness,__main__,versioning}.py`, and
  `scenario/{actions,autofill,gherkin,model,replay,reporting,runner,smoke}.py`.
- Keep package `__init__.py` files as source where needed for package/data resolution (same rule the card-122
  per-module protocol compile used), and keep the MCP **entrypoint launchable** after `mcp_server.py` becomes a
  `.so`.
- Keep the `_bundled` data files reachable so the card-122 encryption read path stays intact.
- Build-time transform only: **no dev-source edits, no logic change.** The dev repo keeps every comment.

This touches the **Docker build / packaging surface** only. It is **offline** (image build + smoke); no live 1C
runtime is required. It extends, and depends on, the card-122 `nuitka-protocol-build-stage`.

## Capabilities

### New Capabilities
- `qa-mcp-comment-free-image`: the shipped image carries no internal R&D references in any readable form, and the
  gate-bearing + non-protocol modules ship as native `.so` (so the license gate cannot be edited out).

### Modified Capabilities
<!-- none: the protocol-compile/encrypt behavior of qa-mcp-protocol-lab is unchanged; this adds a new image-surface contract. -->

## Impact

- Code: `docker/compile_protocol.sh` (extend the per-module compile list) + `docker/Dockerfile.thin` (final image
  copies the non-protocol `.so`, drops their `.py`). No `src/` edits.
- Behavior: the dev `.py` path is unchanged (offline pytest still runs the source); the image runs the compiled
  modules. The MCP entrypoint must still launch and serve 62 tools; the read path must still drive a client.
- Depends on: the sibling change `product-facing-tool-descriptions` (the `grep == 0` acceptance assumes docstrings
  are already clean) and card-122 `nuitka-protocol-build-stage` (the build stage being extended).
- Out of scope / preserved: dev source comments, `docs/`, `openspec/`, `evidence/`, board, git history.
