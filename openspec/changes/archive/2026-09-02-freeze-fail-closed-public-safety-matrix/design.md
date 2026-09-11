## Context

OSS-07-I1 ended at cycle 3 with one `R1` false-PASS blocker after same-card
rescue budget `2/2` was exhausted. The unavailable predecessor payload checked
`P`/`S` ranges rather than exact row meanings, did not assert the exact RED
tuple `46/14/5/D14`, accepted `D12` string presence as execution, did not prove
that original eligible-email bytes reached every non-email rule, and did not
bind `audit_design.py` bytes. Acceptance 1, 2 and 4 failed; 3, 5 and 6 passed.
Cycle-2 R2/R3 are closed and R1 is only partially closed.

This clean workspace contains only the safe published reference `10598ef`, not
the I1 nine-path dirty payload or runtime review files. The card therefore binds
the supplied verdict/history SHA-256 digests and concise findings without
inventing a predecessor path. I2 is a small offline design/investigation under
the approved `Apache-2.0` policy constraint. It cannot implement the wider
OSS-07 story or start OSS-08.

## Goals / Non-Goals

**Goals:**

- Author one minimal successor-owned matrix whose exact ordered row identities,
  semantic `P`/`S` labels and expected results are independently frozen.
- Make byte changes to the matrix or helper, semantic-label/result changes,
  `D12` bypass, and `G18` original-byte diversion observable as verification
  failures.
- Retain an explicit, stable structured-context allowlist and exact offline
  verification/fresh-review floor.
- Close only the carried R1 design invariant from a clean published baseline.

**Non-Goals:**

- Restore, copy, reconstruct or publish the predecessor's nine tracked paths.
- Change `src/`, `tests/`, `host-agent/`, Docker/runtime/provider code, existing
  release behavior, OSS-07 parent/roadmap prose, or OSS-08.
- Create `LICENSE`, `NOTICE`, governance, security, contribution or release
  files; `Apache-2.0` is inherited policy input only.
- Run Windows, SSH, 1C, TestClient, Vanessa, live MCP, Apache service, network,
  capture, replay or external-side-effect work.
- Claim that I1 evidence was copied or that I1 is publishable.

## Decisions

### 1. Use a clean-room five-file delivery surface

Delivery is limited to these new successor-owned files in addition to this
card and its active OpenSpec artifacts:

- `docs/protocol-research/evidence/oss-07-i2-fail-closed-public-safety-matrix-2026-09-02/findings.md`
- `docs/protocol-research/evidence/oss-07-i2-fail-closed-public-safety-matrix-2026-09-02/matrix.json`
- `docs/protocol-research/evidence/oss-07-i2-fail-closed-public-safety-matrix-2026-09-02/freeze.json`
- `tools/protocol-research/oss07_i2/audit_design.py`
- `tools/protocol-research/oss07_i2/verify_matrix.py`

The evidence directory is a small curated report, while executable research
helpers remain under `tools/protocol-research/` as required by repository
ownership. No I1 file is an implementation input. The helper is clean-room and
successor-specific even though its basename preserves the reviewed
`audit_design.py` subject.

Alternative considered: recover the I1 payload and patch its wrapper. Rejected
because the payload is unavailable here, its rescue budget is exhausted and
the linked-card policy requires a separate independently reviewable scope.

### 2. Make the outer verifier the independent trust root

`matrix.json` uses deterministic UTF-8 without BOM, LF line endings and one
canonical serialization. Every row has a unique stable ID, fixed order, exact
semantic label (`P` or `S`) and exact expected result. The complete table is
duplicated as immutable constants in `verify_matrix.py`; the verifier rejects
missing, extra, duplicate, reordered or semantically changed rows rather than
accepting ranges or sets. It also contains the literal ordered RED tuple
`[46, 14, 5, "D14"]` and compares it to actual structured results.

`freeze.json` records schema ID, `Apache-2.0` policy input, exact relative
paths, byte sizes and lowercase SHA-256 digests for `matrix.json` and
`audit_design.py`. After those two files and the freeze record stabilize,
`verify_matrix.py` embeds the exact SHA-256 of the freeze-record bytes. This is
not circular: the freeze does not hash the outer verifier. The verifier checks
semantic contents and then exact bytes before it may trust helper output.
Fresh independent critical review and the ChangeRail payload fingerprint bind
the outer verifier itself.

Alternative considered: let the helper read expected labels/results from the
same matrix it executes. Rejected because a coordinated wrong label or output
could then validate itself, reproducing R1.

### 3. Require observed control/data-flow receipts

The outer verifier invokes the hash-approved helper with a per-run nonce and an
exact structured context. `D12` success requires a structured receipt emitted
only by the row-execution callback and containing the nonce, row ID and input
digest. Parsing the helper source or finding the text `D12` is never evidence.

The canonical eligible-email fixture is the non-personal reserved-domain byte
string `eligible@example.invalid`. `matrix.json` records its exact hex, length
and SHA-256. Before evaluating each canonical non-email rule, the helper emits
a receipt with rule ID, nonce, byte length and digest of the actual input bytes.
The verifier requires the exact non-email-rule ID set once each, and every
receipt must match the original bytes. Decoding/re-encoding, normalization,
replacement, truncation, omission or post-rule receipts fail.

Alternative considered: accept source markers, aggregate counts or one G18
receipt. Rejected because none proves execution or per-rule original-byte flow.

### 4. Keep mutation evidence inside the successor verifier, not test source

`verify_matrix.py --run-mutations` creates an owned temporary directory and
runs one mutation at a time against copied inputs while its trusted constants
remain unchanged. The required cases are:

1. change a row's `P`/`S` label;
2. change each member of `46/14/5/D14` independently;
3. bypass `D12` while leaving its marker text present;
4. normalize/replace the G18 eligible bytes before one non-email rule;
5. omit one G18 non-email-rule receipt;
6. alter one byte of `audit_design.py`;
7. add, remove, duplicate or reorder a row;
8. provide each invalid structured-context case.

Each hostile case must produce a named non-zero fail-closed outcome; the exact
unmodified control must pass. The report lists mutation ID, expected failure
class and observed failure class without copying sensitive input or runtime
logs. This is executable design evidence, not a new pytest/unit-test surface.

### 5. Freeze the structured-context allowlist

The only accepted context keys are `schema`, `run_nonce`, `matrix_sha256`,
`helper_sha256` and `eligible_email_sha256`. Values have fixed primitive types
and exact formats; booleans are not integers, digests are lowercase 64-hex and
the nonce is non-empty but affects receipts only. Missing, extra, duplicate,
mistyped or prose-derived values fail before row selection or helper execution.
The helper cannot receive paths, commands, environment variables, credentials,
user data or expected-result overrides through context.

Alternative considered: forward arbitrary review context. Rejected because it
would make row selection and expected values mutable outside the frozen oracle.

### 6. Preserve the inherited verification and review floor

Delivery must retain command-bound evidence for:

- the pristine control and all hostile mutations through the exact successor
  verifier;
- JSON parsing, Python compilation and exact scope/path allowlist;
- absence of secrets, personal/customer values and non-`Apache-2.0` licensing
  choices in the five-file surface;
- strict validation of this change and all OpenSpec content;
- whitespace checks covering tracked diffs and new untracked files without
  staging;
- a fresh independent ChangeRail review at `critical` risk against the exact
  delivery fingerprint.

I1's negative verdict/history digests prove lineage only. They are not positive
evidence and cannot satisfy I2 review freshness.

## Capture, Replay And Cleanup

There are no capture sources or frame ranges. The only dynamic value is an
ephemeral run nonce, which changes no expected row or result. There is no replay
strategy because I2 uses only synthetic offline bytes. The verifier owns one
temporary directory, removes only that directory on success or failure, and
records no PID, service, credential, raw capture or external runtime output.

## Risks / Trade-offs

- [Risk] The outer verifier duplicates the canonical row table and can drift.
  -> Mitigation: exact table comparison, freeze-record digest, mutation cases
  and fresh critical review bind both copies as one reviewed payload.
- [Risk] A hash proves identity but not semantic correctness.
  -> Mitigation: the independent exact row/result oracle and observed D12/G18
  receipts run before a control is accepted.
- [Risk] The synthetic eligible-email bytes do not represent all email forms.
  -> Mitigation: I2 claims only byte-preserving flow for one exact safe fixture,
  not general email validation correctness.
- [Risk] A five-file bundle adds a verifier outside pytest.
  -> Mitigation: it is a bounded offline investigation surface with explicit
  commands, hostile controls, exact output and independent review.

## Migration Plan

1. Author the clean-room matrix and helper from this specification only.
2. Compute their byte sizes/digests, write the freeze record, then bind its
   exact digest and canonical row/result table in the outer verifier.
3. Run the unchanged control and every required hostile mutation offline.
4. Write the concise findings report with exact hashes and outcomes.
5. Run the inherited floor and obtain a fresh critical review before archive
   or publication.

Rollback removes only the five new successor-owned files and this card-owned
change; the safe `10598ef` baseline has no I1 payload to undo.

## Open Questions

- none. Any need to restore I1 paths, change production/tests, use live or
  Windows infrastructure, broaden licensing/governance work or touch OSS-08 is
  a new card and a fail-closed stop for I2.
