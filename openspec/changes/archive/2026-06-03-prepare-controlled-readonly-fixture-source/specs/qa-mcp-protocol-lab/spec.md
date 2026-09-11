## ADDED Requirements

### Requirement: Controlled fixture source readiness is reviewed before capture

The protocol lab SHALL document the controlled source boundary for read-only
fixture cases before those cases are used for live corpus capture.

#### Scenario: Fixture source is ready for a family

- **WHEN** a planned fixture family is prepared for live capture
- **THEN** the reviewed source evidence records the case id, element family,
  external source boundary, target form or element, expected read-only state
  and provider validation summary
- **AND** generated EDT workspaces, infobase exports, provider payloads and
  runtime logs remain outside reviewed git changes

#### Scenario: Fixture source is not ready for a family

- **WHEN** a planned fixture family cannot be represented safely in the
  controlled source
- **THEN** the reviewed source evidence records the family as `blocked`,
  `pending` or `partial` with owner route, unresolved reason and residual risk
- **AND** no later corpus row for that family is accepted from inferred
  metadata alone
