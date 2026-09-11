## Context

The retained OSS-06-I1 production candidate proves a viable hidden native
`/Execute` direction, but its 1,280-line worker file combines process creation,
worker lifecycle, window observation, prompt action and receipt admission. S1
publishes only the lowest layer. The current public host route and wire schema
must remain byte-for-byte behaviorally unchanged while later S2-S7 cards build
on the published primitives.

No protocol capture or frame range is involved. The evidence source is focused
Go behavior plus Windows-native execution of the exact S1 source. Dynamic run
and token values are retained only as opaque hashes; raw values, environment
contents and desktop UI are not evidence.

## Goals / Non-Goals

**Goals:**

- Define bounded opaque run identity and reserved-environment composition.
- Create and close one exact `Winsta0\qa-mcp-*` desktop without activating it.
- Start one exact windowless worker executable on that desktop without
  inheriting handles.
- Make success and every failure path independently testable and exact-owned.
- Keep added production source within the ordinary `300`-line ceiling.

**Non-Goals:**

- No TestClient worker, TPort wait, window inventory, UIA, prompt action,
  direct-execute receipt or public API wiring.
- No arbitrary public process execution and no generic hidden-desktop tool.
- No `SendInput`, cursor movement, foreground takeover or desktop switching.
- No live 1C certification; that is repeated only after S7 integration.

## Decisions

### Separate pure policy from Windows mechanics

Run identity, name validation and environment composition live in a
cross-platform internal file so hostile bounds and secret handling run in the
ordinary Linux suite. Win32 handle and process operations live behind a
Windows build tag. This gives useful offline RED/GREEN coverage without
pretending that Linux proves native calls.

### Bind every desktop to an opaque run identity

The foundation accepts bounded non-empty run and worker-token values, stores
only SHA-256 hashes, and derives the desktop name from the run hash. Desktop
creation accepts only that validated name. Random generation and IPC use are
left to S2, avoiding duplicate ownership authority in S1.

### Keep job ownership in S2

The exact executable is launched with an explicit `STARTUPINFO.lpDesktop`, a
Unicode environment, `CREATE_NO_WINDOW` and no inherited handles. S1 returns
the exact process handle/PID to its caller and closes the transient thread
handle. It does not create or assign a job: authenticated worker rendezvous,
child job ownership and listener handoff are one coherent S2 lifecycle.

Alternatives rejected: shell/task launch loses the exact desktop/process
boundary; premature job/child ownership duplicates S2; activating the desktop
or using global input violates the published investigation decision.

### Keep the foundation dormant

The new functions are unexported and no existing non-test caller is changed.
S1 tests may invoke them directly, while S2 must be a separately reviewed card
before any worker lifecycle consumes them. No existing route, feature flag,
capability document or HTTP handler is modified.

## Risks / Trade-offs

- [A Windows API regression is hidden by Linux tests] -> Require Windows
  cross-build plus a native focused test that creates/closes the desktop and
  launches the test child on that exact desktop.
- [Raw run identity or inherited internal variables leak] -> Retain only hashes
  and test case-insensitive stripping of all reserved inherited keys.
- [Failure cleanup touches foreign work] -> Cleanup is limited to current-call
  handles; job/process-tree ownership is supplied only by S2 and is never
  broadly enumerated here.
- [Dormant code accidentally changes behavior] -> Manifest scope and focused
  source checks prove zero existing non-test call sites and zero wire/profile
  changes.

## Migration Plan

Publish the dormant foundation first. S2 may then add its bounded worker/job/
TPort lifecycle using these exact primitives. Rollback removes the new internal
files and spec; no runtime rollback is required because S1 has no production
caller.

## Open Questions

- none for S1; worker authentication, long-lived job ownership and listener
  handoff are deliberately owned by S2.
