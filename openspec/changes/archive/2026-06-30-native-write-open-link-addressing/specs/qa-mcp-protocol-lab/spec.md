## ADDED Requirements

### Requirement: Native write tools can open target forms by nav-link
The qa-mcp native write path SHALL support an explicit `open_link` parameter for field-write operations so a write can target an arbitrary managed form without replaying a fixture form as the foreground target.

#### Scenario: Open-link write targets a resolved form
- **WHEN** a caller invokes a native field-write tool with `open_link` and a field name
- **THEN** qa-mcp opens the nav-link target in the TestClient session before sending write frames
- **AND** the result identifies the requested `open_link`, the opened form or blocked-open reason, and the target field

#### Scenario: Fixture write remains compatible
- **WHEN** a caller omits `open_link`
- **THEN** qa-mcp uses the existing capture-backed fixture setup path
- **AND** existing fixture field writes keep their previous result shape and commit semantics

### Requirement: Open-link write evidence is explicit
New claims about config-agnostic write behavior SHALL include retained evidence that identifies the target form, field, write result and verification method without committing raw captures or local runtime logs.

#### Scenario: Live open-link write proof is retained
- **WHEN** a live TestClient proof is run for an open-link write
- **THEN** the evidence bundle records the target nav-link, field, command/tool call summary, result status and read-back or provider-gap outcome
- **AND** raw capture streams and platform logs remain under ignored runtime artifact paths
