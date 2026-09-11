## Context

Published commit `312e91453026cf808e6d48b521c971eb11e7ef96`
contains the independently reviewed S1-R1 through S6 foundations: hidden
desktop/process ownership, one long-lived worker, window isolation, passive
main/prompt observation, minimal addressed prompt action, typed cross-language
receipt validation and a single-use exact cleanup lease. None has a production
caller or public capability.

The pre-stable `open_external_processor` compatibility tool still exposes
display, coordinates and timing and uses chooser/OCR/global display input. It
cannot be the stable project-bound Windows route. A dirty historical I1
combined candidate exists in the shared worktree, but its payload is explicitly
non-publishable and cannot be used as the S7 baseline.

This change touches the Windows bridge integration, Python operation/MCP
composition, profile schema, tests, OpenSpec and retained runtime evidence. It
does not change protocol frame templates or claims, so capture sources, frame
ranges and replay are not applicable. Dynamic runtime values are reduced to
typed hashes, bounded counts, PIDs, port and opaque lifecycle identity. Final
certification uses fresh exact-source Windows execution rather than capture
replay.

## Goals / Non-Goals

**Goals:**

- Compose the published S1-S6 modules through bounded integration files while
  keeping every certified foundation file byte-identical.
- Add one backward-compatible capability to the existing authenticated bridge
  launch/stop API and admit only an absolute EPF/ERF path plus lowercase
  SHA-256 marker.
- Replace the pre-stable tool schema with logical path/expected-caption input,
  bind it to the immutable project target, and derive Windows success only from
  the exact typed receipt.
- Make cleanup single-use and exact-owned on success, refusal, timeout and
  callback failure, with privacy-safe public results and retained evidence.
- Stay within the published S7 ceiling of `500` physical added production lines
  relative to `312e914...`, without deletion offsets.

**Non-Goals:**

- No chooser, OCR/coordinate, mouse, `SendInput`, foreground takeover,
  `SwitchDesktop`, generic command execution or arbitrary desktop input.
- No edits to S1-S6 source/tests, no reuse of the dirty combined I1 payload and
  no resurrection of exhausted OSS-06/S5 implementations.
- No new endpoint, API-major change, raw protocol capture, protocol template,
  infobase creation, target substitution or evidence-policy override.
- No Runtime Proxy/RPW, Relay, Team, live-mcp, downstream AI for 1C, OSS-07,
  release automation or stable cutover work.

## Decisions

### 1. Build from a clean published-S6 composition

Implementation and verification use `312e914...` plus only S7-owned paths.
The delivery manifest records exact predecessor hashes and rejects any S1-S6
change. This is chosen over editing the shared dirty candidate because that
candidate combines failed/historical lineages and cannot prove the authorized
`<=500` S7 payload.

### 2. Extend the existing authenticated launch/stop surface

The bridge advertises `testclient-hidden-desktop-direct-execute` in the current
capability document. The existing launch request receives an optional closed
direct-execute object containing only the absolute EPF/ERF path and marker; the
existing stop request retains exact PID/port/lifecycle/handle validation. A new
generic execution endpoint was rejected because it would widen authority and
break the standalone bridge boundary.

### 3. Compose S1-S6 behind one adapter and one closed receipt

A small bridge adapter starts the S1/S2 lifecycle, invokes S3/S4 observation,
uses S5-R1 only for an admitted fresh prompt, and binds the outcome through S6.
It returns no OS handles or UI content. Prompt-free and prompt-confirmed success
remain distinct typed statuses; every partial or ambiguous state is failure.
Copying foundation logic into the integration was rejected because it would
evade predecessor-byte and independent-review guarantees.

### 4. Make Python admission independent and fail closed

Python checks capability/version, immutable project target/session/generation,
logical path policy, expected-caption marker and the full S6 envelope against
independently supplied current-run cleanup identity. Only then can it construct
the public `form_opened` result and single-use cleanup lease. Loose bridge
booleans, caption text or receipt-provided cleanup selection never authorize
success or stop.

### 5. Tighten the pre-stable MCP schema at the stable gate

The public name stays `open_external_processor`, but its model-visible input is
only logical path plus optional expected caption. Display, endpoint,
coordinates, timing, evidence root/policy and cleanup handles are removed.
This deliberate pre-stable schema break is preferred to retaining model-
controlled physical authority. The stable standalone profile includes the tool
only for an admitted project target and compatible bridge; capability absence
fails before launch and never falls back to the old route.

### 6. Certify final bytes, not historical evidence

Offline hostile tests precede implementation. Final proof rebuilds the exact
host executable and Python artifact from the review candidate, then runs
prompt-off, two distinct fresh prompt-on/recovery fixtures, capability-absent
and malformed receipt/cleanup cases, and Python-to-MCP execution on authorized
Windows `8.3.27.2214`. Evidence retains hashes, counts, stages and cleanup
inventories only. Existing historical evidence informs tests but cannot satisfy
the final gate.

## Risks / Trade-offs

- [The `500`-LOC ceiling may be too small for a safe adapter] → Count physical
  production additions continuously; stop for a new governance decision rather
  than compress validation or copy combined code.
- [Capability advertisement could outrun handler readiness] → One contract test
  binds the advertised token, accepted request fields and closed receipt; any
  missing component removes/refuses the capability before process creation.
- [Cleanup could target stale or foreign state] → Recompute the S6 binding from
  caller-owned current-run identity and consume one atomic lease before the
  exact stop callback; callback failure remains consumed.
- [The old compatibility schema has callers] → Treat the change as an explicit
  pre-stable migration, retain the tool name and document removed physical
  controls; do not provide a hidden fallback.
- [Shared dirty files overlap future integration paths] → Deliver in a clean
  composition/worktree and publish only the deterministic S7 manifest; never
  stash, discard or stage the historical payload by implication.

## Migration Plan

1. Establish hostile RED tests and the exact `312e914...` predecessor/LOC
   manifest in a clean composition.
2. Add the bridge adapter/capability and Python route/profile integration behind
   fail-closed capability negotiation.
3. Pass offline Go/Python, schema, cross-build, privacy and clean-composition
   gates without modifying S1-S6.
4. Run the final exact-source Windows matrix after runtime preflight, restore
   configuration and remove only exact run-owned resources.
5. Move the card to authorization-bound `3.inprogress`, sync/archive the change
   and obtain a fresh critical `GO` before scoped publication.

Rollback removes S7 integration/profile admission and returns to published S6,
where every foundation remains dormant and `open_external_processor` is omitted
from the stable route. No data migration is required.

## Open Questions

- None for planning. If delivery cannot preserve the exact S1-S6 bytes,
  `<=500` ceiling, existing authenticated endpoint or closed receipt, it must
  stop rather than select another architecture under this authorization.
