## 1. Test-First Delivery Contract

- [x] 1.1 Invert focused standalone/rendered-bootstrap tests to require no
  product-license parameters, activation command, lease mount,
  `QA_MCP_LICENSE_*` wiring, or broker path, while retaining the protected
  bundled-data key-file mount; record the pre-implementation RED result.
- [x] 1.2 Invert Dockerfile/verifier/archive-fixture tests so the image contains
  no `ai1c-license` or `license_gate` module and the remaining readable-source,
  plaintext-data, and runtime-key protections still fail on injected leaks;
  record the RED result.

## 2. Remove Bootstrap And Image Wiring

- [x] 2.1 Remove product-license parameters, activation execution, lease
  volume, and `QA_MCP_LICENSE_*` environment wiring from
  `delivery/bootstrap.ps1` and the generated standalone bootstrap path while
  preserving `BUNDLED_DATA_KEY_FILE` as an independent protected input.
- [x] 2.2 Remove the broker binary COPY, gate module compile/drop/smoke
  assertions, broker environment defaults, and license-gate-specific verifier
  checks from the thin-image path.
- [x] 2.3 Remove obsolete vendored broker assets/helpers when no current
  release path consumes them, and update source/archive fixtures accordingly.

## 3. Documentation And Workflow State

- [x] 3.1 Update current standalone, Docker, and delivery runbooks so they
  require no qa-mcp product key, entitlement, activation server, lease, broker,
  or license gate and clearly preserve the separate 1C platform license and
  bundled-data key requirements.
- [x] 3.2 Remove the superseded active
  `openspec/changes/license-activation-bootstrap/` directory without applying
  or archiving its tasks, and retain supersession lineage in the card.

## 4. Verification

- [x] 4.1 Run focused config/startup, standalone renderer, protected-image
  verifier/archive, and release-script tests; record why each changed test
  observes the relevant source and would fail on product-license regression.
- [x] 4.2 Render the shipped standalone bootstrap and scan it plus current
  delivery/image/docs surfaces for forbidden product-license wiring while
  confirming the bundled-data key-file path remains.
- [x] 4.3 Run the protected saved-archive scanner tests (and a safe image smoke
  if the local Docker contour is available) to prove readable source,
  plaintext bundled data, and runtime-key leakage remain blocked.
- [x] 4.4 Parse the rendered bootstrap in the authorized Windows-native
  PowerShell contour and retain the exact command/outcome, or record a concrete
  runtime gap if the contour cannot execute the changed worktree.
- [x] 4.5 Run strict change/all OpenSpec validation and `git diff --check`;
  protocol capture/evidence indexing is N/A because no TestClient protocol
  knowledge changes.
