## Context

OSS-05 is implemented and archived with `170` added production LOC measured by
deterministic preflight and a separate card gate of `231 <= 300` across its
declared production surface. It adds a versioned authenticated capability
handshake for the independently built Windows bridge while narrowing the
executable to existing TestClient lifecycle/relay and bounded desktop routes.

The payload passed exact Windows certification, but review preflight stopped
before any model launch because `New authority or wire protocol: yes` requires
a tracked published investigation and authorization source. This decision
changes only ChangeRail/OpenSpec metadata and makes no runtime claim.

## Goals / Non-Goals

**Goals:**

- name exactly one OSS-05 successor and canonical review path;
- authorize public bridge API major `1` and only its archived bounded surface;
- retain OSS-05's independent `300`-LOC production cap;
- use the minimum valid ChangeRail authorization ceiling `301`;
- require a separate exact authorization card before OSS-05 review resumes.

**Non-Goals:**

- change or re-run the OSS-05 implementation;
- authorize a second API major, endpoint family or successor;
- authorize COM, BSL, agent completion, Team/onboarding or generic execution;
- start OSS-06 or alter its dependency decision;
- perform Windows, live 1C, Docker or external actions.

## Decisions

### 1. Bind the decision to one exact successor

The investigation SHALL block only
`oss-05-extract-independent-open-windows-host-bridge` at
`openspec/board/3.inprogress/oss-05-extract-independent-open-windows-host-bridge.md`.
The later authorization source must repeat this exact id/path and reference
this investigation from tracked `4.done` state.

### 2. Bound the permitted wire contract

The decision permits `qa-mcp.windows-host-bridge` API major `1` only. Its
allowed surface is the authenticated `/v1/capabilities` handshake plus the
already archived TestClient lifecycle/status/stop/relay, window, bounded input,
screenshot and UIA primitives. Removed private product routes remain forbidden.

### 3. Separate machine recognition from implementation budget

The authorization source SHALL use `production_loc_ceiling: 301`, the minimum
value accepted by ChangeRail for a bounded exception. OSS-05 independently
retains its `<=300` added production LOC acceptance gate; this investigation
does not authorize a 301st production line.

### 4. Fail closed outside the exact chain

The authorization flag may be `allow_new_authority_or_wire_protocol: true`
only for this successor. Any changed id/path, another successor, absent
published source, ceiling above `301` or broader route family invalidates the
decision.

## Risks / Trade-offs

- [Risk] The decision is mistaken for a reusable waiver. → Exact successor
  id/path and separate published source are mandatory.
- [Risk] The machine ceiling expands implementation. → OSS-05 retains the
  independent `300`-LOC card gate.
- [Risk] Removed private routes return through the authorization. → The route
  family and explicit non-goals remain closed in card, spec and review.

## Migration Plan

1. Publish this metadata-only investigation in `4.done`.
2. Publish one exact authorization card referencing this investigation and
   the current OSS-05 successor.
3. Update OSS-05's published authorization reference and dependency metadata.
4. Rerun deterministic critical preflight; any mismatch fails closed.

Rollback reverts only the investigation/authorization metadata. OSS-05 then
remains safely blocked before review and publication.

## Open Questions

- None. Any broader API or successor requires a new investigation.
