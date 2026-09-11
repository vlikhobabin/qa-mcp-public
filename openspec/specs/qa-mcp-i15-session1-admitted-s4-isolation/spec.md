# I15 Session-1-Admitted S4 Isolation

## Purpose

Define the bounded evidence-decision contract for one original-route Session-1 admission canary and its conditional one-attempt S4 isolation, exact cleanup and non-certifying outcome.

## Requirements

### Requirement: I15 preserves the exact authorized source and contour
I15 MUST bind all evidence to the unchanged five published-I11 blobs and the
same separately operator-authorized host, principal, Session-0 controller,
interactive Session-1 route, platform, target, candidate, configuration,
run-1 fixture and S4 argv identity used by the I13/I14 lineage. It MUST NOT
provision, restore, unlock, rebind, administer or substitute any contour or
input surface.

#### Scenario: Every identity and initial state matches
- **WHEN** all source/input/runtime identities match and the exact-owned surface
  plus typed job/desktop/transport state is initially zero
- **THEN** I15 may proceed to its one typed Session-1 canary.

#### Scenario: Any identity or initial state differs
- **WHEN** an identity differs, required initial evidence is missing or owned
  state is already present
- **THEN** I15 stops fail-closed without repair, substitution or candidate
  invocation.

### Requirement: Typed Session-1 admission gates candidate invocation
I15 SHALL run exactly one typed Session-1 canary on the original started route
and MUST invoke no candidate unless the receipt proves the exact host,
principal and Session 1. A missing, late or mismatched receipt SHALL produce a
`NOT-VERIFIABLE` or `BLOCKED` decision with candidate invocation count zero and
the exact successful-admission resume condition.

#### Scenario: Canary succeeds
- **WHEN** the one bounded canary produces its matching typed Session-1 receipt
- **THEN** I15 may proceed to one exact-source S4 isolation.

#### Scenario: Canary does not succeed
- **WHEN** the receipt is missing, late or mismatched
- **THEN** I15 invokes no candidate, performs exact cleanup and stops without
  retry or authority widening.

### Requirement: S4 isolation is singular bounded and non-certifying
After successful admission, I15 SHALL invoke the exact-source tracked run-1 S4
candidate at most once and retain only a closed stage/class, hashes, counts,
booleans, receipt presence, exit code and duration. It MUST retain no raw UI,
output, screenshot, credential, connection string, broad dump or task name and
MUST NOT claim or complete I13 certification.

#### Scenario: Candidate reaches a typed terminal receipt
- **WHEN** the single admitted candidate produces a typed observation or
  bounded terminal receipt
- **THEN** the decision records its closed result as isolation evidence only.

#### Scenario: Candidate exits before its receipt
- **WHEN** the typed pre-invocation marker exists but the candidate exits before
  its own receipt
- **THEN** the decision records the closed pre-receipt outcome and one proven
  invocation without starting another attempt or I13 row.

### Requirement: Started-route topology attribution never mutates foreign state
I15 MUST compare privacy-safe hashes/counts of the protected task set before,
during and after the original started route and SHALL correlate a bounded
scheduler-event projection when available. It MUST classify harness/start
behavior, independent drift or ownership violation only when the bounded
evidence distinguishes that class; otherwise it MUST retain
`NOT-VERIFIABLE` and infer no cause. It MUST NOT expose, select or mutate a
foreign task.

#### Scenario: Bounded evidence distinguishes the change
- **WHEN** protected-set hashes and scheduler attribution bind a topology change
  either to the owned start lifecycle or to an independently timed foreign
  event
- **THEN** I15 records the corresponding harness/start or independent-drift
  class without foreign mutation.

#### Scenario: Attribution remains ambiguous
- **WHEN** the event projection is unavailable or cannot distinguish owned
  start behavior from external drift
- **THEN** I15 retains `NOT-VERIFIABLE`, records only directly proven
  exclusions and infers no topology cause.

#### Scenario: Owned action targets foreign state
- **WHEN** any I15 action or cleanup selects a non-I15 task or process
- **THEN** I15 records an ownership violation and blocks completion.

### Requirement: Exact before-image restoration and double cleanup gate the decision
I15 MUST retain the initial configuration content, ACL, creation, write,
access and attributes before-image plus typed task/stage/process/job/desktop/
transport zero-state. It MUST restore that exact state, remove only exact-owned
state and prove a repeated cleanup performs no work. Any foreign target,
residual owned state, missing continuity evidence or nonzero 1C process residue
SHALL block completion.

#### Scenario: Cleanup is exact and rerun-safe
- **WHEN** configuration matches every initial field, exact-owned and 1C residue
  is zero and the second cleanup reports zero removals
- **THEN** cleanup acceptance passes for either canary-only or canary-plus-S4
  outcome.

#### Scenario: Cleanup is incomplete foreign or unproven
- **WHEN** a before-image differs, required initial state was not retained,
  owned residue remains or a foreign target was selected
- **THEN** I15 stops fail-closed and is not eligible for publication.

### Requirement: The retained decision enters fresh critical review
I15 MUST retain bounded schema-valid decision/findings and typed evidence,
preserve Apache-2.0 without changing license paths, pass focused/full offline
Go and vet, deterministic unexecuted cross-build, strict OpenSpec, manifest,
public-surface and whitespace gates, and obtain a fresh critical review before
publication. The decision MUST leave I13 active, unarchived and uncertified.

#### Scenario: Review handoff is complete
- **WHEN** the live decision, exact cleanup and every mandatory offline/workflow
  gate are bound to the reviewed payload
- **THEN** a fresh independent critical/xhigh reviewer may issue the payload
  verdict.
