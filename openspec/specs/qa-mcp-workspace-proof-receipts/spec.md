# qa-mcp-workspace-proof-receipts Specification

## Purpose

Define policy-gated QA/TestClient proof receipts for server SSH workspace
deliveries, preserving immutable pushed source identity boundaries and bounded
diagnostics.

## Requirements

### Requirement: QA proof receipts are policy gated
qa-mcp SHALL report server SSH workspace QA/TestClient proof as `not-required`
unless an explicit project policy or card requires QA proof for the workspace
delivery phase.

#### Scenario: Missing optional QA proof is not required
- **WHEN** a server SSH workspace receipt is requested without a policy requiring
  QA proof
- **THEN** qa-mcp reports proof status `not-required`
- **AND** the receipt does not fabricate a scenario evidence reference.

#### Scenario: Missing required QA proof is a gap
- **WHEN** a server SSH workspace receipt is requested with a policy requiring
  QA proof
- **AND** no QA scenario evidence reference is provided
- **THEN** qa-mcp reports proof status `missing`
- **AND** the receipt includes a bounded diagnostic naming the missing QA proof.

### Requirement: QA proof receipts bind to pushed source identity
qa-mcp SHALL bind required QA proof receipts to the selected project/repository
identity, commit SHA, tree SHA, source scope and source generation or snapshot
identity supplied by the workspace handoff.

#### Scenario: Required proof is current
- **WHEN** a policy requires QA proof
- **AND** the QA scenario evidence reference names the same commit SHA and tree
  SHA as the selected workspace source identity
- **THEN** qa-mcp reports proof status `current`
- **AND** the receipt includes the project/repository identity, source scope,
  source generation or snapshot id and scenario evidence reference.

#### Scenario: Required proof is stale
- **WHEN** a policy requires QA proof
- **AND** the QA scenario evidence reference commit SHA or tree SHA differs from
  the selected workspace source identity
- **THEN** qa-mcp reports proof status `stale`
- **AND** the receipt diagnostic names the stale identity field without exposing
  source bodies or local workspace paths.

### Requirement: QA proof receipt diagnostics are bounded
qa-mcp SHALL reject forbidden source transport and retained evidence routes for
server SSH workspace QA receipts before producing a ready or current receipt.
Receipts MUST NOT retain screenshots, raw protocol logs, customer data, infobase
dumps, XML/BSL source bodies, mutable workspace paths, host bridge source
payloads or MCP file payloads.

#### Scenario: Forbidden mutable source route is rejected
- **WHEN** a workspace receipt input contains a mutable server SSH workspace
  path, host bind, network share, MCP file payload, host bridge source body or
  raw source body marker
- **THEN** qa-mcp reports proof status `unavailable`
- **AND** the diagnostic uses a bounded reason code instead of retaining the
  rejected value.

#### Scenario: Evidence reference is retained without evidence body
- **WHEN** required QA proof is current
- **AND** the input includes a scenario evidence reference and raw evidence
  fields such as a screenshot or protocol log body
- **THEN** qa-mcp retains the scenario evidence reference
- **AND** it omits the raw evidence fields from the receipt.
