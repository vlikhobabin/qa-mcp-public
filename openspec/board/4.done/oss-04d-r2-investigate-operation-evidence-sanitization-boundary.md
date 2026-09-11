# Investigate Operation Evidence Sanitization Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-04d-r2

## Order Index
4034.75

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Investigation For
- `openspec/board/2.todo/oss-04d-propagate-target-session-operation-identity.md`
- Unpublished linked replacement `oss-04d-r1-replace-operation-identity-after-exhausted-review`.

## Source Lineage
- Latest safe published reference: `bf66ce87425827739db5bcc20746d650a988138f`.
- OSS-04D and OSS-04D-R1 each ended with a fresh `NO-GO` after two
  same-card rescues; both histories record rescue budget `2/2`, remaining `0`,
  exhausted `true`.
- `oss04d-r1-exhausted-review-payload-20260825` reconstructs the exact R1
  final tree. The older `oss04-oversized-review-payload-20260825` stash
  reconstructs checkpoint tree `48256182c050da7315caa01c71b94f4ecd34725f`,
  not the final reviewed OSS-04D tree; exact recovery of that final source tree
  is not claimed or required. Neither stash may be published or reapplied as
  an implementation shortcut.
- Canonical ignored verdict/history and bounded evidence remain under
  `.runtime/changerail/{reviews,evidence}/` for both source ids.

## Published Investigation Authorization
none

## Goal
Replace the repeated heuristic sanitizer patch staircase with one reviewed,
typed and bounded operation-evidence boundary design before any further
operation-identity implementation rescue.

## Acceptance
- A durable investigation document traces every final OSS-04D and OSS-04D-R1
  finding to a root cause, invariant and explicit architectural decision.
- The design separates core-trusted provenance from executor-controlled value,
  error and artifact content; it defines typed serialization, exception
  containment and `sanitized` versus sealed `full_local` behavior without
  relying on open-ended substring matching.
- URL handling uses structured parsing and address classification, rejects
  userinfo and non-public routes, and preserves only explicitly admitted public
  documentation fields without over-redacting benign metadata.
- A bounded adversarial verification matrix covers direct and bound artifacts,
  every error scalar and exceptional mapping/object path, key aliases and
  controls, IPv4/IPv6 routes, provenance, routing and unbound compatibility.
- The investigation creates an ordered successor implementation card and, if
  complexity or repeated-defect policy requires it, a separate exact bounded
  authorization card; OSS-04E remains blocked until that successor publishes.
- This card changes no production runtime code, does not reapply either failed
  payload and does not claim Windows/runtime behavior from design-only proof.

## Scope
- Investigation/design documentation, OpenSpec artifacts and board lineage.
- Read-only analysis of retained diffs, verdicts, histories, tests and evidence.
- No `src/`, runtime adapter, resolver, lifecycle or protocol implementation.
- No live 1C, TestClient, Docker, host-agent or Windows mutation.

## Change Set
1. `investigate-qa-mcp-operation-evidence-sanitization-boundary` -
   `openspec/changes/investigate-qa-mcp-operation-evidence-sanitization-boundary/`

## Dependencies
- [OSS-04C](../4.done/oss-04c-compose-project-target-readiness.md) is published.
- Both failed operation-identity lineages have fresh retained `NO-GO` evidence.

## Blocks
- [OSS-04D-R3](../2.todo/oss-04d-r3-implement-typed-operation-evidence-boundary.md)
- `oss-04d-r3-implement-typed-operation-evidence-boundary`

## Verify
- Retained evidence index: `.runtime/changerail/evidence/oss-04d-r2-investigate-operation-evidence-sanitization-boundary/index.json`.
- Evidence structure/hash/link/stash audit: passed (`2` exhausted lineages,
  `1` exact-final stash plus `1` explicitly mapped older checkpoint, `2`
  successor links, design-only scope and `0` production paths).
- `bin/openspec validate qa-mcp-operation-evidence-boundary-design --strict`:
  passed.
- `bin/openspec validate --all --strict`: `32 passed, 0 failed` before
  archive.
- `git diff --check`: passed.
- Test-first/Windows-native/live-1C verification: not applicable because this
  payload changes no runtime code or behavior and performs no external action.
- Fresh independent ChangeRail design review cycle 3: `GO`, `6/6` acceptance,
  `0` findings and `0` unbacked claims; exact tree/fingerprint freshness passed.

## Result
The two exhausted unpublished lineages were reduced to five root-cause classes
and eight closed design decisions. The durable design separates core-trusted
provenance from hostile executor content, requires total typed DTO
reconstruction, structured field/URL admission, sealed contained `full_local`
artifacts and route admission before adapter invocation. It defines an
eight-surface adversarial matrix and creates the only permitted continuation:
OSS-04D-A1 exact authorization followed by OSS-04D-R3 typed implementation,
with a `500` production-LOC ceiling and no new authority or wire protocol.
The design capability is synced and the change is archived at
`openspec/changes/archive/2026-08-25-investigate-qa-mcp-operation-evidence-sanitization-boundary/`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-qa-mcp-operation-evidence-sanitization-boundary`

### Why
Two linked implementation lineages repeated the same sanitizer defect class,
reached their rescue limits and filled the original `300`-LOC ceiling without
establishing a closed public serialization boundary.

### Goal
Produce the reviewed design, verification matrix and exact successor handoff
needed to restart implementation without another regex/alias patch staircase.

### Scope
- Inventory both exhausted payloads and classify their root causes.
- Specify trusted/untrusted data ownership and typed public serialization.
- Specify field, URL, artifact, error and exceptional-value admission rules.
- Define bounded successor scope, verification floors and authorization needs.
- Update the source, parent and downstream board handoff.

### Acceptance
- The design resolves every final finding without prescribing another
  open-ended denylist patch.
- Safe controls and fail-closed hostile cases are explicit and independently
  testable.
- The successor is implementable as a separate reviewable payload.
- No production implementation is included in this change.

### Depends On
- OSS-04D cycle-3 `NO-GO` and OSS-04D-R1 cycle-3 `NO-GO`.

### Related
- `openspec/changes/investigate-qa-mcp-operation-evidence-sanitization-boundary/`

## Log
- 2026-08-25 created with operator authorization after OSS-04D-R1 cycle 3
  returned two blockers and one major at rescue budget `2/2` and `300/300`
  production LOC.
- 2026-08-25 fast-forward produced one design-only apply-ready change with a
  typed boundary decision, adversarial matrix and separate authorization plus
  implementation successor handoff.
- 2026-08-25 completed the design-only payload, retained exact lineage and
  stash evidence, synced the new design capability, passed strict OpenSpec and
  diff gates, and archived the change for independent review. No production,
  Windows, live 1C, Docker or host-agent action was performed.
- 2026-08-25 review cycle 1 returned `NO-GO`: the older OSS-04D stash was
  incorrectly described as its final tree, and compact numeric IPv4 could
  fall through strict IP parsing into DNS admission. Rescue 1 corrected the
  recovery mapping and added a bounded legacy-numeric host rejection rule with
  explicit safe controls.
- 2026-08-25T16:12:37Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
