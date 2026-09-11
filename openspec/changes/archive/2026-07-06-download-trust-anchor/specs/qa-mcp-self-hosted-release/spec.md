## ADDED Requirements

### Requirement: Bootstrap release bases are HTTPS-only

The qa-mcp Windows bootstrap SHALL reject plain `http://` release bases before
downloading `manifest.json`, scripts, executables, sidecars or Docker archives.

#### Scenario: HTTP release base is refused
- **WHEN** an operator invokes `bootstrap.ps1 -ReleaseBase http://example.test/qa-mcp/r-test`
- **THEN** bootstrap exits with a clear HTTPS-required error
- **AND** no release asset is downloaded

#### Scenario: HTTPS release base is accepted for verification
- **WHEN** an operator invokes `bootstrap.ps1 -ReleaseBase https://releases.example.test/qa-mcp/r-test`
- **THEN** bootstrap proceeds to manifest signature verification before trusting
  any manifest asset metadata

### Requirement: Manifest metadata has a detached trust anchor

The qa-mcp self-hosted release channel SHALL publish a detached signature for
`manifest.json`, and `bootstrap.ps1` SHALL verify that signature with an
out-of-band public key before trusting manifest asset hashes or executing any
downloaded release asset.

#### Scenario: Missing manifest signature blocks bootstrap
- **WHEN** bootstrap downloads `manifest.json`
- **AND** the detached manifest signature is missing
- **THEN** bootstrap stops before downloading or executing manifest-declared
  assets

#### Scenario: Invalid manifest signature blocks bootstrap
- **WHEN** bootstrap downloads `manifest.json` and its detached signature
- **AND** signature verification fails against the configured public key
- **THEN** bootstrap stops before downloading or executing manifest-declared
  assets

#### Scenario: Valid manifest signature permits asset hash checks
- **WHEN** bootstrap verifies `manifest.json` against the configured public key
- **THEN** bootstrap may download manifest-declared assets
- **AND** each asset is still checked against the manifest sha256 before use
