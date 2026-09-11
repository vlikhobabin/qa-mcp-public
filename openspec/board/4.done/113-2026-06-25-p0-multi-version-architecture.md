# 113. P0 — multi-version protocol-asset architecture

## Status
4.done

## Order Index
113

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Parent epic 112 (multi-platform 8.5 + 8.3). Foundational design phase — **can start immediately, in parallel
  with P1 (114); does NOT need 8.5 data** (lands with 8.3 populated and an empty 8.5 slot).

## Summary
Make the package select its bundled protocol assets (genuine captures, frame templates, accepted_mappings) by
**platform version**. Today the resolvers point at a single 8.3.27 set under `src/qa_mcp/_bundled/`. Introduce a
per-version layout + version-aware resolution so a second (8.5) set can drop in without touching call sites.

## Scope
1. **Per-version bundled layout:** migrate the current assets into `src/qa_mcp/_bundled/<version-key>/…`
   (e.g. `8.3/`), leaving an empty `8.5/` slot. `version-key` = the major-minor family (`8.3`, `8.5`); the full
   captured `8.x.y.z` is recorded in that set's manifest.
2. **Version detection + selection:** reuse `regression.versioning.platform_version_from_root`; add a
   `version_key(platform_version)` mapping and an active-version resolver with precedence
   `QA_MCP_PLATFORM_VERSION` env → `PLATFORM_ROOT`-derived → default. Thread the active version into
   `resolve_capture_dir`, `_bundled.template`, `default_accepted_mappings_path`.
3. **Fail-closed:** an unsupported platform version yields a clear error
   ("no protocol assets bundled for platform 8.x — supported: 8.3, 8.5; capture per docs/capture-refresh-runbook").
4. **Per-version manifest:** `config/protocol-capture-manifest.json` becomes per-version (a list or
   `…-<version-key>.json`); the drift detector compares against the set matching the live version.
5. **Parametrize `scripts/bundle_runtime_assets.py`** by version (source dir + target `_bundled/<key>/`).
6. **No 8.3 regression:** all current 8.3 resolution + the 475 offline tests stay green.

## Acceptance
- Resolvers return the 8.3 set for an 8.3 platform and would return the 8.5 set for an 8.5 platform; 8.3 path
  unchanged at runtime; an unknown version fails closed with a specific message.
- A unit test asserts version→set selection for 8.3 / 8.5 / unknown.
- `pytest` green (475 + the new selection tests); wheel still ships the (8.3) assets self-contained.

## Dependencies
- none — pure architecture/refactor; can land before any 8.5 capture exists.

## Verify
- Offline: the new selection tests + the existing suite; build the wheel and confirm `_bundled/8.3/…` resolves
  in a clean env (as the current self-containment proof does).

## Archive
- not started

## Result
- **✅ DELIVERED (epic 112).** The multi-version protocol-asset architecture landed: the version-keyed
  `_bundled/<8.3|8.5>/` layout, version-aware resolvers, a per-version manifest and `QA_MCP_PLATFORM_VERSION`
  selection. Proven by the 8.5 vertical slice — qa-mcp drives a live 8.5 client off this layout (the 8.5 slot
  falls back to the byte-identical 8.3 set; see epic 112 Result). Shipped in `main` (epic-112 commits
  303fbbb…2d98c8d).

## Log
- 2026-06-25 created under epic 112. Foundational, parallel with P1.
- 2026-06-29 board hygiene: moved 1.backlog → 4.done (delivered as part of epic 112's validate-first outcome).
