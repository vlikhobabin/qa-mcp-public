# Implement Typed Operation Evidence Boundary

## Status
2.todo

## Owner
qa-mcp

## Series
oss-04d-r3

## Order Index
4034.8

## OpenSpec Stage
blocked / exhausted review lineage

## Parent Epic
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Source Lineage
- Latest safe published implementation reference:
  `bf66ce87425827739db5bcc20746d650a988138f`.
- OSS-04D and OSS-04D-R1 are unpublished exhausted evidence lineages, not
  implementation baselines.
- Production code SHALL be implemented from the published baseline and the
  reviewed OSS-04D-R2 design. Only evidence-backed tests may be selectively
  recovered: the R1 stash matches its final tree, while the older OSS-04D
  stash is a checkpoint and is not the final reviewed payload.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload.md","authorization_id":"oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload"}`

## Goal
Implement the reviewed typed operation-evidence and route-admission boundary,
then publish it only after complete adversarial proof and fresh independent GO.

## Acceptance
- Public results reconstruct exact DTOs from validated core provenance and
  bounded executor content; executor provenance and arbitrary callbacks are not
  trusted.
- Field classification is anchored and preserves declared benign controls while
  removing credential/connection aliases across supported case and separators.
- Documentation URLs use structured parsing/address classification, reject
  userinfo and every non-public route class, and preserve registered public
  aliases canonically.
- Strict-IP parse failures matching the bounded legacy numeric-host grammar
  (`127.1`, `0177.0.0.1`, `0x7f.1` and equivalent one-to-four-component
  forms) are rejected before DNS admission, with canonical global-IP and
  alphabetic public-host controls preserved.
- Direct/bound artifacts, every error scalar and exceptional object/mapping
  path are total, bounded and secret-safe; `full_local` remains sealed and
  root-contained.
- Route admission blocks foreign and asymmetric bound states before Local or
  Windows adapters while preserving true pre-session and unbound compatibility.
- MCP and scenario paths carry one trusted identity and taxonomy for all verdict
  classes.
- Production additions are at most `500`, introduce no new authority or wire
  protocol, and match the exact published authorization source.

## Scope
- Shared-core public DTO serialization, operation route admission and focused
  MCP/scenario adapters required by the reviewed design.
- Test-first adversarial matrix and exact-source Windows offline executor proof.
- No OSS-04E lifecycle implementation, resolver authority, new evidence policy,
  protocol capture or live 1C mutation.

## Change Set
1. `implement-typed-qa-mcp-operation-evidence-boundary` -
   `openspec/changes/implement-typed-qa-mcp-operation-evidence-boundary/`

## Depends On
- [OSS-04D-R2 investigation](../4.done/oss-04d-r2-investigate-operation-evidence-sanitization-boundary.md)
  is published.
- [OSS-04D-A1 authorization](../4.done/oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload.md)
  is published and linked here.
- `oss-04d-r2-investigate-operation-evidence-sanitization-boundary`
- `oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload`

## Verify
- Exact RED evidence for every design-matrix hostile/control class.
- Operation identity, shared-core, runtime-target, MCP and scenario focused tests.
- Full non-live CI/coverage, compilation, strict OpenSpec, diff/manifest scope
  and public-surface checks.
- Exact-source Windows offline Local/Windows executor proof with pre/post
  process/listener/staging identity and owned cleanup only.
- Fresh independent review; prior OSS-04D/R1 verdicts cannot authorize publish.

## Result
The unpublished R3 implementation exhausted review rescue budget `2/2` and is
retained only as exact stash lineage. Its first R4 design investigation also
exhausted review with one remaining matrix-exactness blocker. The linked
OSS-04D-R4-R1 design replacement is now the only allowed continuation.

## Next
- Do not redeliver or publish R3.
- Continue with
  [OSS-04D-R4-R1](../4.done/oss-04d-r4-r1-replace-exhausted-boundary-investigation.md).

## Change 1: `implement-typed-qa-mcp-operation-evidence-boundary`

### Why
The two failed lineages proved that a generic recursive regex/token sanitizer
cannot satisfy the closed public boundary.

### Goal
Implement the reviewed DTO, field/URL, artifact/error and route decisions as one
bounded independently reviewed capability.

### Scope
- Implement only the exact OSS-04D-R2 decisions and adversarial matrix.
- Rebuild from the safe published baseline; do not restore failed production
  code wholesale.
- Keep downstream lifecycle admission in OSS-04E.

### Acceptance
- All card acceptance and design-matrix rows have test-first hostile and safe
  controls.
- Deterministic preflight validates the exact published authorization.
- Fresh independent review returns GO before publish.

### Depends On
- `oss-04d-r2-investigate-operation-evidence-sanitization-boundary`
- `oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload`

### Related
- `openspec/changes/implement-typed-qa-mcp-operation-evidence-boundary/`

## Log
- 2026-08-25 created by OSS-04D-R2 as the only authorized runtime successor;
  delivery remains blocked pending investigation and authorization publication.
- 2026-08-25 OSS-04D-A1 published the exact 500-line/no-authority authorization
  source; R3 is the next sequential card.
- 2026-08-25 R3 ended cycle 3 `NO-GO` at rescue `2/2`; R4 then designed a
  smaller split but also exhausted review on one exact URL-matrix handoff.
  OSS-04D-R4-R1 is the mandatory design replacement before runtime resumes.
