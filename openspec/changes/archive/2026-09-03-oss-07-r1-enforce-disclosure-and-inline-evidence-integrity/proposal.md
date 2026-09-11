## Why

OSS-07 exhausted its two same-card rescues and received final review cycle 3
`NO-GO` because its public-readiness oracle still false-PASSes four concrete
disclosure/evidence-integrity cases. A separately reviewed replacement is
required before the otherwise useful Apache-2.0 source snapshot can publish or
OSS-08 can begin.

## What Changes

- Extend the public scanner to recognize prefixed credentials in structured
  JSON/YAML and environment-style assignments without exposing values.
- Reject non-string, malformed and undecodable declared `*_b64` fields.
- Make fixture allowance multiplicity exact in both directions for the full
  category/path/source/value/count identity.
- Validate declared JSON/JSONL payload byte counts and SHA-256 values, repair
  the 12 sanitized handshake digests and regenerate outer provenance.
- Add RED-first hostile regression tests and preserve one exact
  manifest/fingerprint through independent review.
- Preserve the full unpublished OSS-07 publication snapshot, exact SPDX
  `Apache-2.0`, and byte-identical published OSS-07-I2; do not restore I1.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-public-provenance`: require typed structured credential/Base64
  inspection, exact allowance multiplicity and internally consistent declared
  payload byte-count/SHA evidence before public provenance admission.

## Impact

This changes `tools/public_readiness.py`, its focused offline tests, one curated
handshake JSONL evidence file, the generated outer provenance ledger and the
public-provenance specification. It updates OpenSpec/board lineage and review
handoff metadata only. It does not change Python manager/runtime behavior, MCP
provider setup, live lab configuration, Windows/SSH/1C execution or OSS-08/09.
