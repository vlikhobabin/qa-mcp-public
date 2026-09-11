## ADDED Requirements

### Requirement: Reconciliation binds the exact published I11 state
The handoff SHALL bind local source, remote branch and every I11 evidence claim
to published commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.

#### Scenario: Published identity is exact
- **WHEN** local `HEAD`, credential-free HTTPS `origin/main`, the I11 done card,
  archive and synced specification resolve to the published I11 state
- **THEN** criterion reconciliation may proceed using those tracked artifacts.

#### Scenario: Published identity differs
- **WHEN** source, remote branch, card status, archive or specification differs
- **THEN** reconciliation fails closed without selecting a successor.

### Requirement: Every parent criterion has one evidence classification
The handoff MUST classify every top-level S4-R1 acceptance criterion as closed
by published offline evidence, still requiring certification evidence or
preserving the downstream block. It MUST NOT treat unexecuted evidence as
passed.

#### Scenario: I11 closes an offline invariant
- **WHEN** an invariant is explicitly proven by I11's tracked card, archive,
  specification or curated public-safe summary
- **THEN** the decision records the exact evidence source and may classify only
  that invariant as closed offline.

#### Scenario: A criterion requires execution or cleanup evidence
- **WHEN** a criterion requires a fresh matrix row, stable marker sample or
  exact cleanup observation absent from I11
- **THEN** the parent remains incomplete and the criterion is assigned to the
  certification successor.

### Requirement: The successor is exact and certification-only
The handoff SHALL prepare one apply-ready I13 successor bound to the published
I11 source, the remaining S3/S4/S5 and cleanup evidence floor, and a fresh
independent review. I13 MUST add no implementation authority.

#### Scenario: Published bytes produce the required evidence
- **WHEN** every exact-source matrix row and cleanup assertion passes against
  the bound I11 source
- **THEN** I13 may record the retained evidence and enter fresh review.

#### Scenario: Evidence is unavailable or behavior differs
- **WHEN** required evidence cannot be produced, source identity drifts, a row
  fails or cleanup is incomplete
- **THEN** I13 stops fail-closed and requires a separately authorized
  investigation rather than changing product code.

### Requirement: Parent and roadmap remain synchronized and blocked
The handoff MUST update the S4-R1 parent and project roadmap to name I13 as the
exact next step and MUST preserve the downstream block until I13 and the
parent are independently reviewed and published.

#### Scenario: Handoff is published
- **WHEN** I12 passes strict graph, scope and documentation checks plus fresh
  independent review
- **THEN** both parent and roadmap identify the same I13 path and neither
  claims S4-R1 completion.

### Requirement: Decision payload remains offline documentation only
I12 MUST modify only documentation and OpenSpec workflow state, preserve
Apache-2.0 and add no product/test behavior, public or wire surface, authority,
runtime configuration or external side effect.

#### Scenario: Offline proof floor passes
- **WHEN** strict OpenSpec, decision schema/graph, exact scope, public-safety,
  license and whitespace checks pass
- **THEN** I12 may enter ordinary review without executing the future
  certification matrix.
