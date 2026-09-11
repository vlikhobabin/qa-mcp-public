## ADDED Requirements

### Requirement: Semantic source inventory is documented

The protocol lab SHALL document approved `help-mcp`, `meta-mcp` and `edt-mcp`
semantic sources before using them to label corpus evidence, including the
provider owner, source build or version when known, external workspace or
snapshot boundary, allowed use and compact readiness evidence or provider-gap
record.

#### Scenario: Semantic source is approved for corpus labeling

- **WHEN** help, metadata or EDT context is used to select or label a protocol
  corpus case
- **THEN** the source inventory records the provider id, source purpose,
  source location or external boundary, readiness evidence path and owner
- **AND** generated EDT workspaces, infobase exports, raw provider payloads and
  local runtime output remain outside reviewed git changes

#### Scenario: Semantic source is unavailable

- **WHEN** an optional help, metadata or EDT source cannot be reached or cannot
  inspect the needed object model
- **THEN** the source inventory or compact evidence records the provider gap,
  affected semantic use, owner route and residual risk
- **AND** raw TCP capture, normalization, replay and direct Python-manager
  probing remain usable without that source
