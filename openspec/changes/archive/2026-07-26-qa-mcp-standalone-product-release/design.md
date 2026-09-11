## Context

`publish_self_hosted.sh` already builds, scans, inventories and signs a frozen
component release. Its final activation step and default URL still target the
retired unauthenticated secret-link server.

## Goals / Non-Goals

**Goals:**

- Produce a root-consumable immutable `versions/<version>/` staging directory.
- Bind staged bootstrap and guidance to authenticated product-version paths.
- Fail closed on legacy component-side activation.
- Keep guidance solo-only and diagnostic-safe.

**Non-Goals:**

- Uploading S3 objects or portal pages from the component repository.
- Changing the frozen component manifest.
- Reworking the source license activation flow owned by the existing active
  `license-activation-bootstrap` change.
- Running live TestClient scenarios.

## Decisions

1. The default base is
   `https://releases.aifor1c.ru/qa-mcp/download/versions`; the staged version
   URL appends the exact manifest version.
2. `--server-root` and `--activate` fail before build/staging. The legacy
   `--release-link-id` input is accepted only as an inert compatibility input
   and is explicitly ignored.
3. A new component-owned standalone runbook is copied into all release-facing
   guidance filenames. Existing activation source/runbook files are not
   rewritten while their active OpenSpec change remains open.
4. The component stages only; root validates the signature/inventory and owns
   create-only remote publication.

## Risks / Trade-offs

- Existing automation may still pass a link id. Keeping it inert avoids an
  abrupt parsing failure while ensuring it cannot influence a URL or remote
  object.
- The source bootstrap still belongs to another active change. Deterministic
  staging substitutions remove retired release/license origins from the
  published artifact without absorbing that change.

## Verification

Offline tests inspect the helper, run a staged-release fixture, verify all
signed-manifest assets, assert product-relative paths, scan staged current
guidance for the legacy origin, and prove retired activation fails before
creating a staging directory.
