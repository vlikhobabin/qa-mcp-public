## ADDED Requirements

### Requirement: Shipped non-protocol modules are compiled to native code

The Docker build SHALL per-module compile the shipped non-protocol Python modules — `mcp_server.py`,
`license_gate.py`, and the `data/`, `debug/`, `regression/`, `scenario/` leaf modules — to native `.so` so that
their `.py` source (and its internal comments) is absent from the final image. Package `__init__.py` files MAY
remain as source where required for package and bundled-data resolution.

#### Scenario: Non-protocol leaf modules ship only as native code
- **WHEN** the built `qa-mcp-thin:protected` image is inspected for `mcp_server.py`, `license_gate.py`, and the
  listed `data`/`debug`/`regression`/`scenario` leaf modules
- **THEN** each is present only as a compiled `.so` and its `.py` source is absent (only package `__init__.py`
  files may remain as `.py`)

### Requirement: The shipped image carries no internal R&D references

The shipped image MUST carry zero internal R&D references in any readable form. After the docstrings are cleaned
(sibling change), the non-protocol modules are compiled, the package `__init__.py` files are docstring/comment
stripped, and the bundled data is encrypted, a recursive scan of the shipped `qa_mcp` package in the image SHALL
find zero `card [0-9]` / `Vanessa` / `evidence/` tokens. The `evidence/` path form is used because the bare
`from .evidence import …` reference to the `protocol.evidence` submodule is a legitimate code identifier, not a
research-leak path. The scan runs after `_bundled` encryption so the capture/mapping JSON (which carries
`evidence/` provenance paths) is ciphertext rather than plaintext.

#### Scenario: Image scan finds zero R&D tokens
- **WHEN** `grep -rIE 'card [0-9]|[Vv]anessa|evidence/'` is run over the shipped `qa_mcp` package inside the image
- **THEN** it returns zero matches

### Requirement: The compiled image stays functionally intact

Compiling the non-protocol modules SHALL NOT break the runtime. The MCP server must still start, expose its full
tool surface, drive the read path, and the dev source path must stay verifiable offline.

#### Scenario: Server still serves the full tool surface from compiled modules
- **WHEN** the built image is started
- **THEN** the MCP server launches from the compiled `mcp_server` entrypoint, lists 62 tools, and a
  `read_form_descriptor` call drives a client through the read path

#### Scenario: The gate module ships only as compiled native code
- **WHEN** the runtime loads `qa_mcp.license_gate` inside the image
- **THEN** there is no readable `license_gate.py` on disk and the module is loaded by the Nuitka compiled-module
  loader (so the startup gate cannot be edited out of the source) — verified by on-disk `.py` absence and the
  loader type, since Nuitka reports a compiled module's `__file__` as the original `.py` path

#### Scenario: The dev source path is unchanged
- **WHEN** the offline test suite is run against the dev `.py` source tree
- **THEN** it stays green (compilation is a build-time transform; no dev-source files are edited)
