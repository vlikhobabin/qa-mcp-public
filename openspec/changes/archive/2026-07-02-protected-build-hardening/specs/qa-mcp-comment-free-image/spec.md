## ADDED Requirements

### Requirement: Compiled protected modules omit docstrings

The protected-image compile pipeline SHALL compile shipped protocol and gate-bearing modules without Python docstrings so detailed reverse-engineering prose is not recoverable from compiled `.so` files.

#### Scenario: Protocol docstrings are absent from compiled modules
- **WHEN** the protected image is built
- **AND** `strings` is run over shipped `qa_mcp/protocol/*.so` files
- **THEN** selected protocol docstring prose and internal R&D tokens are not present

### Requirement: Protected-image verifier proves gate and decrypt invariants

The standalone protected-image verifier SHALL prove the same security invariants it reports: gate-bearing modules ship as compiled native modules, readable protected sources are absent, compiled modules do not expose selected protocol prose, encrypted bundled data is decryptable through the production loader, and the MCP tool surface still loads.

#### Scenario: Verifier rejects readable gate modules
- **WHEN** `mcp_server.py` or `license_gate.py` remains readable in the runtime image
- **THEN** `docker/verify_protected_image.py` fails

#### Scenario: Verifier performs decrypt round trip
- **WHEN** bundled protected data is encrypted in the image
- **THEN** `docker/verify_protected_image.py` decrypts or opens representative bundled data through the production loader
- **AND** it fails if decryption is not usable by the runtime

#### Scenario: Verifier catches protocol prose leakage
- **WHEN** compiled protected modules still contain selected protocol docstring prose or internal R&D tokens
- **THEN** `docker/verify_protected_image.py` fails before publish
