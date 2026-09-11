# 118. P5 — multi-version delivery (Docker selects 8.3 or 8.5 by the host platform)

## Status
4.done

## Order Index
118

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Parent epic 112. Final phase: ship BOTH platform asset sets in one artifact and select at runtime from the
  user's environment, then generalize the runbook so a third version is a documented procedure.

## Summary
2026-07-06 triage: 8.5 protocol support is already delivered by the validate-first outcome of epic 112, not by a
separate populated `_bundled/8.5` corpus. Keep this backlog card only for the remaining **delivery proof and docs
cleanup**: one public/thin delivery must select the live platform version correctly for 8.3 and 8.5, document the
validate-first rule, and remove any remaining outdated "8.5 bundle must be pre-populated" guidance.

The card is no longer "build 8.5 support"; it is "make the release/runbook evidence match the support already
proved."

2026-08-01 recheck: code/docs already contain the 8.5 validate-first fallback
(`config/protocol-capture-manifest-8.5.json`, `_bundled/8.5/README.md`,
`docs/platform-support.md`) and retained Linux-native 8.5 grid evidence exists
under `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/8-5-grid-smoke/`.
The remaining work is evidence reconciliation and, only if absent for the
current alpha release artifact, one Windows/model-B or accepted equivalent
release-smoke transcript.

## Scope
1. **Release/runbook truth:** update stale references that imply `_bundled/8.5` must be populated before 8.5 can
   run. Current rule: validate with the existing 8.3 protocol data first; re-capture only a red capability.
2. **Runtime version declaration:** the delivery must pass the full live 1C version into
   `QA_MCP_PLATFORM_VERSION`/`PLATFORM_ROOT` so synthesized bootstrap and foreground frames declare the live
   platform version.
3. **Docker docs:** remove stale `/mcp/` examples while touching the delivery docs; use `/mcp`.
4. **E2E evidence:** retain one release-smoke transcript for 8.3 and one for 8.5 (thin model-B or host-platform
   model-A is acceptable if the evidence names the model). The proof is Agent/MCP HTTP -> attach/read, not a new
   protocol re-capture.
5. **Linux model-A dependency check:** if model-A is in scope for this card, rerun the `ldd` missing-library check
   against the supported 8.5 Linux binary and record the result.

## Acceptance
- Delivery docs and in-package notes match the epic-112 validate-first decision.
- The shipped/bootstrap path passes the live full platform version and documents supported builds
  (`8.3.27.2130`, `8.5.1.1343`) plus the "same family may work; validate first" policy.
- Retained E2E evidence exists for both an 8.3 and an 8.5 delivery run.
- If model-A Linux delivery is covered, the 8.5 `ldd` check records 0 missing libraries or an explicit runtime gap.

## Change Set
1. `reconcile-qa-mcp-8-3-8-5-release-evidence` —
   `openspec/changes/archive/2026-08-02-reconcile-qa-mcp-8-3-8-5-release-evidence/`

## Change 1: `reconcile-qa-mcp-8-3-8-5-release-evidence`

### Scope
- Inventory existing 8.3 and 8.5 protocol/runtime/release evidence and link the
  retained artifacts from this card.
- Remove or update stale docs that still imply `_bundled/8.5` must be populated
  before 8.5 can run.
- If the current release artifact still lacks 8.5 delivery evidence, run and
  retain exactly one release-smoke transcript that proves the shipped path passes
  the full live platform version and can attach/read through MCP.

### Acceptance
- The card either closes with links to existing 8.3 and 8.5 release-equivalent
  evidence, or it retains one new 8.5 release-smoke transcript for the current
  alpha artifact.
- No new 8.5 protocol implementation or recapture is performed unless the
  validate-first smoke goes red.

## Dependencies
- P0 (113) — version selection. P4 (117) — a validated 8.5 set. The Docker delivery from
  [[qa-mcp-public-delivery-prep]].

## Verify
- Planning gate: `openspec validate reconcile-qa-mcp-8-3-8-5-release-evidence --strict` and
  `openspec validate --all --strict` — passed (22 items) on 2026-08-01.
- Runtime gate (2026-08-02): current image
  `qa-mcp:card118-current` / `sha256:330509dc2114519d637ea2acc8a25e967d7b0b07c2c9ed15e68112ddba27aa2e`
  passed two release-equivalent Linux model-A runs over the canonical `/mcp`
  endpoint. Both `8.3.27.2130` and `8.5.1.1343` negotiated MCP `2025-11-25`
  with 68 tools, launched an owned TestClient, opened and read the
  `Справочник.Товары` form descriptor (67 elements; values not retained), and
  completed ownership-checked TestClient/Xvfb cleanup. The 8.5 run declared
  live version `8.5.1.1343` while resolving protocol data to family `8.3`.
- Dependency/cleanup gate: 8.5 `ldd` reported zero missing libraries; 8.3 used
  the existing autodetected system-libgcc launch profile and passed under that
  effective environment. Final TPorts and owned 1C/container processes were
  absent, and Apache was restored to `active` after the 8.3 file-infobase run.
- Documentation RED: `.venv/bin/pytest -q tests/test_multi_version_delivery_docs.py`
  initially failed 2 tests because two active URLs used `/mcp/` and
  `docker/README.md` omitted the 8.5 full-version/fallback contract.
- Focused GREEN: `.venv/bin/pytest -q tests/test_multi_version_delivery_docs.py
  tests/test_lifecycle.py tests/test_mcp_server.py
  tests/test_self_hosted_release_scripts.py` — 184 passed.
- Public surface: `python3 scripts/public-surface-scan.py` from the suite root
  `/opt/ai-dev-suite-for-1c` — passed (full). The component does not own a
  duplicate `qa-mcp/scripts/public-surface-scan.py` entrypoint.
- Contract gate: evidence JSON parsed with `jq`; OpenSpec status/instructions
  succeeded; strict change validation passed; full-tree strict validation
  passed 22/22; `git diff --check` passed.

## Next
- done

## Archive
- `openspec/changes/archive/2026-08-02-reconcile-qa-mcp-8-3-8-5-release-evidence/`

## Related
- `openspec/changes/archive/2026-08-02-reconcile-qa-mcp-8-3-8-5-release-evidence/`
- `docs/protocol-research/evidence/card118-multi-version-delivery-2026-08-02.md`
- `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/20260802T002132Z/`

## Result
- Delivered and verified; awaiting independent ChangeRail review. The current
  image passed release-equivalent 8.3/8.5 HTTP/MCP smokes, active guidance now
  matches the validate-first fallback contract, and the two release-path
  defects exposed by the first smoke have focused RED-to-GREEN coverage.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Log
- 2026-06-25 created under epic 112.
- 2026-07-06 board triage: epic 112/113/117 are done; 8.5 was validated on 8.3 protocol data with live-version
  injection. This card remains only if we want release-level 8.3/8.5 smoke evidence and stale-doc cleanup.
- 2026-07-07 real-base greenfield (.205, `8.3.27.2130`) drove the v0.3.0 release end-to-end on DemoSSL +
  [redacted third-party configuration] — that is 8.3 release-level evidence; the 8.5 side + stale-doc cleanup are still open. (No 8.5
  platform on .205.) Still backlog; low priority relative to the new `docs/qa-mcp-connection-issues-2.md`
  hardening wave under epic 111.
- 2026-08-01 alpha-release triage: confirmed this is not "implement 8.5"; moved
  to `2.todo` as a bounded evidence/docs reconciliation before release.
- 2026-08-01 ChangeRail fast-forward: created apply-ready proposal, design,
  `qa-mcp-self-hosted-release` delta spec and tasks; strict validation passed
  for the change and the full OpenSpec tree.
- 2026-08-02 delivery: audited retained Windows/Linux evidence, built and ran
  the current model-A image for both supported platform baselines, retained a
  sanitized curated report, fixed Streamable HTTP post-body receive forwarding
  and container ownership-root resolution, updated active docs, and passed the
  focused/public/OpenSpec verification gates.
- 2026-08-02T00:46:10Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
