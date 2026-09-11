## ADDED Requirements

### Requirement: Runtime packages ship readable source
Every supported qa-mcp wheel and container SHALL install the ordinary readable
Python modules used to execute the public core and SHALL NOT require a compiled
or stripped confidentiality variant.

#### Scenario: Installed package is inspected
- **WHEN** a release wheel or image is installed and the qa-mcp package is
  enumerated
- **THEN** the expected `.py` modules are present and importable
- **AND** no Nuitka loader is required.

### Requirement: Curated protocol assets ship plaintext and key-free
Curated distributable captures, templates and accepted mappings SHALL be normal
plaintext package assets and MUST load without an encryption key or decryption
module.

#### Scenario: Clean runtime loads bundled assets
- **WHEN** qa-mcp starts with no bundled-data key variables or files
- **THEN** representative JSON/JSONL assets parse through production loaders
- **AND** protocol bootstrap and mapping reads do not attempt decryption.

### Requirement: One open package contract serves both products
qa-mcp SHALL expose one readable versioned public package artifact for
standalone and downstream AI for 1C consumption; this repository MUST NOT
produce or document a protected cloud-only build.

#### Scenario: Distribution contracts are compared
- **WHEN** this repository's standalone and downstream-consumer distribution
  contracts are inspected
- **THEN** they identify the same public artifact and source-revision/digest
  scheme
- **AND** no alternate protected variant or runtime data key is offered.

### Requirement: Open assets retain integrity and privacy gates
Removing secrecy controls MUST NOT remove package-integrity checks or the rule
that only reviewed curated non-customer assets are distributable.

#### Scenario: Wheel asset integrity is verified
- **WHEN** the release wheel is built from a clean checkout
- **THEN** expected assets have deterministic manifest hashes and parse
  successfully
- **AND** missing, malformed or unreviewed assets block release.
