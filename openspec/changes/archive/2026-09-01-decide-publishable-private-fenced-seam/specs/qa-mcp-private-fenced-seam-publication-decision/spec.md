## ADDED Requirements

### Requirement: Offline clean-versus-dirty seam boundary reconstruction
The decision SHALL reconstruct the private fenced S4 seam dependency boundary
from published artifacts, local clean-HEAD/current-diff source analysis and
retained privacy-safe I4 composition evidence only. It SHALL identify the
required source predicates, ownership and call relationships, clean-HEAD
absences, dirty-candidate dependencies and standalone composition failure
without changing production or test source.

#### Scenario: Boundary is reproducible without target access
- **WHEN** an independent reviewer follows the published source predicates from clean HEAD and compares them with the protected dirty candidate
- **THEN** the reviewer can reproduce which seam dependencies are absent from HEAD and why wired or dormant I4 composition is not currently publishable without launching 1C, connecting to an endpoint or accessing a retained target identity

### Requirement: Exactly one bounded publication decision
The decision SHALL publish exactly one of two mutually exclusive outcomes.
Outcome A SHALL authorize at most one minimal separately reviewable private
seam extraction/composition relative to clean HEAD and SHALL state exact owned
paths or source predicates, dependency ceiling, hostile verification floor,
rollback and fail-closed staging. Outcome B SHALL conclude that no bounded
extraction is valid and SHALL require architectural redesign and supersession
of I4.

#### Scenario: Bounded extraction is valid
- **WHEN** the offline boundary proves that one behavior-neutral seam can be isolated from clean HEAD with no protected predecessor byte and can be compiled and hostile-verified independently
- **THEN** the decision records Outcome A with all ownership, ceiling, verification, rollback and staging constraints and no implementation authority

#### Scenario: Bounded extraction is not valid
- **WHEN** any required seam behavior remains inseparable from protected predecessor bytes or cannot be independently compiled and hostile-verified
- **THEN** the decision records Outcome B, requires architectural redesign/supersession of I4 and authorizes no extraction

### Requirement: Published Outcome A authorizes one clean-base seam card
The published decision SHALL authorize exactly one later separately accepted
private seam card relative to clean published HEAD. The card SHALL own only the
seven paths and named predicates in the curated decision, SHALL change no more
than three non-test and four test Go paths with at most 250 added non-test Go
lines, and SHALL add no package, dependency, public caller, route, wire field,
marker derivation or unrelated predecessor behavior.

#### Scenario: Clean-HEAD consumer is composed
- **WHEN** the future card replaces exactly the two direct clean-HEAD inventory call sites with the private fenced wrapper and connects the bounded diagnostic closure
- **THEN** its exact staged tree compiles and the connected hostile oracle observes both real worker boundaries
- **AND** no dirty whole-file byte or unowned hunk enters the staged tree

#### Scenario: Seam ceiling or oracle fails
- **WHEN** an extra path or predicate is required, a direct inventory bypass remains, the diagnostic is dormant, the exact staged tree does not compile or any hostile row fails
- **THEN** delivery stops without publishing or importing predecessor bytes
- **AND** a new architectural investigation is required

#### Scenario: I4 is reconsidered
- **WHEN** the seam card has received independent review and publication
- **THEN** I4 may be replanned against that published seam commit in a separate session
- **AND** the current dirty I4 payload remains excluded and conveys no pre-composed authority

### Requirement: Protected payload and authority remain closed
The decision SHALL preserve the recorded S4-R1, S7, fixture, OSS-07 and OSS-08
baselines byte-for-byte and SHALL publish only I5 documentation, OpenSpec
artifacts, synced decision specification and minimum lineage metadata. It SHALL
grant no seam, classifier, runtime correction, test payload, live confirmation,
retry, target, Windows mutation, public route or S7 authority.

#### Scenario: Decision payload is reviewed for publication
- **WHEN** I5 reaches its independent review gate
- **THEN** immutable-baseline and manifest-scope evidence proves that no protected or prohibited payload is included and the review metadata classifies I5 as an investigation/design decision rather than another repeated implementation

### Requirement: Evidence remains privacy-safe and offline
The decision SHALL contain only source predicates, bounded hashes, path names
and non-sensitive findings necessary to reproduce the dependency conclusion.
It MUST NOT publish raw runtime evidence, endpoint access, machine/UI dynamic
identity or a claim of new runtime observation.

#### Scenario: Curated findings are inspected
- **WHEN** privacy and forbidden-endpoint checks scan the publishable I5 payload
- **THEN** they find no credential, raw UI value, accessed endpoint or new live-result claim, and any retained machine identity appears only as explicitly inaccessible evidence lineage
