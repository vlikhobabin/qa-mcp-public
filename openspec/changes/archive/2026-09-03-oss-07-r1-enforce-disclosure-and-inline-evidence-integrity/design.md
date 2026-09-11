## Context

The source OSS-07 payload is an unpublished working-tree snapshot based on
`61b8d90`. Its cycle-3 review proved that the public scanner's byte-regex and
allowance-consumption model is incomplete and that sanitizing a curated JSONL
payload can preserve outer provenance while invalidating row-local digests.
The source card exhausted both same-card rescues, so this first linked
replacement must own the full payload and obtain a new exact-fingerprint review.

The affected capture source is the 29-row curated 8.5 handshake JSONL under
`docs/protocol-research/evidence/card115-8-5-handshake-decode-2026-06-25/`.
Twelve `manager_to_client` rows contain the length-preserving sanitized host
label: their decoded byte counts remain correct, but their declared SHA-256
values still describe the original payload bytes. No new frame capture,
protocol claim or replay is required.

## Goals / Non-Goals

**Goals:**

- Detect case-insensitive prefixed password names consistently across quoted
  JSON keys, YAML keys and environment/assignment syntax.
- Fail closed for every declared `*_b64` value that is not a valid Base64
  string, while continuing independent JSONL-line inspection.
- Compare observed and configured fixture matches as exact multisets, including
  missing occurrences.
- Validate row-local `payload_b64` against declared `byte_count` and `sha256`
  before audit/provenance success.
- Recompute only the 12 stale sanitized payload digests, regenerate the outer
  provenance document and preserve one exact manifest/fingerprint through review.

**Non-Goals:**

- Restoring OSS-07-I1 or changing byte-identical OSS-07-I2.
- Expanding credential discovery beyond the reviewed password-name family or
  inventing a general secret-analysis language.
- Capturing/replaying 1C traffic, running live/SSH/Windows/1C checks, or changing
  Python manager/MCP runtime behavior.
- Implementing OSS-08 release automation or OSS-09 cutover.

## Decisions

### Use one canonical assignment grammar over raw/decoded views

The scanner will recognize a password key ending in `password`, `passwd` or
`pwd`, optionally preceded by underscore-separated or uninterrupted camelCase
identifier prefixes, followed by either `=` or `:` and a concrete value.
Quoted structured keys and unquoted YAML/env keys use the same case-insensitive
suffix rule. A concrete value means every non-empty supported assignment value;
there is no minimum password length. This closes the exact reviewed gap without introducing
format-specific parsers whose accepted syntax would diverge.

Alternative: special-case JSON and YAML independently. Rejected because it
duplicates the security boundary and would still leave other textual structured
formats inconsistent.

### Return declared-payload findings from structured traversal

JSON/JSONL traversal will classify non-string `*_b64` declarations separately
from invalid string encodings. Successfully decoded payloads remain available
for disclosure inspection. A row that also declares `byte_count` or `sha256`
will be checked for type, canonical SHA-256 form and equality to decoded bytes.
Findings expose only category/path/source/count, never values or payload bytes.

Alternative: validate inline hashes only in the provenance generator. Rejected
because `audit` and standalone snapshot admission must fail on the same evidence
integrity defect before provenance can be regenerated.

### Compare exact observed/configured match multisets per identity

For every category/path/source combination, the scanner will count observed
matched byte values, compare that map to the decoded policy allowance map, and
emit the absolute multiplicity difference. An unconfigured value, an excess
configured fixture, and unused allowance capacity all fail. This preserves the
full category/path/source/value/count identity without outputting the value.

Alternative: keep decrement-only consumption and separately audit policy counts.
Rejected because two algorithms could disagree and recreate latent allowance.

### Repair sanitized row-local digests, not payload semantics

The twelve affected JSONL rows keep their already-reviewed sanitized
`payload_b64`, `byte_count`, direction, timestamps, connection/chunk identity and
preview fields. Only each stale `sha256` is recomputed from decoded payload bytes.
The complete file must then verify 29/29, after which the outer provenance ledger
is regenerated from the reviewed tree.

Alternative: preserve old digests under an `original_sha256` field. Rejected
because the original private payload bytes are not public inputs and cannot be
reproduced by consumers; the existing `sha256` contract describes current row
bytes.

### Freeze review handoff after manifest reconciliation

Immediately before reviewer launch, the implementing/orchestrator context will
reconcile all committable paths, run normalized preflight, compute the
fingerprint independently, and pass those exact values to a fresh reviewer.
No tracked file may change between that computation and reviewer completion.

## Risks / Trade-offs

- [Exact under-count checks expose stale fixture allowances after unrelated
  edits] → Treat that as intended fail-closed policy drift and update an
  allowance only with a reviewed exact-value reason and hostile test.
- [A broad password regex creates false positives in source/tests] → Preserve
  exact byte-value allowances and require exact counts, so source examples are
  admitted narrowly rather than excluded by directory or file.
- [Inline validation encounters unrelated JSON with similarly named fields] →
  Apply integrity comparison only when a structured object declares
  `payload_b64` together with `byte_count` and/or `sha256`; every `*_b64` field
  still receives type/decode validation.
- [Outer provenance changes after the row repair] → Regenerate deterministically
  only after the audit is clean and verify a byte-exact `--check` result.
- [Fingerprint drift repeats] → Make card/manifest updates before the final
  preflight and prohibit tracked edits until the verdict has been validated.

## Migration Plan

1. Add hostile tests and retain their RED outcomes outside tracked source.
2. Implement scanner and inline integrity checks until the focused suite passes.
3. Recompute the twelve current-payload digests and verify all 29 rows.
4. Regenerate outer provenance and run the complete offline verification floor.
5. Sync/archive this change, reconcile the replacement manifest and card, then
   compute one final preflight/fingerprint and launch a fresh reviewer.
6. Publish only on a fresh valid `GO`; otherwise retain `NO-GO` and follow the
   replacement-card rescue/investigation policy.

Rollback before publication is simply leaving the replacement unpublished; the
safe public baseline remains `61b8d90`.

## Open Questions

None. Cycle-3 findings, scope and verification floor are exact and locally
reproducible.
