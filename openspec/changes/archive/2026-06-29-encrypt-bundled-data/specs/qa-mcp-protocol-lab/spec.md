## ADDED Requirements

### Requirement: Bundled protocol data ships encrypted at rest and decrypts at runtime
The delivery image SHALL ship the bundled protocol **data** (`_bundled` genuine
captures, manager-frame / value-read templates and accepted-mappings) as
**ciphertext** (AES-GCM), not plaintext. The engine SHALL **decrypt in memory**
at runtime through a helper that lives in **compiled** code and whose decryption
**key is embedded in the compiled `.so`** (never present as readable `.py` or
plaintext in the image). Encryption SHALL be a **build-time transform**: the dev
`_bundled` tree stays plaintext and is not re-encoded in the repo.

#### Scenario: The image's bundled data is ciphertext
- **WHEN** the protected thin image is built
- **THEN** the `_bundled` capture/template/mapping files in the image are AES-GCM
  ciphertext (not readable JSON / JSONL)
- **AND** no readable `.py` in the image contains the decryption key

#### Scenario: The engine decrypts and still opens a real form
- **WHEN** the MCP server runs from the protected image and a tool needs bundled
  data (a capture replay, a manager-frame template or accepted-mappings)
- **THEN** the compiled loader decrypts the bytes in memory and the engine drives a
  real client (e.g. `read_form_descriptor` returns live fields) — functional parity
  with the plaintext build

#### Scenario: The loader transparently handles plaintext dev data
- **WHEN** the same loaders run against the dev `src/` tree where `_bundled` files
  are plaintext
- **THEN** the loader detects the files are not encrypted and reads them directly,
  so the offline `pytest` suite stays green with no `_bundled` re-encoding in the
  repo
