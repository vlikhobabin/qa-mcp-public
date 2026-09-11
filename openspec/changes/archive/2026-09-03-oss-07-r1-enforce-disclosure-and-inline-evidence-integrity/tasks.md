## 1. RED-first cycle-3 regressions

- [x] 1.1 Add hostile focused tests for prefixed JSON and YAML password
  assignments, a non-string declared `*_b64` value and an under-count fixture
  allowance; run only those tests and retain the expected RED outcomes.
- [x] 1.2 Add an inline JSONL integrity regression that fails when decoded
  `payload_b64` disagrees with declared `byte_count` or `sha256`; retain the
  expected RED outcome against the current stale handshake fixture.

## 2. Fail-closed public admission

- [x] 2.1 Implement one case-insensitive prefixed password-key grammar for
  quoted JSON, YAML and environment/assignment syntax without emitting values.
- [x] 2.2 Make structured `*_b64` traversal reject non-string, malformed and
  undecodable declarations while continuing independent line inspection.
- [x] 2.3 Compare observed scanner matches to fixture allowances as exact
  category/path/source/value/count multisets and fail for both over- and
  under-counts.
- [x] 2.4 Validate declared structured payload byte counts and SHA-256 values
  against decoded bytes before audit or provenance admission.

## 3. Curated evidence repair

- [x] 3.1 Recompute only the 12 stale inline SHA-256 values for the already
  sanitized handshake payloads and prove all 29 rows have matching byte counts
  and digests.
- [x] 3.2 Regenerate the outer asset provenance ledger after a clean disclosure,
  inline-integrity and unchanged-I2 gate, then verify it byte-exactly.

## 4. Offline verification and archive

- [x] 4.1 Run the focused readiness suite, confirming every new hostile test is
  GREEN and observes the production scanner/evidence boundary.
- [x] 4.2 Run `uv run pytest -q -m "not live"` and retain its complete outcome.
- [x] 4.3 Run public audit/history, provenance, 12-document links, standalone
  clean snapshot and the unchanged I2 `46/14/5/D14`, `23/23` oracle; retain
  concise evidence under ignored `.runtime/changerail/` only.
- [x] 4.4 Sync the `qa-mcp-public-provenance` delta, validate the change,
  capability and complete OpenSpec set strictly, and run `git diff --check`.

## 5. Same-card rescue 1 after review cycle 1

- [x] 5.1 Retain RED-first hostile tests proving an absent allowlisted path,
  raw-to-symlink/source substitution and camelCase JSON/YAML/env credential
  keys all bypass the reviewed implementation.
- [x] 5.2 Reconcile the complete configured and observed
  category/path/source/value/count multisets after scanning, including zero
  observations for missing paths or replaced sources.
- [x] 5.3 Extend the existing case-insensitive password suffix grammar to
  camelCase identifier prefixes without reporting matched values.
- [x] 5.4 Repeat focused, full non-live, audit/history, provenance, docs, I2,
  standalone snapshot, strict OpenSpec, whitespace, scope, manifest and
  normalized-preflight gates on one exact cycle-2 handoff payload.

## 6. Same-card rescue 2 after review cycle 2

- [x] 6.1 Retain RED-first JSON, YAML and environment fixtures proving short
  non-empty password/passwd/pwd values bypass the reviewed implementation,
  including the already-supported identifier-prefix and case variants.
- [x] 6.2 Remove only the unsupported eight-byte value floor so every
  non-empty supported assignment is detected without exposing its value.
- [x] 6.3 Repeat the complete offline verification, exact invariant hashes,
  manifest/scope and whitespace gates before normalized preflight and fresh
  independent review cycle 3.
