## ADDED Requirements

### Requirement: The thin delivery image ships the protocol engine compiled to native code
The thin (model-B) delivery image SHALL ship the protocol engine
(`qa_mcp/protocol/`) as **compiled native `.so` modules**, with **no readable
`protocol/*.py` source** in the image. Compilation SHALL be a **build-time
transform**: a Docker builder stage on the image's exact Python/arch
(`python:3.13`, linux-amd64) per-module-compiles each `protocol/*.py` to a `.so`
in place; the dev `src/` source is not edited. `mcp_server.py` (orchestration)
remains readable `.py`.

#### Scenario: The published thin image contains no readable protocol source
- **WHEN** the thin image is built from `docker/Dockerfile.thin`
- **THEN** the installed `qa_mcp/protocol/` directory in the image contains the
  compiled `.so` modules and **zero `*.py` files** (other than what Nuitka
  requires)
- **AND** `mcp_server.py` is still present as `.py` and imports the compiled
  protocol package

#### Scenario: The compiled build keeps functional parity and drives a real client
- **WHEN** the MCP server is started from the compiled thin image
- **THEN** it starts, exposes the full tool surface (the model-B tool count), and
  a protocol tool such as `read_form_descriptor` drives a live TestClient and
  returns real form fields — identical behavior to the readable `.py` build

#### Scenario: In-package protocol data files stay reachable after compilation
- **WHEN** the protocol engine resolves a `Path(__file__)`-relative data file in
  the compiled image (`protocol/bootstrap_frames_1to3.json` for the synth
  bootstrap, `protocol/assets/calendar_button.png` for XTEST)
- **THEN** the `protocol/` directory and those data files are preserved by the
  per-module compile, so the loads resolve and the synth-bootstrap read path
  works — a single-package `.so` that breaks this path SHALL NOT be used

#### Scenario: Dev source and offline tests are unaffected
- **WHEN** the offline `pytest` suite runs against the dev `src/` tree
- **THEN** it runs the readable `.py` path and stays green, because compilation
  happens only in the image build and does not modify `src/`
