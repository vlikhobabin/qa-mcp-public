# Enforce Target-Bound Evidence And Cleanup

## Status
4.done

## Owner
qa-mcp

## Series
oss-04f

## Order Index
4036

## OpenSpec Stage
archived / reviewed / published

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Live admission: `yes`
- Final certification: `yes`
- Published investigation authorization: `none`

## Parent Epic
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Goal
Close project-mode tool schemas, representative read/display routing, evidence
provenance and exact-owned local/Windows cleanup, then certify the complete
OSS-04 behavior with retained native runtime proof.

## Acceptance
- Model input cannot supply physical target, endpoint, credential, rebind or
  evidence-retention controls in project mode.
- Representative read and display operations route through the common executor
  with the admitted target/session and bounded artifact provenance.
- Cleanup signals only exact lifecycle-owned resources; non-owned attachment is
  detached and stale/foreign handles are refused.
- Linux and Windows native evidence proves lifecycle/read/display/cleanup plus
  negative no-alternate-target behavior and unrelated-resource preservation.
- The final source file hashes reconcile with the preserved full payload and
  retained runtime summaries.
- The payload stays at or below `300` added production LOC.

## Change Set
1. `enforce-qa-mcp-target-evidence-cleanup` -
   `openspec/changes/enforce-qa-mcp-target-evidence-cleanup/`

## Dependencies
- [OSS-04E-R1](../4.done/oss-04e-r1-replace-exhausted-lifecycle-admission.md)
  is reviewed and published at baseline
  `83d88eba4cd608e6141f2ac3def269cb813b502c`.
- The unpublished exhausted OSS-04E payload and its stash are evidence lineage
  only and MUST NOT be restored.

## Verify
- Project-bound schema, executor read/display, evidence-policy and exact cleanup
  tests for local and Windows adapters.
- Test-first hostile cases for schema retargeting, stale/foreign/recycled
  handles, non-owned detach, relay/native-port separation and alternate-target
  side-effect spies.
- Audit prior evidence only as lineage, then run fresh exact-final-source Linux
  and authorized Windows lifecycle/read/display/cleanup proof; old oversized
  source is not a substitute for current proof.
- Focused core/MCP/scenario/lifecycle/display suite, exact non-live CI command,
  coverage, compilation, host-agent Go tests, strict OpenSpec, diff check,
  production LOC gate `<=300` and independent critical review.

## Result
Implementation and exact-source Linux plus exact-wheel Windows certification
are complete. The authorized Windows proof used
`HISTORICAL-LAB-HOST\\historical-user` at `192.0.2.204`, platform `8.3.27.2130` and exact
target `C:\\1C_BASES\\vanessa_client`; the earlier `.203` discovery is
classified as an unrelated host and is not acceptance evidence. Sanitized
evidence proves bound lifecycle/read/display routing, exhaustive `63`-tool
authority refusal, exact-owned cleanup and unchanged unrelated Docker/1C state.
All `14/14` delivery tasks are complete, the capability spec is synced and the
change is archived at
`openspec/changes/archive/2026-08-27-enforce-qa-mcp-target-evidence-cleanup/`.
Review rescue 1 closed the cycle-1 endpoint/credential/schema-oracle findings;
final `mcp_server.py` SHA-256 is
`4074600d3d82e2e6b2911c8db76504bcdd42fdd831d918e31df7e95a5235aa83`
and final wheel SHA-256 is
`99a78a3394f555d354db1c2aca4e0ea91ed1ce295a51a124bdfeeae2143203dc`.

## Next
- Parent OSS-04 and the immutable runtime-target milestone are closed.
- OSS-06 is planning-ready because OSS-04 is complete and OSS-05 is
  apply-ready. Start no further card without a separate operator command.

## Change 1: `enforce-qa-mcp-target-evidence-cleanup`

### Why
The published lifecycle admission is fail-closed, but project-mode schemas,
representative display evidence and exact-owned teardown remain open surfaces.

### Goal
Close those surfaces without exposing physical target authority and certify the
complete OSS-04 chain against the exact final Linux and Windows source.

### Scope
- Bound schemas and provider-owned hidden arguments.
- Representative read/display executor routing with bounded provenance.
- Exact-owned local/Windows cleanup, non-owned detach and hostile refusal.
- Sanitized exact-source native proof; no OSS-05/OSS-06 implementation.

### Acceptance
- Every card criterion and capability requirement passes.
- Added production LOC remains at or below `300`.
- The change syncs, archives and receives a fresh critical `GO` review.

### Depends On
- Published OSS-04E-R1 commit
  `83d88eba4cd608e6141f2ac3def269cb813b502c`.

### Related
- `openspec/changes/enforce-qa-mcp-target-evidence-cleanup/`

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload F.
- 2026-08-27 fast-forward refreshed against published OSS-04E-R1: exhausted
  payload restoration is forbidden, current exact-source native reruns are
  mandatory, and critical live/final-certification review is explicit.
- 2026-08-27 moved to `3.inprogress`; test-first delivery started from
  published `83d88eb` without restoring any exhausted stash.
- 2026-08-27 implementation reached `273` added production LOC after the
  bounded review rescue; final focused compatibility passed `892` tests and
  hostile cleanup/evidence coverage passed `20` tests.
- 2026-08-27 exact-source Linux target-bound lifecycle/read/display/cleanup
  passed with raw screenshot removal, owned PID cleanup and Apache restoration.
- 2026-08-27 pre-review exact CI passed `1587` tests at `74.66%` coverage;
  host-agent Go, compilation, diff check and strict OpenSpec (`38/38`) passed.
- 2026-08-27 corrected the endpoint: `.203` was an unrelated discovery host.
  Authorized `.204` preflight confirmed `HISTORICAL-LAB-HOST\\historical-user`, platform
  `8.3.27.2130` and exact `C:\\1C_BASES\\vanessa_client` target.
- 2026-08-27 initial Windows certification exposed two bounded public-boundary defects:
  remote owned attachments lacked the provider display sentinel and discarded
  validated `client_target` lifecycle identity. Both were fixed with regression
  coverage; the first rescue-era hostile suite passed `19` tests.
- 2026-08-27 exact final wheel Windows lifecycle/read/display/hostile/cleanup
  proof passed. Retained summaries are indexed under
  `.runtime/changerail/evidence/oss-04f-enforce-target-evidence-cleanup/`; raw
  screenshots, UI text, credentials, tokens and transient run-owned resources
  were removed or remain ignored.
- 2026-08-27 review cycle 1 returned `NO-GO`: project mode still exposed
  `base_url`, nested role credentials and `out_dir`; the unit/native oracle
  audited only a representative subset, and archived task 4.2 claimed future
  publication work complete.
- 2026-08-27 bounded rescue 1 provider-bound endpoint/output roots, removed the
  credential matrix from project mode, preserved unbound schemas and added a
  recursive authority audit across all `63` project tools. Exact-source Linux
  and exact-wheel `.204` Windows native proofs were rerun successfully.
- 2026-08-27 rescue verification passed hostile `20`, focused `892`, exact
  non-live CI `1587` at `74.66%`, compilation, Go tests, strict OpenSpec
  `38/38`, evidence-index validation, diff check and production LOC
  `273 <= 300`.
- 2026-08-27 synced `qa-mcp-target-bound-evidence-cleanup` into main specs and
  archived the completed `14/14` change; the card remains in `3.inprogress`
  pending the independent review and publish gate.
- 2026-08-27 fresh independent critical `xhigh` review cycle 2 returned `GO`
  with `9/9` acceptance, zero findings and zero unbacked claims. The exact
  pre-publish CI rerun passed `1587` tests at `74.66%` coverage.
- 2026-08-27 published to `4.done`; parent OSS-04 was closed, immutable
  runtime-target binding was marked complete and OSS-06 became planning-ready.
