## Context

The protected image and standalone bootstrap grew around a product-license
model: `delivery/bootstrap.ps1` activates through the broker, generated runs
set `QA_MCP_LICENSE_GATE=1`, the image vendors `ai1c-license`, and verifiers
assert that `license_gate` is compiled and non-removable. The separate
bundled-data protection model now supplies `BUNDLED_DATA_KEY_FILE` at runtime
so encrypted protocol data and its decryption key do not share shipped layers.

The operator decision removes qa-mcp product licensing but does not relax the
source/data/key protections. This is delivery, image, test, docs, and OpenSpec
workflow work. It makes no TestClient protocol claim, so capture sources, frame
ranges, dynamic fields, replay, live 1C cleanup, Vanessa MCP, and EDT/meta
evidence are not applicable.

## Goals / Non-Goals

**Goals:**

- Make source and rendered standalone bootstrap paths license-free.
- Stop shipping and invoking the qa-mcp product-license broker.
- Remove license-gate-specific compile/verifier invariants without weakening
  protected source, encrypted bundled data, or no-key-in-image checks.
- Retire the superseded active `license-activation-bootstrap` work without
  applying or archiving it as completed.

**Non-Goals:**

- Remove `BUNDLED_DATA_KEY_FILE` or ship plaintext bundled protocol data.
- Change root-owned license components or other providers' policies.
- Change self-hosted release-link activation commands that publish an artifact
  rather than activate a product license.
- Run a live TestClient protocol scenario.

## Decisions

1. **Remove broker assets from the final image.** A free component has no need
   to carry `delivery/broker/ai1c-license` or bake a broker path into the image.
   Keeping the binary as historical baggage would enlarge the public attack
   surface and make zero-invocation harder to prove.
2. **Keep data protection orthogonal.** Bootstrap may continue mounting
   `BUNDLED_DATA_KEY_FILE`; its source is an operator-provided protected input,
   never an entitlement, lease, activation response, or broker command.
3. **Preserve compilation based on confidentiality, not licensing.** The
   `mcp_server` and other private implementation modules remain compiled and
   readable source remains forbidden. `license_gate` disappears from compile
   lists, loader assertions, layer fixtures, and verifier terminology.
4. **Cancel superseded active work by removing its active change directory.**
   Its tracked Git history and the replacement card preserve lineage. Running
   `openspec archive` would falsely claim its activation tasks were delivered
   and would sync obsolete license requirements into main specs.
5. **Use generated-bootstrap tests as the cross-format contract.** Source
   assertions and rendering tests must prove that the generated script contains
   neither activation/broker commands nor `QA_MCP_LICENSE_*` wiring. A Windows
   PowerShell parser check remains part of the project verification floor when
   the authorized workstation is reachable.

## Risks / Trade-offs

- **[Risk] Product-license and release-link uses of “activation” are confused.**
  -> Remove only broker/product activation; keep clearly named self-hosted
  publication/link activation behavior and tests.
- **[Risk] Removing gate assertions weakens source protection.** -> Replace
  gate-specific assertions with generic protected entrypoint/module checks and
  retain archive-level source, plaintext-data, and key leakage tests.
- **[Risk] The bootstrap loses its bundled-data key source.** -> Keep the
  protected key-file input and mount, and add tests that classify it explicitly
  as data protection rather than product licensing.
- **[Risk] Windows parser evidence is unavailable.** -> Run the offline
  renderer/tests first and record the exact workstation check result; stop if a
  mandatory reachable Windows verification cannot be completed.

## Migration Plan

1. Add RED assertions to startup, rendered-bootstrap, Dockerfile/verifier, and
   archive fixture tests for the license-free behavior.
2. Remove broker activation and gate wiring from source delivery/image paths,
   then update current runbooks and release docs.
3. Remove the superseded active OpenSpec change and sync replacement delta
   specs.
4. Run focused Python tests, protected archive/source/key checks, renderer
   verification, strict OpenSpec validation, and the Windows parser check when
   required/available.

Rollback is a scoped source revert. Re-enabling product licensing is not a
supported operational rollback and requires a new product decision and change.

## Open Questions

- None for implementation. The source card explicitly separates bundled-data
  protection from qa-mcp product entitlement.
