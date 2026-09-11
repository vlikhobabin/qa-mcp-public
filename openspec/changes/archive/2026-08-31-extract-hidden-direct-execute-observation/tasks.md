## 1. RED Observation Oracles

- [x] 1.1 Add portable hostile tests for missing/duplicate marker, malformed
  expected hash, foreign PID/job/desktop/window, changed exact main HWND and
  ambiguous/changed UIA topology; assert action count remains zero.
- [x] 1.2 Add receipt/privacy tests rejecting raw marker/UI text,
  credential-like or connection fields, non-hash structural strings, geometry,
  screenshots and non-zero action count.
- [x] 1.3 Retain the literal focused RED command, observed failures and a
  test-to-prior-unsafe-behavior mapping before adding production S4 source.

## 2. Dormant Passive Primitive

- [x] 2.1 Implement portable exact main-window re-admission, canonical marker
  hash/cardinality, bounded structural-row validation, deterministic topology
  hashing and typed sanitized receipt in a separate S4 file.
- [x] 2.2 Implement a Windows-only passive UIA adapter that returns at most
  `512` exact-PID hashed structural rows and never returns raw values or obtains
  an action pattern for invocation.
- [x] 2.3 Require two exact-main snapshots with identical marker cardinality
  and topology; keep action count zero, production additions `<=300`, S1-S3
  byte-identical and all S4 functions caller-free outside tests.

## 3. Offline And Clean-Composition Verification

- [x] 3.1 Run the exact focused S4 tests, full `go test ./...`, `go vet ./...`,
  Windows test executable cross-build and Windows host-agent cross-build.
- [x] 3.2 Reconstruct published `46287c...:host-agent` in a fresh module-aware
  directory, overlay only exact S4 source/test paths and repeat focused/full/
  vet/cross-build gates with deterministic candidate hashes.
- [x] 3.3 Run production LOC, published S1-S3 byte-identity, dormant-caller,
  forbidden-action and public/wire/Python scope scans plus `git diff --check`.

## 4. Exact Windows Passive Proof

- [x] 4.1 Inventory trusted `HISTORICAL-LAB-HOST\\historical-user`, exact platform
  `8.3.27.2214`, declared `C:\\1C_BASES\\vanessa_client`, listener `18081`,
  Docker and exact current-run task/stage state without exposing ignored
  credentials, UI text or connection strings.
- [x] 4.2 Run the exact-source direct-`/Execute` candidate and retain only two
  stable passive main/marker/topology snapshots, zero-action counters and
  source/candidate hashes; do not confirm a prompt or use visible desktop.
- [x] 4.3 Before cleanup verify exact task/action/path/hash/PID/job/desktop/port
  ownership, remove only current-run resources and retain bounded before/after
  proof that listener `18081`, unrelated processes and Docker are preserved and
  no reboot occurred.

## 5. Delivery Handoff

- [x] 5.1 Create an ignored S4 evidence index containing RED/GREEN/final,
  clean-composition, native-observation and cleanup receipts with no raw logs,
  screenshots, UI text, credentials or connection strings.
- [x] 5.2 Sync `qa-mcp-hidden-direct-execute-observation`, archive the change
  and update only the S4 card/manifest while keeping the roadmap snapshot,
  dirty combined candidate, `.codex/config.toml` and S5-S7 excluded.
- [x] 5.3 Run strict all-OpenSpec, manifest working-tree scope-check and final
  verification, then prepare deterministic preflight for exactly one fresh
  ordinary/high independent review before scoped publication.

## 6. Bounded Review Rescue 1

- [x] 6.1 Retain review-cycle-1 `NO-GO` and a focused RED proving a changed or
  reused second main identity must prevent the passive observer from running.
- [x] 6.2 Re-admit the exact second window identity before the second UIA
  traversal and prove the observer callback remains uncalled on rejection.
- [x] 6.3 Rerun focused/full Go, vet, clean composition, mutation/static gates,
  strict OpenSpec and exact-source Windows observation plus exact cleanup before
  preparing fresh review cycle 2.
