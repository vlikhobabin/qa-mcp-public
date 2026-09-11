## ADDED Requirements

### Requirement: Same-family compatible builds retain validate-first evidence

The qa-mcp supported-build manifest SHALL admit a new full build from an
already-supported platform family only after live protocol evidence shows that
the existing bundled corpus works with the live build identity. A green
compatibility result SHALL NOT replace committed capture templates.

#### Scenario: 8.3.27.2214 reuses the existing 8.3 corpus

- **WHEN** a TestClient on `8.3.27.2214` accepts the genuine TestManager
  handshake and the existing bundled 8.3 corpus passes the required read-only
  UI checks
- **THEN** `8.3.27.2214` is recorded in
  `compatible_platform_versions` for the 8.3 manifest
- **AND** the committed 8.3 template hash remains unchanged
- **AND** raw capture payloads remain outside Git.
