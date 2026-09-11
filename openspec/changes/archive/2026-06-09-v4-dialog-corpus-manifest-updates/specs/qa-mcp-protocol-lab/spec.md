## ADDED Requirements

### Requirement: V4 corpus rows use a fail-closed manifest shape
The protocol lab SHALL define every V4 dialog, expected-error and bounded-wait
candidate through a reviewed manifest row before capture or evidence
publication.

#### Scenario: V4 manifest row is complete
- **WHEN** a V4 manifest row includes scenario family, target marker, expected
  text or diagnostic marker, pre-state, action, result expectation, recovery
  expectation, `mutates_business_data=false` and expected result markers
- **THEN** tooling or reviewers can route the row to the matching V4 scenario
  family
- **AND** the row remains candidate until replay/probe or typed contract proof
  satisfies the evidence gate

#### Scenario: V4 manifest row is incomplete
- **WHEN** a V4 manifest row lacks required common fields or required
  family-specific fields such as bounded wait duration or expected diagnostic
  marker
- **THEN** the row fails closed before capture or publication

### Requirement: V4 evidence separates expected errors from infrastructure failures
The protocol lab SHALL publish V4 expected-error evidence with result markers
that distinguish reviewed expected diagnostics from infrastructure failures.

#### Scenario: Expected diagnostic is published
- **WHEN** a V4 expected-error row produces the reviewed diagnostic marker
- **THEN** the compact evidence records the diagnostic marker, recovery result
  and non-business safety classification
- **AND** accepted status still depends on replay/probe or typed contract proof

#### Scenario: Infrastructure failure remains separate
- **WHEN** a V4 run fails without the reviewed expected diagnostic marker
- **THEN** the compact evidence records an infrastructure failure, rejected or
  blocked reason
- **AND** the row is not promoted as an expected-error protocol claim

### Requirement: V4 runtime artifacts stay outside reviewed git
The protocol lab SHALL keep raw V4 captures, platform logs and generated
replay payloads under ignored runtime paths while retaining compact reviewed
evidence links.

#### Scenario: V4 evidence is published compactly
- **WHEN** a V4 proof bundle is retained
- **THEN** reviewed Markdown or JSON summaries link frame ranges, markers,
  normalized hashes and recovery results
- **AND** raw capture payloads remain outside committed documentation
