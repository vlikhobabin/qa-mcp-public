## Context

After OSS-04D the common boundary can validate identity, but lifecycle tools do
not yet create a target-bound attachment/session. This payload adds admission
only; exact cleanup and tool-schema closure remain OSS-04F.

## Goals / Non-Goals

**Goals:**
- Use only the frozen provider physical profile for project launch/attach.
- Create immutable session/attachment identity after non-mutating admission.
- Block unavailable, mismatched and override cases before side effects.
- Validate required raw remote identity without filling missing members from
  configured defaults or accepting aliases.

**Non-Goals:**
- Add evidence artifact routing or exact-owned cleanup.
- Change existing protocol frames/templates.
- Perform the final live certification.

## Decisions

1. Resolve file/client-server and platform values only from the provider env;
   process/default fallback is ignored in project mode.
2. Store target, session, generation, ownership class and lifecycle handle in
   attachment state after readiness succeeds.
3. Require host-agent target observation for remote attach; endpoint
   reachability alone is insufficient.
4. Return typed blocked lifecycle results rather than throwing secret-bearing
   platform/connection errors.
5. For a project-bound owned remote launch, validate the unmodified host-agent
   payload first. Top-level launch, `client_target` and `lifecycle_handle` each
   carry a positive integer PID and TPort plus the same explicit lifecycle id.
   `bool`, string, zero, missing and alias-only members are invalid; no default
   port or `id` alias may make an incomplete `client_target` admissible.
6. Normalize or retain a remote target only after raw identity admission. Any
   failure returns a typed blocked result and leaves application session and
   attachment empty, before relay/protocol probing.

## Risks / Trade-offs

- [Legacy callers pass explicit target arguments] → Project mode blocks them;
  unbound standalone keeps existing behavior.
- [Admission succeeds but later cleanup is not yet target-aware] → This card
  does not expose project cleanup as complete; OSS-04F follows immediately.
- [Python treats `bool` as `int`] → Raw PID/port validation uses exact integer
  type and positive-value checks, with explicit boolean adversarial tests.
- [Host-agent compatibility aliases hide missing identity] → Aliases remain
  available to unbound compatibility paths only; bound admission requires the
  canonical raw fields.

## Verification Strategy

- No capture source, protocol frame range, dynamic wire field or replay change
  is involved; existing host-agent response objects are exercised offline.
- Test-first adversarial matrices cover missing, zero, boolean and string PID
  or port, missing/blank/alias-only lifecycle identity and disagreement among
  all three raw identity projections. Every negative case asserts no session,
  attachment or downstream endpoint probe.
- Linux focused/full gates are followed by an exact-source wheel check on the
  authorized architect workstation. The Windows harness monkeypatches process
  launch/attach and therefore creates no 1C process; only the owned staging
  directory and its venv are removed, followed by read-only inventory.

## Migration Plan

Enable project admission only when a resolution is composed. Rollback starts an
explicitly unbound application, never an in-place rebind.

## Open Questions

- None. Existing reviewed protocol mappings are reused without capture changes.
