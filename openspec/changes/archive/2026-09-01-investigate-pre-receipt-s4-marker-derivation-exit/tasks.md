## 1. Protected Baseline And RED Contract

- [x] 1.1 Record the exact `77a4b389` base, classify the three intended
  planning inputs and bind every protected tracked/untracked S4-R1, S7,
  fixture and OSS-07 path before deriving the delivery manifest.
- [x] 1.2 Add RED/direct tests in the new portable `_test.go` path for valid
  checkpoint-to-stage mapping, the missing-checkpoint process-exit mapping,
  invalid stage/outcome pairings, malformed hashes, invalid/in-progress
  checkpoints, nonzero actions, raw-UI retention and forbidden serialized
  fields. These portable tests do not exercise every Windows live-emission
  branch and do not prove a `diagnostic_setup` producer.
- [x] 1.3 Prove the RED test observes the intended validator/classifier boundary
  and fails before the implementation exists.

## 2. Independently Publishable Test Diagnostic

- [x] 2.1 Implement the strict bounded diagnostic schema, validation,
  checkpoint mapping and privacy-safe serialization in the new portable Go
  test path only.
- [x] 2.2 Implement the env-gated Windows test observer in the new Windows Go
  test path; validate/hash exact inputs, launch the S4-R1 candidate once as an
  external child, hash/discard raw output and retain one sanitized receipt only
  when an implemented argv-identity, child-launch or nonzero-exit/checkpoint
  emission branch completes. Harness setup, freshness/allocation, timeout,
  checkpoint-read/validation, unexpected-zero-exit and unsafe-write failures
  abort fail-closed and are not admitted evidence rows.
- [x] 2.3 Prove zero production callers, no action/retry/sentinel success and a
  clean `77a4b389` export plus only the two new test paths passes focused/full
  Go tests, vet and Windows amd64/386 test and host cross-builds.
- [x] 2.4 Prove the separate clean-base-plus-seven-S4-R1-path composition still
  passes its focused/full Go tests, vet and Windows amd64/386 test and host
  cross-builds without changing any protected byte.

## 3. Exact Windows Passive Classification

- [x] 3.1 Preflight only `historical-user@192.0.2.201` as
  `HISTORICAL-LAB-HOST\\historical-user` in interactive Session 1 with exact platform,
  infobase, candidate/run-1/run-2/config/ACL hashes, free owned runtime state
  and preserved unrelated task/boot fingerprints.
- [x] 3.2 Run one exact S3 control and retain its sanitized positive lifecycle
  and cleanup receipt before admitting S4 diagnostics.
- [x] 3.3 Run exactly two one-shot passive run-1 diagnostics with identical
  candidate, fixture hashes and argv identity; retain matching typed failure
  stages or record the precise disagreement as `NOT-VERIFIABLE` and do not run
  fixed-marker, S5 or visible-desktop proof.
- [x] 3.4 After every row restore configuration bytes/ACL/metadata and remove
  only exact-owned task, stage, PID/job/desktop/TPort state; prove zero owned
  residue and unchanged unrelated fingerprints.

## 4. Decision, Evidence And Review Handoff

- [x] 4.1 Publish one curated privacy-safe decision report and evidence index:
  runbook/environment correction, bounded S4-R1 resume hypothesis with a
  concrete verification target, or `NOT-VERIFIABLE` with an exact resume
  condition; retain no raw UI, screenshots, credentials or large logs.
- [x] 4.2 Recheck protected per-path identities, scan committed/ignored evidence
  for privacy violations and update the card, roadmap and OSS-06 parent without
  resuming S4-R1, S7, OSS-07 or OSS-08.
- [x] 4.3 Run focused/full clean-base and seven-path composition floors, Go vet,
  Windows cross-builds, strict change/all OpenSpec, manifest working-tree scope,
  tracked/untracked whitespace and `git diff --check` with named outcomes.
- [x] 4.4 Sync/archive the exact investigation capability and leave the card in
  `3.inprogress` for a genuinely fresh ordinary-risk independent review.

## Completion Evidence

- The clean `77a4b389` export plus only the two S4-R2 test files passed focused
  and full Go tests, `go vet`, Windows amd64/386 test compilation and Windows
  amd64/386 host cross-builds. A retry-validation mutation produced the
  expected hostile-test RED failure before the unchanged implementation passed.
- The separate clean `77a4b389` plus the seven protected S4-R1 Go paths passed
  full Go tests, `go vet`, Windows amd64/386 test compilation and host
  cross-builds without modifying a protected byte.
- The operator-approved immutable receipt at
  `.runtime/changerail/evidence/oss-06-s4-r2-investigate-pre-receipt-marker-derivation-exit/fresh-matrix.json`
  records exact S3 success, two agreeing
  `process_exit/candidate_exited_without_checkpoint` rows, action/retry counts
  zero and exact cleanup. It proves no other live emitting branch. Setup,
  timeout and checkpoint harness aborts remain non-evidence and cannot produce
  or admit a positive row. No live command ran during either resume session.
- The curated decision is
  `docs/protocol-research/evidence/pre-receipt-marker-derivation-exit-2026-09-01/findings.md`.
