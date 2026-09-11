## MODIFIED Requirements

### Requirement: Protected image archives are scanned at the saved-layer level

qa-mcp release gates SHALL verify the saved Docker image archive for protected
thin images by inspecting every image layer tar and image config/history
metadata, not only the merged runtime filesystem. The gate MUST fail if any
saved layer exposes readable protected protocol or private entrypoint source,
unencrypted bundled protocol data, or bundled-data encryption key material.
The archive scan SHALL NOT require or validate product-license broker or gate
artifacts.

#### Scenario: Archive scanner rejects a plaintext protected layer

- **WHEN** a saved protected thin image archive contains a layer entry with
  readable `qa_mcp/protocol/*.py` source other than package `__init__.py`
- **THEN** the archive scanner fails before the archive can be staged or
  published

#### Scenario: Archive scanner rejects readable protected entrypoints

- **WHEN** a saved protected thin image archive contains readable
  `qa_mcp/mcp_server.py` or another protected private entrypoint source
- **THEN** the archive scanner fails before the archive can be staged or
  published

#### Scenario: Archive scanner rejects plaintext bundled protocol data

- **WHEN** a saved protected thin image archive contains unencrypted bundled
  captures, templates, or accepted mappings under `qa_mcp/_bundled`
- **THEN** the archive scanner fails before the archive can be staged or
  published

#### Scenario: Archive scanner rejects bundled-data key leakage

- **WHEN** a saved protected thin image archive contains the active bundled-data
  key in a layer payload, image config, or image history metadata
- **THEN** the archive scanner fails before the archive can be staged or
  published

#### Scenario: Archive scanner is independent of product licensing

- **WHEN** a saved protected image contains no `ai1c-license` binary,
  product-license gate module, entitlement, or lease
- **THEN** that absence does not cause the archive verification to fail
