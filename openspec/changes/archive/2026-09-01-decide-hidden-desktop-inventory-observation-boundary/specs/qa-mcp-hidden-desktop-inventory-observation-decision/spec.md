## ADDED Requirements

### Requirement: Retained first-inventory refusal remains unresolved
The decision MUST classify retained
`first_window_inventory/first_window_inventory_failed` as an unresolved
fenced composite boundary unless contemporaneous retained evidence identifies
the exact terminal source. It MUST NOT claim that the child/listener fence
passed or that one desktop API failed from the umbrella value alone.

#### Scenario: Published fence retains the predecessor failure pair
- **WHEN** the consumed confirmation contains the same first-inventory
  stage/failure pair after the liveness-fenced candidate was admitted
- **THEN** the decision records that the source collapses pre-fence,
  inventory and post-fence terminal states into that pair
- **AND** exact liveness, hidden-desktop call execution and API-level cause
  remain unknown.

#### Scenario: Desktop call usability is compared with process liveness
- **WHEN** source proves exact child/listener/job/TPort predicates but carries
  no retained desktop-handle, thread-desktop or window-station predicate
- **THEN** the decision treats desktop inventory usability as a separate
  unobserved invariant
- **AND** neither liveness nor desktop failure is inferred from the other.

### Requirement: One behavior-neutral classifier is the successor ceiling
The decision SHALL authorize exactly one later successor at the existing
private S4 inventory/diagnostic seam. That successor MAY retain one
allowlisted terminal cause but MUST preserve current control flow, Windows call
counts, fail-closed results and passive-UIA admission behavior.

#### Scenario: Existing terminal sources are classified
- **WHEN** a separately accepted successor encounters pre-fence child/listener
  refusal, hidden or operator open/enumeration/overflow failure, isolation
  validation failure, post-fence change, successful empty, main-absent or
  exact-main state
- **THEN** it retains exactly one matching closed-vocabulary cause code at the
  existing first or second boundary
- **AND** it serializes no raw error text or dynamic machine/UI identity.

#### Scenario: Classification would alter observation behavior
- **WHEN** a proposed classifier adds a Windows call, retry, fallback,
  sentinel, wait, desktop-handle transfer, job assignment or admission path
- **THEN** it exceeds this authorization and MUST stop
- **AND** architectural redesign is required before such behavior can be
  considered.

### Requirement: Hostile verification binds the successor
The successor MUST pass one injected offline hostile matrix proving exact
cause projection, privacy, unchanged call counts and unchanged fail-closed
admission. The same matrix MUST first demonstrate that the predecessor
umbrella projection cannot retain the expected cause.

#### Scenario: Every cause branch is injected
- **WHEN** hostile tests inject every allowlisted terminal source plus unknown,
  conflicting and malformed states
- **THEN** each valid source produces exactly one expected cause and every
  invalid state refuses before passive UIA
- **AND** the tests prove hidden/operator call counts and pre/post fence checks
  are unchanged with no retry or fallback.

#### Scenario: Privacy-hostile values are injected
- **WHEN** injected errors and identities contain raw text, endpoint, desktop,
  handle, PID, port or UI-like values
- **THEN** the retained diagnostic contains only its schema, stage, status,
  failure and allowlisted cause code
- **AND** all hostile dynamic values are absent.

### Requirement: Decision grants no implementation or runtime authority
This decision MUST change only its card, OpenSpec artifacts, synced capability
and curated privacy-safe findings. It MUST NOT modify the blocked S4-R1 or
foreign payload, implement the successor, contact a Windows endpoint, launch
1C, access real configuration, consume another confirmation or start S7.

#### Scenario: Decision is delivered for review
- **WHEN** strict offline validation, privacy/endpoint checks, protected-path
  comparison and manifest reconciliation pass
- **THEN** the decision remains documentation-only and independently
  reviewable
- **AND** successor implementation and any future live observation each still
  require separate explicit authority.
