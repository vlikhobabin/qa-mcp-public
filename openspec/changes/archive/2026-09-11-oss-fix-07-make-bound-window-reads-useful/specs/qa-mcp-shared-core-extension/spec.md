## ADDED Requirements

### Requirement: Bound active-window reads expose a useful safe observation
Bound read_active_window through the default handler MUST derive its public
observation from actual ActiveWindowContext data. Its value MUST contain the
fixed window_state and exact bounded marker_count without raw window references,
markers, captions or physical paths. A successful read MUST NOT reduce to an
unconditional empty object.

#### Scenario: Actual window observation states are distinguishable
- **WHEN** a well-formed actual active-window DTO has a nonempty reference present in its marker list, no reference and no markers, or another unresolved reference/marker combination
- **THEN** its safe state is respectively observed, missing or ambiguous, with the exact marker count
- **AND** these are DTO observation states, without a new protocol uniqueness claim.

#### Scenario: An unsuccessful or malformed native observation is returned
- **WHEN** the actual default handler receives unsuccessful base status or malformed reference/marker types
- **THEN** the bound operation produces a fixed non-success result rather than fabricating a successful observed window.

### Requirement: Expected-window predicates are evaluated against internal window data
An explicitly requested bound window predicate MUST be evaluated against the
internal reference/markers before public redaction. Only a safe boolean outcome
may cross the public boundary; neither expected text nor raw observation data
MUST be echoed. Missing or ambiguous observation and invalid/empty expectations
MUST NOT become passing window assertions.

#### Scenario: Match and mismatch use the actual read
- **WHEN** an expected substring matches an observed window reference/marker or does not match it
- **THEN** the public assertion outcome is respectively true or false
- **AND** text occurring only in capture metadata, credentials or the public result envelope does not produce a match.
