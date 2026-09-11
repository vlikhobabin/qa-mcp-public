# Pre-receipt marker-derivation exit investigation

## Decision

The completed S4-R2 receipt is accepted as immutable, unchanged-payload
evidence. The foreground supervisor timeout recorded in `fresh-blocker.json`
was a delivery-process stop after the task had completed; it is not a runtime
classification and does not authorize or require another live run.

The evidence supports one bounded S4-R1 resume hypothesis: the protected
candidate exits before its first atomic pre-receipt checkpoint and before
listener readiness, so the next separately authorized S4-R1 continuation must
target candidate startup and first-checkpoint creation rather than marker
derivation. It does not establish a root cause and does not admit S4, S5, S7,
OSS-07 or OSS-08 work.

## Evidence binding

- Approved receipt:
  `.runtime/changerail/evidence/oss-06-s4-r2-investigate-pre-receipt-marker-derivation-exit/fresh-matrix.json`
  at SHA-256
  `5ecfaecd630286370dbbe63361144ed6ab31bd65b303e98a939dd8fa6877632a`.
- Historical process stop:
  `.runtime/changerail/evidence/oss-06-s4-r2-investigate-pre-receipt-marker-derivation-exit/fresh-blocker.json`
  at SHA-256
  `53697b4b39aa36c5b571d47c1821cd8930c823e3442ff3088cba3b338a035c95`.
- Portable test observer SHA-256:
  `9a98c4763dcc832350394d177c2adec6aa7148b12de242eea2798c35a79dc1cb`.
- Windows test observer SHA-256:
  `5778b56b8a8e4ac02504f19963e4213636dcb3f366a30a039e09f10ea485acc9`.

The approved receipt binds an exact host and principal, interactive session
`1`, the candidate, observer, platform, run-1 fixture, configuration content,
ACL and metadata baseline by hash. It retains no endpoint, path, raw argv, UI
text, screenshot, credential or child output.

## Observed boundary

1. The exact S3 control passed with action count zero and complete cleanup.
2. Both one-shot S4-R2 rows produced the same closed classification:
   `process_exit/candidate_exited_without_checkpoint`, exit code `1`.
3. Neither row reached listener readiness or produced a positive checkpoint.
   Action and retry counts remained zero.
4. Every row restored configuration content, ACL, creation time, last-write
   time, last-access time and attributes exactly. Owned task, stage and 1C
   process counts were zero afterward, while unrelated task and boot identity
   remained exact.

The agreement proves only that the candidate exits before the first retained
checkpoint. It cannot distinguish test initialization, candidate startup or
the earliest controller setup without a later card-owned observation.

## Diagnostic boundary

The immutable code has live producers only for an exact-identity mismatch
(`argv_validation`), child launch failure, nonzero exit without a checkpoint,
and nonzero exit with a valid failed checkpoint mapped into the later closed
stages. `diagnostic_setup` has no live producer. Harness precondition/setup,
receipt freshness/allocation, timeout, checkpoint-read or validation,
unexpected-zero-exit and unsafe-write failures abort via the test harness and
are not admitted diagnostic rows. Existing portable direct tests cover the
validator, checkpoint mapping, missing-checkpoint process-exit mapping and
privacy surface; they do not prove every Windows live-emission branch.

The approved receipt exercised only
`process_exit/candidate_exited_without_checkpoint`. No other live producer is
claimed as proven, and a harness abort cannot create or admit a positive row.

## Resume target

S4-R1 remains stopped. A separate operator-authorized continuation may proceed
only against its protected payload and must first retain a valid allowlisted
`controller_start` checkpoint or a later checkpoint from the same exact
composition, with zero action/retry, privacy-safe output and exact cleanup. A
missing checkpoint or another exit remains fail-closed and cannot count as S4
marker admission. S7 remains blocked until S4-R1 independently completes,
reviews and publishes.
