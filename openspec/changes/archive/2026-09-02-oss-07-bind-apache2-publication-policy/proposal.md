## Why

qa-mcp cannot be represented as ready for public source publication until the
operator-approved license, public contacts, history boundary and inherited I2
fail-closed prerequisite are one explicit repository policy. This must happen
before later OSS-07 disclosure, provenance or documentation claims.

## What Changes

- Add the exact Apache License 2.0 text, NOTICE/trademark attribution and SPDX
  `Apache-2.0` package metadata.
- Define a machine-readable publication policy and human-readable policy that
  select an audited source snapshot rather than exposing excluded internal Git
  history, and use public issue/security-reporting routes without personal
  contact data.
- Bind the published OSS-07-I2 files and its unchanged-control/23-mutation
  verifier into every repository-readiness gate.
- Fail closed on unresolved secret, privacy, provenance or I2 findings; never
  restore or reconstruct the exhausted OSS-07-I1 payload.

## Capabilities

### New Capabilities

- `qa-mcp-publication-policy`: Defines the exact license, legal/trademark
  attribution, public contact routes, history strategy, publication boundary
  and inherited fail-closed safety prerequisites for a public qa-mcp snapshot.

### Modified Capabilities

- none.

## Impact

This change affects package metadata, top-level legal files, public policy
documentation, OpenSpec workflow and offline verification inputs. It changes
no Python manager behavior, MCP provider setup, protocol/runtime tools, live
lab configuration or release automation. It requires no Windows, SSH, 1C,
TestClient, Vanessa, EDT/meta snapshot, Apache service or network execution.
