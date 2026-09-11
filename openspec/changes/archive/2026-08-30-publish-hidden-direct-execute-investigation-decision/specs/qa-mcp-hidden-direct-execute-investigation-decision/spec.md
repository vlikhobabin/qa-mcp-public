## ADDED Requirements

### Requirement: Published decision is exact-lineage and non-admitting
The published investigation decision MUST bind its conclusions to the retained
source, executable, wheel, Windows platform, declared target, prompt matrix and
exact-owned cleanup evidence, and MUST NOT change production code, runtime
behavior or stable tool admission.

#### Scenario: Retained direct-execute evidence is summarized
- **WHEN** the documentation-only decision is prepared for review
- **THEN** it identifies the exact sanitized lineage and outcomes without
  retaining credentials, connection strings, UI text or raw screenshots

#### Scenario: Production payload appears in decision scope
- **WHEN** manifest scope-check finds any production path owned by the decision
- **THEN** review is blocked and the decision cannot be published

### Requirement: Chooser and direct routes remain distinctly classified
The decision MUST record the native chooser route as non-admitting and MUST
identify hidden native direct `/Execute` as the only eligible production
direction without treating investigation evidence as final admission.

#### Scenario: Successor planning consumes the decision
- **WHEN** a later foundation or final successor references the decision
- **THEN** it cannot introduce chooser, `SendInput`, physical cursor,
  foreground-takeover or desktop-switch fallback

### Requirement: Bounded successor handoff is exact
The investigation MUST block exactly
`oss-06-s7-admit-hidden-direct-execute-public-route` and MUST require ordinary
foundation successors to remain within `300` added production LOC while the
separately authorized final successor remains within `500`.

#### Scenario: A different successor claims authorization lineage
- **WHEN** path, id, dependency or production ceiling differs from the
  published bounded train
- **THEN** deterministic preflight fails closed and no semantic review starts
