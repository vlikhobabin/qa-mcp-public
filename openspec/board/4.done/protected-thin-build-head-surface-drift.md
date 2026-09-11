# Card: protected thin-build gate drifted from HEAD's tool/module surface

Status: done
Owner: qa-mcp
Capability: `qa-mcp-comment-free-image`
Change: `sync-protected-build-gates-with-head-surface` (archived `2026-07-09-…`)

## Problem

Rebuilding the protected **thin** delivery image (`docker/Dockerfile.thin`) from
current `main` (`93dfaf6`) **fails to build**. The protected build keeps three
hand-maintained, hard-coded lists/constants that must track the shipped surface
but have no automated guard, and all three drifted after the v0.3.0 build
(`3cb6f00`, the last successful thin build):

1. **Leaf-module compile list** (`docker/compile_modules.sh` `MODULES=()`) and the
   **matching drop list** (`docker/Dockerfile.thin` `for rel in …` loop) omit two
   runtime tool modules added *after* v0.3.0:
   - `com_host.py` — host-side COM query tools (added `7f4677c`)
   - `doctor.py`  — `qa_mcp_doctor` end-to-end diagnostics (added `11a0046`/`847b560`/`ece16b3`)
   Because they are neither compiled to `.so` nor dropped, their readable source
   survives and the final gate `test -z "$(find "$PKG" -name '*.py' ! -name '__init__.py')"`
   aborts the build.
2. **Stage-2 tool-count smoke** (`docker/Dockerfile.thin`, final stage) asserts
   `n==67`, but the true current tool count is **68** — and the two other
   authorities already agree on 68 (`docker/Dockerfile.thin` protected-package
   stage smoke `n==68` + `docker/verify_protected_image.py` `EXPECTED_TOOLS=68`).
   So stage-2's `67` is stale and fails once (1) is fixed.

Net: any future thin release/rebuild from HEAD (the successor to v0.3.0) is
blocked. This is the same class of drift as the v0.3.0 `platform_support/` fix.

## Evidence (already reproduced 2026-07-08 on the Linux dev box)

- Build 1 failed at the "no readable source" gate — leftover `com_host.py` + `doctor.py`.
- After adding both to `compile_modules.sh` MODULES + the Dockerfile drop-list, build
  advanced past encryption to the stage-2 smoke and failed at `assert n==67` (actual 68).
- After aligning stage-2 to `n==68`, the build succeeds:
  `final protected package smoke OK: 68 tools; gate loader= nuitka_module_loader`.
- `docker/verify_protected_image.py` (in-image) green:
  `protected-image OK: 68 tools; gate modules compiled; protocol .so leak scan clean;
  16 bundled data files encrypted and decryptable; license broker present`.
- The compiled `display_backend.so` reports `HOST_AGENT_VERSION 0.1.4-window-by-client-port`
  and emits `client_port` (direct + env `QA_MCP_CLIENT_PORT` paths) — corroborated by
  the live .201 [redacted third-party configuration] auto-window re-proof this session.

The three edits are already applied to the working tree (uncommitted, pending this
card's `do`/`review`/`pub`).

## Change 1: `sync-protected-build-gates-with-head-surface`

Capability: `qa-mcp-comment-free-image` (the protected/comment-free per-module compile).

**What.** Make the protected thin-build track HEAD's actual shipped tool/module
surface instead of stale hard-coded lists:
- Add `com_host.py` and `doctor.py` to `docker/compile_modules.sh` `MODULES=()` and to
  the `docker/Dockerfile.thin` drop/strip loop (keep the two in sync, as the header mandates).
- Align the stage-2 tool-count assertion to the single true value (68), consistent with
  the protected-package stage smoke and `verify_protected_image.py`.
- **Anti-drift (the durable fix):** add a guard so this cannot silently regress —
  e.g. derive the leaf-module list from the package tree (every shipped non-`__init__`
  top-level/leaf `.py` must be compiled or explicitly dropped) and/or derive the
  tool-count from a single source rather than three hand-copied literals. At minimum,
  a build-time assertion that the compile list ∪ drop list == the set of shipped leaf
  modules, so a newly added module fails loudly and early with a clear message.

**Why.** Restores the ability to build/release the thin tester image from HEAD and
prevents the next added module/tool from silently breaking the release build.

**Tasks.**
- [ ] Apply the two-list + tool-count edits (done in working tree; confirm + keep in sync).
- [ ] Add the anti-drift build-time guard (compile∪drop == shipped leaf set; single-source tool count).
- [ ] Verify: `docker build -f docker/Dockerfile.thin` succeeds from HEAD; `verify_protected_image.py` green.
- [ ] Sync the `qa-mcp-comment-free-image` spec delta; archive the change.

## Log
- 2026-07-08: Discovered while rebuilding the thin image for the host-agent 0.1.4 /
  auto-window (`client_port`) end-to-end re-proof. Fix reproduced + verified locally;
  card filed per operator decision to formalize now.
- 2026-07-09: Delivered via OPSX. Change `sync-protected-build-gates-with-head-surface`
  created + validated (`openspec validate --strict` pass), implemented (the 3 edits +
  loud drift gate), verified (fresh `docker build -f docker/Dockerfile.thin` OK;
  in-image `verify_protected_image.py` green — 68 tools, `.so`-only, 16 encrypted
  bundled files, broker present), spec `qa-mcp-comment-free-image` synced (+1 ADDED
  requirement), change archived `2026-07-09-sync-protected-build-gates-with-head-surface`.
