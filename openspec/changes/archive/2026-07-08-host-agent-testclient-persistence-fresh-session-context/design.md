## Context

The predecessor change `host-agent-launched-testclient-persistence` repaired
the Windows host-agent `/testclient/launch` contract so success required
process liveness plus TPort liveness, and it supplied a bounded GUI child
environment. Real .205 host evidence after that change showed the child still
exits roughly four seconds after launch even though the command and bounded
environment are correct. A normal interactive launch of the same command
persists on the same host, so the remaining differentiator is the inherited
Task Scheduler process token/session context.

This change affects provider/runtime launch behavior, not native TestClient
wire frames. Offline Linux verification can cover launch plumbing and Windows
cross-compilation only. The actual persistence proof requires the real Windows
.205 host and must remain a provider gap in this run.

## Goals / Non-Goals

**Goals:**

- Launch Windows host-agent TestClient children through a fresh interactive
  session primary token using `CreateProcessAsUserW`.
- Bind the created process to the interactive desktop (`winsta0\\default`) so
  the TestClient can create its GUI window in the logged-in session.
- Preserve existing launch validation, command construction, redaction,
  bounded environment metadata, readiness classification and status semantics.
- Fail closed with structured diagnostics when the interactive session token or
  process creation cannot be prepared.
- Keep non-Windows/Linux host-agent test behavior on the existing `exec`
  launcher path.

**Non-Goals:**

- No claim that the Windows .205 TestClient persists in this session.
- No native TestClient protocol claim, capture, replay template or corpus
  update.
- No business data mutation, UI command click, posting, import/export or COM
  live write.
- No transient scheduled-task launch mechanism unless the token path proves
  insufficient in a later runtime session.

## Decisions

### Use a platform launcher boundary

The common launch flow should continue to validate requests, build the
`1cv8 ENTERPRISE ... /TESTCLIENT -TPort` command, prepare launch metadata and
wait for readiness. The OS-specific spawn should move behind a small launcher
boundary that returns PID and a wait channel.

Rationale: this keeps readiness behavior and tests stable while allowing the
Windows build to use native token/session APIs. Non-Windows tests can continue
to execute fake platform binaries through `exec`.

### Windows launch uses the active interactive session token

The Windows launcher should obtain the active console session id, query the
session user token, duplicate it as a primary token, and call
`CreateProcessAsUserW` with `lpDesktop = "winsta0\\default"`. The bounded
environment remains available and is passed as a Unicode environment block.
Launch-context metadata should expose only bounded facts such as method,
session id and environment key names, not token handles or environment values.

Rationale: the real-host evidence isolated the remaining failure to inherited
Task Scheduler token/session state. `CreateProcessAsUserW` with the active
session token is the smallest direct fix for that differentiator.

Alternative considered: register and run a transient interactive scheduled
task. That remains a fallback follow-up if `CreateProcessAsUserW` cannot be
used on the real host, but it adds task lifecycle cleanup and policy surface
that is not needed for the first fix.

### Fail closed when token preparation fails

If active-session id lookup, user-token query, token duplication or
`CreateProcessAsUserW` fails, `/testclient/launch` should return `ok:false`
with a structured diagnostic such as `testclient-interactive-session-unavailable`
or `testclient-launch-start-failed`. It should not silently fall back to direct
`exec` on Windows because direct `exec` is the path proven insufficient on .205.

Rationale: a direct fallback can recreate the false-positive readiness path and
hide the launch-context problem from operators.

## Risks / Trade-offs

- `WTSQueryUserToken` may require privileges unavailable to the deployed
  host-agent account -> return a structured provider/runtime diagnostic and
  keep transient scheduled task launch as a follow-up option.
- Offline tests cannot prove Windows GUI persistence -> retain a provider-gap
  artifact and do not claim the persistence acceptance criterion.
- Windows API calls are easy to break at compile time -> include a Windows
  cross-compile check for the host-agent package.
- Passing a bounded environment with an interactive token may still miss a
  user-profile detail that `CreateEnvironmentBlock` would provide -> retain
  launch-context metadata and the required real-host proof to validate.

## Migration Plan

1. Add RED Go tests around the new launcher boundary and launch-context metadata.
2. Implement the non-Windows launcher as the current `exec` behavior.
3. Implement the Windows launcher with active session token duplication and
   `CreateProcessAsUserW`.
4. Run focused Go tests, full host-agent Go tests and Windows cross-compile.
5. Record the Windows .205 persistence proof as a qa-mcp provider gap for this
   session.
6. Sync the requirement delta into `qa-mcp-windows-host-agent-security` and
   archive after verification.

## Open Questions

- Whether the deployed .205 host-agent account has the privileges required for
  `WTSQueryUserToken` from its scheduled-task context. The real host is
  unavailable here, so this remains part of the provider-gap proof.
