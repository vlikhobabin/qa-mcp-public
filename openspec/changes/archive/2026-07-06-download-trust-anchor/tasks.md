## 1. HTTPS Release Base

- [x] 1.1 Add release-base URI validation to `delivery/bootstrap.ps1` after `DistBase` fallback and normalization.
- [x] 1.2 Reject `http://`, missing-scheme and malformed release bases before `Invoke-WebRequest` is called.
- [x] 1.3 Add focused tests proving plain HTTP release bases are refused.

## 2. Manifest Signature Verification

- [x] 2.1 Add bootstrap parameters or trusted local configuration for the detached manifest public key and verifier path.
- [x] 2.2 Download `manifest.json.minisig` and verify `manifest.json` before parsing it as trusted metadata.
- [x] 2.3 Fail closed when the signature, public key or verifier is missing or invalid.
- [x] 2.4 Preserve existing sha256 verification for every manifest-declared asset after manifest signature verification succeeds.

## 3. Release Publishing And Docs

- [x] 3.1 Extend publish tooling or release docs to generate and stage `manifest.json.minisig`.
- [x] 3.2 Document the out-of-band public-key handoff and tester bootstrap command.
- [x] 3.3 Document signing-key rotation and the reason same-origin `.sha256` sidecars are not sufficient.

## 4. Verification

- [x] 4.1 Run focused bootstrap/release tests covering HTTPS rejection and signature flow.
- [x] 4.2 Run `openspec validate download-trust-anchor --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Retain any signature-fixture transcript under `.artifacts/openspec/download-trust-anchor/<run-id>/`.
