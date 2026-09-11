## Context

Bootstrap downloads `manifest.json`, scripts, executables and image archives
from `ReleaseBase`, then verifies each asset against sha256 values stored in
that same manifest. This protects against accidental corruption after the
manifest is trusted, but it does not protect against a compromised release
directory serving a matching malicious manifest and assets. The current script
also accepts plain HTTP release bases.

The card accepts either signed executables or a detached manifest signature.
Detached manifest signing is the smaller qa-mcp-owned change because the
release helper already generates one manifest that enumerates every executable,
script and image asset. Executable Authenticode signing can still be added later
as a defense in depth release policy.

## Goals / Non-Goals

**Goals:**

- Reject plain HTTP release bases before any network fetch.
- Verify `manifest.json` with a detached signature before trusting sha256
  values inside it.
- Require the verification key to be supplied out of band, not downloaded from
  the release directory being verified.
- Keep existing per-asset sha256 checks after manifest verification.
- Document the operator and CI signing flow.

**Non-Goals:**

- Add or manage a production signing key in this repository.
- Replace per-asset sha256 checks.
- Sign historical releases in place from this automated run.
- Change TestClient protocol or live 1C runtime behavior.

## Decisions

**D1 - Enforce HTTPS at normalized release-base validation.**
Parse the normalized release base as a URI and require scheme `https`. Reject
`http`, missing schemes and malformed values before downloading
`manifest.json`. This is intentionally stricter than relying on
`Invoke-WebRequest` defaults.

**D2 - Use a detached manifest signature as the first trust anchor.**
Publish `manifest.json.minisig` next to `manifest.json` and verify it before
converting the manifest JSON into trusted asset metadata. The public key is
provided by a new bootstrap parameter or locally trusted configuration so a
compromised release directory cannot swap both manifest and key.

Alternative considered: Authenticode-sign only downloaded executables. That
does not cover scripts, image archives or the manifest that chooses which
assets are downloaded.

**D3 - Fail closed when signature prerequisites are missing.**
If the public key, signature file or verifier is missing, bootstrap stops with
an explicit trust-anchor error. The release channel should not silently downgrade
to TLS-only verification for tester machines.

**D4 - Keep sha256 verification after signature verification.**
The detached signature authenticates the manifest. The existing sha256 checks
still prove that every downloaded asset matches the authenticated manifest
metadata before execution or `docker load`.

## Risks / Trade-offs

- Minisign tooling may not be installed on tester machines -> document the
  required trusted verifier path and fail with a clear setup error.
- Key rotation needs an operator process -> keep the public key out of the
  release directory and document rotation as a release procedure.
- A malicious same-origin bootstrap could remove checks -> this change follows
  the card's accepted detached-manifest criterion; signing `bootstrap.ps1`
  itself remains a possible follow-up.

## Verification Matrix

This is release-bootstrap trust behavior, not a 1C metadata or live TestClient
runtime change.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `delivery/bootstrap.ps1` release-base and manifest verification path | offline bootstrap contract tests and signature-fixture smoke | focused pytest/script assertions; retained signature verification transcript if a verifier fixture is executed | `.artifacts/openspec/download-trust-anchor/<run-id>/` | required | qa-mcp | N/A for live 1C runtime because bootstrap stops before TestClient launch on trust failure | bootstrap script signing remains a defense-in-depth follow-up |
