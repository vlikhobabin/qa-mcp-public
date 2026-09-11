# Replace OSS-07 public-readiness disclosure and evidence integrity

## Status
4.done

## Owner
unassigned

## Series
oss-07-r1

## Order Index
406.1

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
- Exhausted source card:
  `openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md`.
- Latest safe published ref and current `origin/main` baseline:
  `61b8d90a82982ba7a9e5db2a2cf97689b0da69c4`.
- Canonical OSS-07 review evidence:
  `.runtime/changerail/reviews/oss-07-prepare-qa-mcp-public-repository-readiness.json`
  and
  `.runtime/changerail/reviews/oss-07-prepare-qa-mcp-public-repository-readiness.history.json`.
- Retained delivery evidence:
  `.runtime/changerail/evidence/oss-07-prepare-qa-mcp-public-repository-readiness/index.json`.
- Reviewed OSS-07 payload tree
  `406d765f57a94f6d1d142981c469b5c9b096f7aa` and fingerprint
  `sha256:d40c08931fc90832b7de669750082086c92d739269e83f88c9a8bc81c3774625`.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/oss-07-r1-a1-authorize-public-readiness-payload-complexity.md","authorization_id":"oss-07-r1-a1-authorize-public-readiness-payload-complexity"}`

## Summary
Own a replacement publication payload after OSS-07 ended with final review
cycle 3 `NO-GO` and exhausted both same-card rescue attempts. Preserve the
useful unpublished OSS-07 source snapshot, repair the remaining fail-closed
scanner grammar/type/count invariants and the curated JSONL inline payload
integrity defect, then hand one exact unchanged manifest/fingerprint to a new
independent review before publication.

This is a separate linked replacement card, not a third OSS-07 same-card fix.
The source OSS-07 card and its review evidence remain immutable final-NO-GO
lineage and are not publication authority.

## Lineage And Prior Findings
- Review cycle 1 found four blocker classes: encoded disclosure invisibility,
  missing hostile scanner tests, a non-standalone snapshot proof and semantic
  damage from broad privacy substitutions.
- Same-card rescue 1 repaired those classes, but review cycle 2 found one
  remaining blocker: lowercase credentials and disclosures under Git-visible
  test paths bypassed broad fixture exemptions.
- Same-card rescue 2 removed broad exemptions and extended hostile coverage,
  but review cycle 3 found three blockers: prefixed JSON/YAML credential
  assignments plus wrong-typed declared Base64 and under-count allowlists still
  false-PASS; 12 sanitized handshake rows retain stale inline SHA-256 values;
  and the reviewer launch did not preserve the supplied exact fingerprint.
- OSS-07 same-card rescue budget is `2/2`, remaining `0`, exhausted. No OSS-07
  payload may publish without this independently reviewed replacement.

## Current Hypothesis
The remaining defects share a missing typed integrity boundary. Scanner
allowances are consumed as maxima rather than exact multisets, structured
credential/Base64 parsing is not closed over supported value types and key
prefixes, and provenance checks only the outer file digest rather than declared
inline payload byte count and SHA-256. One typed, regression-tested verifier can
close these specific gaps without adding a new runtime or network capability.

## Acceptance
- The replacement owns the complete unpublished OSS-07 publication payload
  relative to safe base `61b8d90a82982ba7a9e5db2a2cf97689b0da69c4` and
  preserves exact SPDX `Apache-2.0` policy, public docs, provenance decisions
  and standalone snapshot behavior.
- Prefixed credential assignments expressed as JSON, YAML or environment-style
  syntax, including uninterrupted camelCase identifier prefixes, are detected
  case-insensitively without emitting matched values. Every non-empty supported
  assignment value is detected; no minimum secret length is imposed.
- Every declared structured `*_b64` field must be a valid Base64 string;
  non-string, malformed or undecodable declarations fail closed while other
  independently valid lines remain inspected.
- Fixture allowances are exact multisets keyed by
  category/path/source/value/count: both excess and missing occurrences fail,
  and global reconciliation catches an absent path or replaced source so no
  allowance can hide another value, source or path.
- Each curated JSON/JSONL row that declares `payload_b64`, `byte_count` and
  `sha256` is validated against decoded bytes. The 12 sanitized handshake rows
  have recomputed inline SHA-256 values, all 29 rows are byte-count/hash
  consistent, and the outer provenance ledger is regenerated.
- RED-first hostile tests demonstrate every cycle-3 bypass, the cycle-2
  short-value bypass and inline-hash mismatch before implementation, then pass
  against the repaired behavior.
- The published OSS-07-I2 six-file surface remains byte-identical and its
  `46/14/5/D14` control plus all `23/23` hostile outcomes pass. The failed
  OSS-07-I1 payload is not restored, copied or reconstructed.
- Before review, the delivery manifest, preflight, independently computed tree
  SHA and diff fingerprint all describe one exact unchanged payload. A fresh
  independent review returns a valid, fresh `GO` for that fingerprint before
  any scoped commit or push.
- OSS-08 and OSS-09 implementation, live/SSH/Windows/1C execution and any
  runtime target substitution remain out of scope.

## Change Set
- `oss-07-r1-enforce-disclosure-and-inline-evidence-integrity`

## Depends On
- `oss-07-r1-i1-investigate-public-readiness-payload-complexity` at
  `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`

## Verify
- RED-first focused hostile tests for prefixed structured credentials, short
  non-empty JSON/YAML/environment password assignments, wrong-typed declared
  Base64, under-count allowlists and stale inline payload byte-count/SHA
  declarations.
- `uv run pytest -q tests/test_public_repository_readiness.py`
- `uv run pytest -q -m "not live"`
- `python3 tools/public_readiness.py audit --history --json`
- `python3 tools/public_readiness.py provenance --check --json`
- `python3 tools/public_readiness.py docs --json`
- `python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations`
- `python3 tools/public_readiness.py snapshot --json`
- `bin/openspec validate --all --strict`
- Delivery-manifest working-tree/staged scope checks and `git diff --check`.
- Fresh independent ChangeRail review against the exact final fingerprint.

Observed offline result: the four new scanner hostile cases and stale curated
handshake check were RED before implementation, then the focused suite passed
`18` tests with the standalone snapshot separately GREEN. Full non-live passed
`1602` with `4` expected skips; audit has zero findings, provenance has `649`
entries, docs has `12/12` with zero broken links, all `29/29` handshake rows
match declared byte counts/SHA-256, and unchanged I2 returns `46/14/5/D14`
with `23/23` hostile outcomes. Evidence index:
`.runtime/changerail/evidence/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity/index.json`.

Same-card rescue attempt 1 retained three additional RED cases for the cycle-1
R1/R2 blockers. After the bounded repair, the focused suite passes `21` tests
with the standalone snapshot separately GREEN, and full non-live passes `1605`
with `4` expected skips. Fresh audit/history has zero findings, provenance
remains `649` Apache-2.0 entries, docs remain `12/12`, and byte-identical I2
again returns `46/14/5/D14` with `23/23` hostile outcomes.

Same-card rescue attempt 2 retained a RED nine-fixture syntax/suffix matrix for
short non-empty JSON, YAML and environment assignments. The single production
grammar change removes only the unsupported eight-byte floor; exact tuple
allowances now account for pre-existing benign short source/test examples.
Focused readiness passes `23` tests and full non-live passes `1606` with `4`
expected skips. Fresh audit/history has zero findings, provenance remains `649`
Apache-2.0 entries, docs remain `12/12`, standalone snapshot builds one wheel
and one sdist, strict OpenSpec passes `73/73`, and byte-identical I2 again
returns `46/14/5/D14` with `23/23` hostile outcomes.

## Archive
- `openspec/changes/archive/2026-09-03-oss-07-r1-enforce-disclosure-and-inline-evidence-integrity/`

## Related
- `openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md`
- `openspec/board/4.done/oss-07-i2-freeze-fail-closed-public-safety-matrix.md`
- `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`
- `openspec/board/4.done/oss-07-r1-a1-authorize-public-readiness-payload-complexity.md`
- `.runtime/changerail/reviews/oss-07-prepare-qa-mcp-public-repository-readiness.json`
- `.runtime/changerail/reviews/oss-07-prepare-qa-mcp-public-repository-readiness.history.json`
- `.runtime/changerail/evidence/oss-07-prepare-qa-mcp-public-repository-readiness/index.json`
- `.runtime/changerail/reviews/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.history.json`

## Result
The complete unpublished OSS-07 source snapshot is retained under replacement
ownership and the cycle-3 blockers are repaired. One canonical password-key
grammar now detects every non-empty prefixed JSON/YAML/env assignment without a
secret-length floor; declared `*_b64` types and encodings fail closed; fixture
allowances compare exact observed/configured
multisets globally in both directions, including absent paths and raw-to-symlink
source substitution; and current decoded payload bytes gate declared
byte count/SHA-256. The 12 stale sanitized handshake digests are recomputed,
the full 29-row file is internally consistent and outer provenance is current.
No live, SSH, Windows or 1C execution occurred, OSS-07-I2 is unchanged and the
failed I1 payload was not restored. Publication still requires one exact fresh
independent `GO`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `oss-07-r1-enforce-disclosure-and-inline-evidence-integrity`

### Why
The final OSS-07 reviewer demonstrated four concrete fail-open paths in the
public disclosure/evidence oracle, and the exhausted source card cannot consume
another same-card rescue.

### Goal
Make public-source admission typed and exact for structured credentials,
declared Base64, allowlist multiplicity and inline payload integrity while
preserving the full useful OSS-07 publication snapshot.

### Scope
- Close prefixed JSON/YAML/environment credential grammar and reject every
  wrong-typed or invalid declared `*_b64` value. Detect every non-empty
  password/passwd/pwd assignment value without a minimum length.
- Treat fixture allowances as exact category/path/source/value/count multisets,
  failing for both unallowlisted matches and unused allowance capacity.
- Validate declared JSON/JSONL payload byte counts and SHA-256 values, repair
  the 12 affected sanitized handshake rows and regenerate outer provenance.
- Add RED-first regression tests for all cycle-3 bypasses and integrity drift.
- Preserve OSS-07-I2 bytes and all Apache-2.0/public snapshot behavior; make no
  live, Windows, 1C, SSH, OSS-08 or OSS-09 change.

### Acceptance
- Each cycle-3 hostile fixture fails before the implementation and is detected
  afterward with a safe category/path/source/count finding.
- Audit, provenance, docs, standalone snapshot, full non-live tests, I2,
  strict OpenSpec, scope and whitespace gates all pass on one exact payload.

### Depends On
- `oss-07-r1-i1-investigate-public-readiness-payload-complexity` at
  `openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md`,
  plus immutable final-NO-GO OSS-07 lineage and safe base `61b8d90`.

### Related
- `openspec/changes/oss-07-r1-enforce-disclosure-and-inline-evidence-integrity/`

## Log
- 2026-09-03 created as the first linked replacement after OSS-07 review cycle
  3 returned final `NO-GO` with same-card rescue budget exhausted at `2/2`.
  It adopts the unpublished OSS-07 snapshot and narrows new implementation to
  scanner grammar/type/count invariants, inline JSONL payload integrity and
  exact manifest/fingerprint preservation before a fresh review.
- 2026-09-03 fast-forward planning completed one apply-ready change modifying
  the existing `qa-mcp-public-provenance` capability; live/Windows/1C and
  OSS-08/09 remain out of scope.
- 2026-09-03 RED-first evidence reproduced all four cycle-3 scanner/integrity
  bypasses and the 12 stale curated handshake hashes. The repaired focused
  suite is `18 passed` plus a separately GREEN standalone snapshot; full
  non-live is `1602 passed, 4 skipped`; audit/provenance/docs/I2/OpenSpec and
  whitespace gates are GREEN. The capability delta is synced and archived;
  exact manifest/fingerprint review is next.
- 2026-09-03 independent replacement review cycle 1 returned `NO-GO` for two
  blockers: configured allowance tuples were not reconciled when a whole path
  or source disappeared, and camelCase password-key prefixes remained
  undetected. Same-card rescue attempt 1 retained three RED hostile cases and
  repaired only those two blockers. Focused `21`, full non-live `1605/4`,
  audit/provenance/docs/I2 and standalone snapshot gates are GREEN; exact
  manifest scope is clean and normalized preflight is ready for fresh cycle-2
  review.
- 2026-09-03 independent replacement review cycle 2 returned `NO-GO` only for
  an unsupported eight-byte minimum in password-assignment detection. Bounded
  same-card rescue attempt 2 retained a nine-case RED matrix, removed only that
  floor, and reconciled newly visible benign occurrences through exact
  value-bound tuple allowances. Focused `23`, full non-live `1606/4`, zero-
  finding audit/history, provenance `649`, docs `12/12`, standalone snapshot,
  strict OpenSpec `73/73` and unchanged I2 `46/14/5/D14`, `23/23` are GREEN;
  final exact-payload normalization and fresh review cycle 3 are next.
- 2026-09-03T04:20:01Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
