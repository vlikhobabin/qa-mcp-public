## Context

The fixture source, live capture/probe and classification changes create
reviewed evidence. Publication is deliberately last so docs and mapping notes
do not imply acceptance before the evidence contract is satisfied.

## Goals / Non-Goals

Goals:

- Link all compact fixture evidence from `docs/protocol-research/evidence-index.md`.
- Update corpus runner and protocol package docs to describe fixture-derived
  statuses.
- Promote accepted fixture rows only when classification evidence supports
  them.
- Keep unresolved rows visible with owner route and residual risk.

Non-goals:

- Do not create new fixture evidence during publication.
- Do not accept rows with missing hashes, frame ranges or probe/replay status.
- Do not commit raw runtime output.

## Publication Rules

- Evidence index entries link compact reviewed directories only.
- Accepted mapping docs list capture ids, frame ranges, hashes, probe/replay
  status and evidence paths for accepted rows.
- Pending, partial, unsupported, timeout, rejected or blocked rows remain in
  corpus/comparison notes and are not copied into accepted mapping lists.
- Historical evidence remains immutable; new output gets a new evidence id.

## Safety Constraints

Publication is offline documentation work. If a missing evidence link is found,
delivery must go back to the capture/probe or classification change instead of
fabricating evidence during publication.
