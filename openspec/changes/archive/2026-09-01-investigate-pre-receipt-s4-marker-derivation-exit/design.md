## Context

The blocked S4-R1 candidate is a clean `77a4b389` composition of seven Go
paths. Its offline and exact S3 gates pass, but the first run-1 marker-
derivation row exits nonzero before `native-observation.json` exists. The
retained blocker contains only the row result and cleanup proof, so it cannot
distinguish runner/setup failure, candidate launch/exit, listener lifecycle,
window admission or passive UIA sampling.

The seven S4-R1 paths are protected inputs to this investigation. Although
their current test candidate can emit a bounded pre-receipt checkpoint file,
this card cannot edit or publish those bytes. The diagnostic therefore has to
compile from the published base and observe the composed S4-R1 candidate as an
external child.

This is not a protocol-capture or replay claim. There are no TestClient frame
ranges or dynamic protocol fields to normalize. The only live inputs are the
exact candidate, platform, infobase, run-1 EPF and marker selector hashes; raw
child output is hashed in memory and discarded.

## Goals / Non-Goals

**Goals:**
- Admit exactly one typed, bounded and privacy-safe classification when the
  live observer reaches an implemented emission branch: argv identity
  mismatch, child launch failure, or nonzero child exit with a missing or valid
  failed checkpoint.
- Map supported emitted rows to argv validation, child launch, listener
  readiness, process exit, desktop/window inventory, main admission or passive
  UIA sampling. Keep `diagnostic_setup` as a reserved validation enum with no
  live producer, not as an evidence claim.
- Abort harness precondition/setup, receipt freshness/allocation, timeout,
  checkpoint read/validation, unexpected zero-exit and unsafe-write failures
  fail-closed without admitting a positive or typed evidence row.
- Reproduce the same stage in two exact-contour passive runs or record a
  precise `NOT-VERIFIABLE` decision.
- Keep the test-only observer independently compilable from `77a4b389` and
  preserve every protected byte and cleanup invariant.

**Non-Goals:**
- Change, certify, archive, review or publish S4-R1 or S7.
- Add a public caller, wire field, production package, retry, sentinel success,
  visible-desktop proof or S5 action.
- Substitute host, principal, session, platform, infobase or fixture.
- Retain raw UI text, raw argv, screenshots, credentials or large platform
  logs.

## Decisions

1. Add only
   `host-agent/windows-display-agent/s4_r2_pre_receipt_diagnostic_test.go` and
   `host-agent/windows-display-agent/s4_r2_pre_receipt_diagnostic_windows_test.go`.
   The portable file owns the schema, strict validator, checkpoint mapping and
   hostile tests. The Windows file owns one explicitly env-gated live test that
   launches an external S4-R1 candidate. Both are Go test files, so they add no
   production caller or binary surface.
2. Build the diagnostic test binary from a temporary clean export of
   `77a4b389` plus only these two new files. Pass the already composed S4-R1
   candidate as an absolute, hash-bound external input. This proves that the
   committed diagnostic does not depend on or absorb the seven protected
   source paths.
3. Validate inputs before launch without serializing raw argv. An exact
   candidate/platform/fixture identity mismatch can emit `argv_validation`;
   other harness precondition/setup or receipt-allocation/freshness failures
   abort with `t.Fatal` and do not produce an admitted diagnostic. A retained
   status contains schema, stage, outcome, candidate/platform/target/fixture/
   argv hashes, bounded exit code and booleans for listener/action/raw-UI state.
   It cannot contain paths, UI strings, environment values or child output.
4. Map the external candidate's strict pre-receipt checkpoint schema into the
   investigation stages. `controller_transfer` or a later checkpoint proves
   listener readiness; inventory/main/UIA checkpoints retain their narrower
   stage. A missing checkpoint after nonzero child exit emits
   `process_exit/candidate_exited_without_checkpoint`. A malformed or
   in-progress checkpoint, checkpoint read error, bounded timeout, unexpected
   zero exit or unsafe diagnostic write aborts fail-closed and is not an
   admitted evidence row. Process start failure can emit `child_launch`; no
   abort can be reinterpreted as success.
5. Run exact S3 once before the investigation rows. Run the test-only observer
   twice with the same candidate, fixture hashes and argv. Do not retry a row
   for acceptance and do not proceed to fixed-marker or S5 actions. Agreement
   means identical typed stage and outcome, not merely two nonzero exits.
6. Preserve exact Windows configuration bytes, ACL and file metadata. Remove
   only the current-run task/stage/PIDs/job/desktop/TPort artifacts, then prove
   unrelated task and boot fingerprints are unchanged. Retain only sanitized
   receipts and a curated decision report.

## Risks / Trade-offs

- [The external observer sees only the last atomic checkpoint] -> Treat it as a
  lower-bound stage, retain process exit separately and avoid stronger causal
  claims than the checkpoint proves.
- [Diagnostic timing perturbs the failure] -> The observer polls only a file
  owned by the child and waits passively; require two agreeing one-shot rows.
- [The protected candidate cannot emit a valid checkpoint] -> Publish
  `NOT-VERIFIABLE` with the exact missing boundary rather than editing S4-R1.
- [Dirty S4-R1/S7/OSS-07 bytes enter publish scope] -> Bind protected per-path
  hashes, maintain an explicit manifest and stage only new diagnostic,
  evidence/docs, OpenSpec and the three intended planning paths.
- [A status leaks paths or UI] -> Validate a closed JSON schema, scan retained
  evidence for forbidden fields/patterns and retain only hashes/counts/enums.

## Migration Plan

1. Bind the published base, protected tracked/untracked scope and exact fixture
   hashes; create the new-path-only test diagnostic with RED/GREEN validator,
   checkpoint-classifier and privacy tests. These direct tests do not claim to
   execute every Windows live-emission branch.
2. Prove clean-base focused/full Go tests, vet and Windows amd64/386 test and
   host cross-builds, then prove the separate seven-path candidate composition.
3. Run authorized host/principal/session/platform/target/config preflight, the
   real S3 control and exactly two passive run-1 diagnostic rows.
4. Restore and prove exact-owned cleanup, compare the typed rows and publish a
   bounded resume/runbook/environment decision or `NOT-VERIFIABLE`.
5. Sync/archive the investigation capability, run strict/scope/privacy checks
   and request a fresh ordinary-risk review.

Rollback removes the two new `_test.go` files and curated investigation
evidence/docs. It does not alter the protected candidate or external target.

## 1C Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason | Residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery/runtime apply | Passive external observation of the exact S4-R1 test candidate on `HISTORICAL-LAB-HOST\\historical-user`, interactive Session 1, platform `8.3.27.2214`, `C:\\1C_BASES\\vanessa_client` | Exact identity/config preflight, one S3 control, two one-shot S4-R2 diagnostic rows and exact-owned cleanup | `scenario_log` and `cleanup_evidence` containing only hashes, enums, bounded counts/exit codes and preservation booleans | `.runtime/changerail/evidence/oss-06-s4-r2-investigate-pre-receipt-marker-derivation-exit/` | planned | N/A | Last-checkpoint evidence may bound rather than uniquely prove the platform fault; decision must preserve that uncertainty | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Managed form layout | Read-only run-1 marker observation; no form source or layout edit | No visual mutation or screenshot; marker/UI values remain hash-only | N/A | N/A | N/A | This card changes no managed form and forbids raw UI retention | Marker value remains uncertified unless the protected candidate reaches passive UIA | `/opt/ai-dev-suite-for-1c/qa-mcp` |

## Open Questions

- The exact failure stage is intentionally unresolved until the two authorized
  passive rows complete; it is an investigation output, not a planning
  assumption.
