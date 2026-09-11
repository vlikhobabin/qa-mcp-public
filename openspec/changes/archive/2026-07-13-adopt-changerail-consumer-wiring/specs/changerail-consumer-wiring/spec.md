## ADDED Requirements

### Requirement: qa-mcp exposes canonical ChangeRail discovery
The qa-mcp repository SHALL expose canonical ChangeRail and `chrl` Claude
commands, Claude skills, Codex skills, OpenSpec lifecycle skills, and local
helper wrappers from `/opt/changerail`.

#### Scenario: Both agent clients discover the shared lifecycle
- **WHEN** Claude or Codex starts from the qa-mcp root
- **THEN** the canonical `changerail-*`, `chrl-*`, and OpenSpec lifecycle surfaces resolve from `/opt/changerail`
- **AND** the obsolete generic OPSX wiring is absent.

### Requirement: Domain and project skills retain separate ownership
ChangeRail adoption SHALL replace only generic workflow-owned surfaces and
SHALL document that AI1C domain overlays remain owned by `agent-core` while
qa-mcp-specific skills remain owned by qa-mcp.

#### Scenario: Consumer adoption does not absorb project expertise
- **WHEN** the generic workflow links are inspected
- **THEN** they resolve to `/opt/changerail`
- **AND** project/domain skill sources are not copied into or claimed by ChangeRail.

### Requirement: Local provider state remains private
The qa-mcp component SHALL keep generated full-provider MCP profiles and
runtime/auth state ignored while permitting public-safe canonical skill links
to be committed.

#### Scenario: Verification does not publish machine-specific profiles
- **WHEN** the consumer gate inspects local MCP profiles and ignore policy
- **THEN** both profiles cover the qa-mcp root with an exact-pinned filesystem MCP
- **AND** those generated profiles, credentials, sessions, and runtime reports remain excluded from the delivery payload.

### Requirement: Consumer adoption is fail-closed verified
The complete qa-mcp ChangeRail consumer SHALL pass every check implemented by
the canonical project verifier before review-gated publication.

#### Scenario: Canonical verification succeeds
- **WHEN** `/opt/changerail/bin/verify-project /opt/ai-dev-suite-for-1c/qa-mcp` runs
- **THEN** all 43 checks pass
- **AND** no stale OPSX wiring, missing helper, unsafe runtime policy, or profile scope failure is reported.
