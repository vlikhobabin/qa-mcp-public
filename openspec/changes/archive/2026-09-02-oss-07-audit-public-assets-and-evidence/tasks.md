## 1. Build The Offline Audit

- [x] 1.1 Add failing focused tests for exhaustive provenance, secret-safe
  findings, all-file scanning, private/customer/machine markers, RFC1918,
  password/private-key/service-token detection, structured Base64 and UTF-16
  payload decoding, malformed/invalid payload failure, lowercase/prefixed
  credential and `tests/`-path bypasses, symlink targets, exact counted fixture
  allowlisting, unsupported binary rejection and I2 gate invocation.
- [x] 1.2 Implement bounded standard-library audit/provenance commands that
  emit only safe category/path/count summaries and prohibit directory-wide or
  whole-file scanner exemptions.
- [x] 1.3 Sanitize exact historical lab/customer identities, remove the exact
  source-incomplete `.cfe`, sanitize the two decoded machine-bearing protocol
  assets length-preservingly, and preserve each report's technical outcome.

## 2. Freeze Provenance And Verify

- [x] 2.1 Generate the sorted per-file path/size/SHA-256/provenance/decision
  manifest, make `provenance --check` byte-compare the recomputed document, and
  gate both provenance check/write on clean disclosure/policy and I2 outcomes.
- [x] 2.2 Run current-tree and selected-history audit, provenance check, I2
  hostile-mutation oracle, strict change validation and whitespace checks.
- [x] 2.3 Record Windows-native and all live/platform verification as not
  applicable and do not run it; no protocol claim or runtime behavior changes.
