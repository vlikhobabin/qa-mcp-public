## MODIFIED Requirements

### Requirement: Shipped non-protocol modules are compiled to native code

The Docker build SHALL per-module compile the shipped private non-protocol
Python modules, including `mcp_server.py`, `telemetry_bridge.py`, and the `data/`, `debug/`,
`regression/`, and `scenario/` leaf modules, to native `.so` so their `.py`
source and internal comments are absent from the final image. The retired
`license_gate.py` module SHALL NOT be shipped as source or native code. Package
`__init__.py` files MAY remain as source where required for package and bundled
data resolution.

#### Scenario: Non-protocol leaf modules ship only as native code

- **WHEN** the built `qa-mcp-thin:protected` image is inspected for
  `mcp_server.py`, `telemetry_bridge.py`, and the listed
  `data`/`debug`/`regression`/`scenario` leaf
  modules
- **THEN** each shipped module is present only as a compiled `.so` and its
  `.py` source is absent, except permitted package `__init__.py` files
- **AND** no `license_gate` source or native module is present

### Requirement: The compiled image stays functionally intact

Compiling the non-protocol modules SHALL NOT break the runtime. The MCP server
must still start without product-license evaluation, expose its full tool
surface, drive the read path, and keep the dev source path verifiable offline.

#### Scenario: Server still serves the full tool surface from compiled modules

- **WHEN** the built image is started without qa-mcp entitlement, lease,
  broker, or license server material
- **THEN** the MCP server launches from the compiled `mcp_server` entrypoint,
  lists the expected tool surface, and a `read_form_descriptor` call can drive
  a client through the read path

#### Scenario: The protected entrypoint ships only as compiled native code

- **WHEN** the runtime loads `qa_mcp.mcp_server` inside the image
- **THEN** there is no readable `mcp_server.py` on disk and the module is loaded
  by the Nuitka compiled-module loader
- **AND** no product-license gate module is required or loaded

#### Scenario: The dev source path is unchanged

- **WHEN** the offline test suite is run against the dev `.py` source tree
- **THEN** it stays green because compilation remains a build-time transform

### Requirement: Compiled protected modules omit docstrings

The protected-image compile pipeline SHALL compile shipped protocol and
private entrypoint modules without Python docstrings so detailed
reverse-engineering prose is not recoverable from compiled `.so` files.

#### Scenario: Protocol docstrings are absent from compiled modules

- **WHEN** the protected image is built
- **AND** `strings` is run over shipped `qa_mcp/protocol/*.so` files
- **THEN** selected protocol docstring prose and internal R&D tokens are not
  present

### Requirement: Protected-image verifier proves gate and decrypt invariants

The standalone protected-image verifier SHALL prove the security invariants it
reports: private entrypoint modules ship as compiled native modules, readable
protected sources are absent, compiled modules do not expose selected protocol
prose, encrypted bundled data is decryptable through the production loader,
the runtime key is not shipped, and the MCP tool surface still loads. It SHALL
NOT require a product-license gate module or broker.

#### Scenario: Verifier rejects readable protected entrypoint modules

- **WHEN** `mcp_server.py` or another protected private entrypoint module remains
  readable in the runtime image
- **THEN** `docker/verify_protected_image.py` fails

#### Scenario: Verifier performs decrypt round trip

- **WHEN** bundled protected data is encrypted in the image and the independent
  runtime key is supplied
- **THEN** `docker/verify_protected_image.py` decrypts or opens representative
  bundled data through the production loader
- **AND** it fails if decryption is not usable by the runtime

#### Scenario: Verifier catches protocol prose leakage

- **WHEN** compiled protected modules still contain selected protocol docstring
  prose or internal R&D tokens
- **THEN** `docker/verify_protected_image.py` fails before publish

#### Scenario: Verifier does not depend on product licensing

- **WHEN** the protected image and verifier run without `ai1c-license`, a
  `license_gate` module, entitlement material, a lease, or a license server
- **THEN** product-license absence does not fail verification or startup
