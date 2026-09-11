## 1. RED Identity And Isolation Oracles

- [x] 1.1 Add portable RED tests for missing, duplicate, foreign-PID,
  outside-job, wrong-class, wrong-owner, wrong-desktop and owned-`Default`
  candidates, recording the exact focused command and prior unsafe behavior.
- [x] 1.2 Add RED receipt tests proving JSON contains only bounded
  hashes/counts/booleans and source guards reject global-input, foreground,
  desktop-switch, addressed-message and UIA action primitives.
- [x] 1.3 Add buildable Windows-native RED helpers for one synthetic hidden
  root/owned-popup lifecycle and one exact-platform real-TestClient lifecycle;
  do not run UIA, marker, chooser or prompt actions.

## 2. Dormant Window Isolation Primitive

- [x] 2.1 Implement the portable bounded identity, exact predicate/admission
  and sanitized receipt in `hidden_desktop_window_isolation.go`.
- [x] 2.2 Implement read-only exact desktop open/enumeration, PID/class/owner
  extraction and S2 job-membership classification in
  `hidden_desktop_window_isolation_windows.go`.
- [x] 2.3 Keep the two production files at no more than `300` physical lines,
  add zero non-test callers and leave published S1/S2 source byte-identical.

## 3. Offline And Clean-Composition Verification

- [x] 3.1 Run exact focused `TestHiddenWindowIsolation` tests, full
  `go test ./...`, `go vet ./...`, Windows `go test -trimpath -c` and host
  `go build -trimpath`; retain exact commands and bounded outcomes.
- [x] 3.2 Reconstruct `HEAD:host-agent` in a fresh module-aware directory,
  overlay only the exact four S3 paths, rerun all gates twice and prove stable
  candidate hashes.
- [x] 3.3 Run forbidden-input/source-call scan, production LOC gate and
  dormant-caller scan; fail on any S4-S7/public-route dependency.

## 4. Exact Windows Native Proof

- [x] 4.1 Inventory trusted `HISTORICAL-LAB-HOST\\historical-user`, exact platform
  `8.3.27.2214`, declared `C:\\1C_BASES\\vanessa_client`, listener `18081`,
  exact S3 task/stage and Docker state before mutation without exposing ignored
  credentials or UI content.
- [x] 4.2 Run one exact interactive ScheduledTask candidate selecting the
  synthetic owner-topology and real-TestClient isolation cases; retain only
  per-case verdicts, counts, class hashes, zero-input flags and candidate/source
  hashes in `windows-native.json`.
- [x] 4.3 Before destructive cleanup, verify exact task/action/path/hash/PID/
  port ownership; remove only current-run resources and retain before/after
  `windows-cleanup.json` proving owned/1C processes zero, listener `18081`
  preserved, no Docker mutation and no reboot.

## 5. Delivery Handoff

- [x] 5.1 Create `.runtime/changerail/evidence/oss-06-s3-extract-hidden-window-isolation/`
  with RED/GREEN/final summaries, deterministic clean-composition command,
  native/cleanup receipts and an indexed sanitized candidate lineage.
- [x] 5.2 Sync `qa-mcp-hidden-window-isolation`, archive the change and update
  the S3 card/manifest without touching S4-S7 or unrelated dirty payload.
- [x] 5.3 Run strict change/all OpenSpec validation, manifest working-tree
  scope-check, `git diff --check` and deterministic review preflight; obtain one
  fresh ordinary/high independent `GO` before scoped publication.
