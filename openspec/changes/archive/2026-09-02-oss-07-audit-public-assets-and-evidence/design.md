## Context

The public surface contains bundled protocol fixtures, one UI bitmap and more
than six hundred curated evidence files. Most are project-generated, but a
compiled configuration extension and several historical reports expose lab or
customer identifiers. A generated per-path ledger plus conservative scanner is
needed to make the redistribution decision reproducible.

## Goals / Non-Goals

**Goals:**

- Inventory every tracked file under the three declared asset/evidence roots.
- Bind path, byte length and SHA-256 to an explicit provenance/redistribution
  class and fail on drift.
- Detect high-confidence disclosure hazards without printing matched values.
- Sanitize narrow historical identifiers and remove the exact compiled `.cfe`
  artifact that lacks a source-complete redistribution basis.

**Non-Goals:**

- Reinterpret protocol claims, delete curated text/JSON evidence broadly or
  scan a live host.
- Modify release automation or OSS-08/09.

## Decisions

1. One standard-library Python entrypoint owns `audit`, `provenance` and
   `snapshot` subcommands to stay below the production-LOC investigation
   threshold and avoid new dependencies.
2. The generated manifest contains one entry per Git-visible file under
   `src/qa_mcp/_bundled/`, `src/qa_mcp/protocol/assets/` and
   `docs/protocol-research/evidence/`. Each entry carries SHA-256, bytes,
   provenance class, decision and rationale. Directory-level wildcard claims
   are insufficient.
3. Project-authored source/JSON/JSONL/Markdown/feature/script evidence and the
   project-created UI asset are redistributable under Apache-2.0 after scanner
   admission. The compiled `.cfe` is removed because its complete source and
   independent binary provenance are unavailable; its curated BSL/report
   evidence remains.
4. Findings are emitted as category/path/count only. Secret-like bytes are
   never echoed. Private Docker documentation subnets and reserved test values
   are allowlisted only by exact category, repository-relative path, source,
   matched bytes and occurrence count; directory-wide and whole-file exemptions
   are forbidden. Malformed JSON/JSONL, invalid declared Base64 and unsafe
   symlink targets fail closed. Historical real lab/customer identities are
   sanitized.
5. Selected-history scanning classifies excluded ancestors under the snapshot
   policy and scans current publishable bytes strictly. It does not rewrite or
   copy historical objects.

## Risks / Trade-offs

- [Risk] Pattern scans can false-positive fixtures. -> Allow only explicit
  reserved domains/documentation subnets and test markers by exact rule.
- [Risk] A generated ledger becomes stale. -> `provenance --check` recomputes
  the complete sorted document and compares bytes.
- [Risk] Sanitization damages historical meaning. -> Replace only endpoint,
  account and customer identity while retaining topology, command class and
  observed outcome.

## Migration Plan

Add RED tests, add the tool, sanitize the exact findings, delete the exact CFE,
generate the manifest, and require byte-identical `--check`. Rollback restores
only this change's sanitized text/artifact/manifest/tool changes; I2 is never
modified.

## Capture, Replay And Cleanup

No new capture or replay occurs. Existing curated captures are read as opaque
bytes for hashing and disclosure scanning. Dynamic values are only owned temp
paths; snapshot/audit cleanup removes only their temporary directory.

## Open Questions

- none.
