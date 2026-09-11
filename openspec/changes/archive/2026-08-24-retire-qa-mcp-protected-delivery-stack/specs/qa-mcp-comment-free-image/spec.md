## REMOVED Requirements

### Requirement: Shipped non-protocol modules are compiled to native code
**Reason**: All qa-mcp source is now intentionally readable in standalone and
AI for 1C cloud deployments.
**Migration**: Install the normal public wheel/source package in every image.

### Requirement: The shipped image carries no internal R&D references
**Reason**: Readable public source and curated research provenance are no longer
treated as confidentiality leaks.
**Migration**: Use publication privacy/provenance review to exclude only
credentials, customer data and private product material.

### Requirement: The compiled image stays functionally intact
**Reason**: There is no compiled confidentiality image after this change.
**Migration**: Run equivalent import, tool-surface and TestClient smoke checks
against the normal source-visible package.

### Requirement: Compiled protected modules omit docstrings
**Reason**: Public implementation documentation and docstrings are allowed.
**Migration**: Retain useful source documentation and validate it through
ordinary lint/test/review gates.

### Requirement: Protected-image verifier proves gate and decrypt invariants
**Reason**: No protected modules, encrypted bundled data or runtime data key
remain.
**Migration**: Replace the verifier with wheel/image package integrity and
plaintext asset-load tests.

### Requirement: Protected build fails loudly on leaf-module surface drift
**Reason**: Readable leaf modules are the desired open-source package surface.
**Migration**: Verify that expected modules and tool profiles are present and
importable rather than compiled or dropped.
