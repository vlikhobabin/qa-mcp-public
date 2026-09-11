## Context

Card 122 (`nuitka-protocol-build-stage`) already per-module compiles `qa_mcp/protocol/*.py → .so` in a
`python:3.13` builder stage and drops the readable `.py` from the final image (`docker/compile_protocol.sh` +
`docker/Dockerfile.thin`). The non-protocol modules still ship as readable `.py`. Two reasons to compile them too:
(1) their `#` comments carry 86 internal R&D tokens (card/Vanessa/evidence) that the card-123 acceptance requires
gone from the image; (2) compiling `mcp_server.py` + `license_gate.py` makes the card-121 startup gate
**non-removable** (the `check` call can't be edited out of a `.so`) — the coupling-correction prerequisite before
the gate is turned ON.

Measured surface (offline, 2026-06-27):
- Non-protocol **leaf** modules to compile (15 + `mcp_server` + `license_gate`): `mcp_server.py`, `license_gate.py`,
  `data/odata.py`, `debug/{gates,measure}.py`, `regression/{checks,harness,versioning}.py`,
  `scenario/{actions,autofill,gherkin,model,replay,reporting,runner,smoke}.py` — together 86 R&D tokens.
- Modules that must stay source: every package `__init__.py` (Nuitka rejects a package `__init__.py` as a
  `--module` target) **and** `regression/__main__.py` (it is a `python -m qa_mcp.regression` entrypoint, which
  needs a runnable code object that a compiled extension module does not provide). These carry ~7 R&D tokens in
  `data/__init__.py`, `scenario/__init__.py`, `_bundled/__init__.py`, `regression/__init__.py`,
  `regression/__main__.py`.

## Goals / Non-Goals

**Goals:**
- The non-protocol leaf modules ship only as native `.so`; their `.py` (and comments) are absent from the image.
- `mcp_server.py` + `license_gate.py` ship as `.so` so the startup gate cannot be edited out.
- A recursive `grep` over the shipped `qa_mcp` package returns zero `card [0-9]` / `Vanessa` / `evidence` tokens.
- The image still launches the MCP server, lists 62 tools, drives the read path; the dev `.py` path stays green.

**Non-Goals:**
- No dev-source edits — build-time transform only (the dev repo keeps all comments and docstrings).
- Not re-compiling `protocol/` (already done by card 122) or changing the `_bundled` encryption read path.
- Not cleaning runtime-exposed docstrings — that is the sibling change `product-facing-tool-descriptions`.

## Decisions

- **Per-module compile, mirror the card-122 recipe.** Reuse the proven `nuitka --module <file>` per-module approach.
  Extend the build so it also compiles the non-protocol leaf modules and places each resulting `.so` back into its
  own subpackage dir (`data/`, `debug/`, `regression/`, `scenario/`, package root), then deletes the matching
  `.py`. (Alternative: a single bundled `.so` per subpackage — rejected for the same reason card 122 rejected it:
  it breaks `Path(__file__)` data resolution and over-bundles.)
- **Drive the compile from an explicit module list, not a blind glob.** Unlike `protocol/*.py`, the non-protocol
  surface spans subpackages and contains files that must stay source (`__init__.py`, `__main__.py`). Pass an
  explicit list of repo-relative module paths to the compile step (extend `compile_protocol.sh` to accept a list,
  or add a sibling `compile_modules.sh`) so the source-staying files are never compiled by accident.
- **`mcp_server.py` is safe to compile (entrypoint check).** The product entrypoint is the console script
  `qa-native-mcp = "qa_mcp.mcp_server:main"` — an `import qa_mcp.mcp_server; main()` (attribute access), which
  resolves against the compiled `.so` exactly like a `.py`. It does **not** rely on `if __name__ == "__main__"`,
  so compilation does not break launch. The build smoke must import the compiled entrypoint and assert 62 tools.
- **Keep `__init__.py` and `regression/__main__.py` as source, then comment-strip them.** `__init__.py` can't be a
  Nuitka `--module` target; `regression/__main__.py` must stay a runnable code object for `python -m`. These ~5
  files carry ~7 R&D tokens, so add a build-time **comment-strip pass** (drop `#` comment lines / the token-bearing
  trailers) over the source-staying `.py` in the image so the `grep == 0` acceptance holds. This is a build-time
  transform on the installed copy — the dev source is untouched (card-122 D6 principle). `regression/__main__.py`
  stays a thin dispatcher that imports the compiled `regression.harness` `.so`, so `python -m qa_mcp.regression`
  keeps working.
- **Assert, don't assume.** The final stage must, like card 122, end with hard assertions: no readable non-protocol
  leaf `.py` remains (only `__init__.py`/`__main__.py`), the recursive R&D-token grep is zero, and the compiled
  entrypoint imports and lists 62 tools.

## Risks / Trade-offs

- [Compiling `regression/__main__.py` would break `python -m qa_mcp.regression`] → Keep `__main__.py` as source
  (comment-stripped); compile only the logic modules it imports (`harness`, `checks`, `versioning`).
- [A source-staying wrapper still carries an R&D token after strip] → The build ends with a hard `grep == 0`
  assertion that fails the build, so a missed token cannot ship silently.
- [A compiled module breaks a runtime import path (relative/cross-package import)] → The card-122 per-module recipe
  already proved relative + cross-package imports resolve against sibling `.so`; the build-time import smoke
  (entrypoint + 62 tools + a read-path drive) catches any regression before the image is trusted.
- [`Path(__file__)`-based data resolution breaks when a module becomes `.so`] → Per-module compile keeps each
  subpackage dir + its `__init__.py` and data files in place, so `__file__` still resolves (same property card 122
  relied on for `protocol/` data + the `_bundled` read path).

## Migration Plan

Build-time only; no runtime migration. Rollback = revert the `compile_protocol.sh`/`Dockerfile.thin` extension; the
dev source already runs uncompiled. The dev `.py` test path is unaffected throughout.

## Open Questions

- None blocking. If `python -m qa_mcp.regression` is judged not a shipped product surface, `regression/__main__.py`
  could instead be removed from the image rather than comment-stripped; defaulting to keep-and-strip preserves the
  current behavior with no functional loss.
