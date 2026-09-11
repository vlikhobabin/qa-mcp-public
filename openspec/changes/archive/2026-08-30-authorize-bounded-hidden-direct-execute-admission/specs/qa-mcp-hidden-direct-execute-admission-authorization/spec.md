## ADDED Requirements

### Requirement: Authorization binds one exact investigation and successor
The published authorization MUST contain the canonical path and id of
`oss-06-i2-publish-hidden-direct-execute-investigation-decision` and
`oss-06-s7-admit-hidden-direct-execute-public-route`, and MUST be valid only
when the investigation is an unchanged tracked `4.done` artifact with exact
dependency and block relations.

#### Scenario: Exact published relation is present
- **WHEN** S7 deterministic preflight reads the authorization source
- **THEN** the investigation, authorization and successor paths, ids and
  relations match exactly before any semantic review is allowed

#### Scenario: Relation or identity differs
- **WHEN** any referenced path, id, lane, dependency or block relation is
  missing, stale or substituted
- **THEN** the authorization is invalid and preflight stops without review

### Requirement: Authorization is bounded and non-transferable
The authorization MUST set `production_loc_ceiling` to `500` and
`allow_new_authority_or_wire_protocol` to `true` for S7 only. It MUST NOT apply
to S1-S6, another card, a larger payload or a generic execution authority.

#### Scenario: Exact S7 stays within the ceiling
- **WHEN** S7 adds no more than `500` production LOC and declares the reviewed
  backward-compatible capability
- **THEN** the authorization may satisfy only the deterministic LOC/protocol
  complexity guard and does not replace critical semantic review

#### Scenario: Scope or ceiling is exceeded
- **WHEN** another card references the authorization or S7 exceeds `500`
- **THEN** deterministic preflight fails closed and publication is forbidden

### Requirement: Authorization publication has no runtime effect
This card MUST change only authorization/spec/card documentation and MUST NOT
modify host-agent/Python source, execute Windows 1C or admit the stable tool.

#### Scenario: Production or runtime mutation enters scope
- **WHEN** manifest or evidence audit finds production source or runtime action
  owned by the authorization card
- **THEN** review is blocked until the authorization is documentation-only
