## ADDED Requirements

### Requirement: Protected image archives are scanned at the saved-layer level

qa-mcp release gates SHALL verify the saved Docker image archive for protected
thin images by inspecting every image layer tar and image config/history
metadata, not only the merged runtime filesystem. The gate MUST fail if any
saved layer exposes readable protected protocol source, readable gate-bearing
modules, unencrypted bundled protocol data, or the bundled-data encryption key.

#### Scenario: Archive scanner rejects a plaintext protected layer
- **WHEN** a saved protected thin image archive contains a layer entry with
  readable `qa_mcp/protocol/*.py` source other than package `__init__.py`
- **THEN** the archive scanner fails before the archive can be staged or
  published

#### Scenario: Archive scanner rejects readable gate modules
- **WHEN** a saved protected thin image archive contains readable
  `qa_mcp/mcp_server.py` or `qa_mcp/license_gate.py`
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

### Requirement: Self-hosted publish gates on the archive scanner

The qa-mcp self-hosted publish helper SHALL run the saved-archive protected
image scanner after `docker save` and before copying the image archive into the
staged release directory. A failed archive scan MUST block staging, manifest
creation, upload, and public-link activation.

#### Scenario: Archive scan blocks staging
- **WHEN** `publish_self_hosted.sh` builds and saves a protected thin image whose
  saved archive fails the archive scanner
- **THEN** the helper exits non-zero before copying the image archive into the
  versioned release directory

#### Scenario: Clean archive can be staged
- **WHEN** `publish_self_hosted.sh` builds and saves a protected thin image whose
  saved archive passes the archive scanner
- **THEN** the helper can continue to sha256 sidecars, component manifest
  creation, and optional activation
