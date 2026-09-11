## Context

`WTSQueryUserToken` is unavailable to the installed host-agent and
`CreateProcessAsUserW` is empirically insufficient for 1C TestClient
persistence even when the caller is SYSTEM. A transient InteractiveToken task
whose action is 1cv8 itself also cannot transfer durable ownership: removing or
completing that task terminates its scheduler job and the direct child. A
controlled task whose action uses `Shell.Application.ShellExecute` instead
produced a client that survived task completion and removal and completed the
product protocol handshake. The delivered launch reproduces that proven
contour without placing the infobase credential in task metadata.

## Goals / Non-Goals

**Goals:** launch from a verified interactive host-agent session; preserve
one-string 1C argument quoting; avoid plaintext launch artifacts; return the
actual PID; monitor readiness/exit; select the exact requested four-component
platform version.

**Non-Goals:** run the host-agent as SYSTEM; create credential-bearing task
actions or scripts; leave a per-launch task after response; acquire another
user's token; accept caller-provided executables/argv; change Linux launch.

## Decisions

### The installed host-agent verifies the interactive logon

The Windows launcher first compares `ProcessIdToSessionId(GetCurrentProcessId)`
with `WTSGetActiveConsoleSessionId`. A missing active console session or any
mismatch fails closed before a launch artifact is created.

### The transient task contains no TestClient credential

Live T4 probes showed that direct `CreateProcessW` from the otherwise-correct
Limited/Interactive host-agent still yields a TestClient that binds briefly and
exits. The same semantic command launched by the interactive Windows shell
under an InteractiveToken task survives task completion and task removal, and
the bundled manager handshake then completes on `demo10413`.

After session verification, the host-agent opens an ephemeral loopback listener
and generates a random nonce. A fixed registration helper receives only a JSON
task name and fixed action. The hidden Limited/InteractiveToken task action
contains only its fixed encoded broker, loopback port and nonce. The broker
authenticates the nonce, receives the credential-bearing JSON request over that
in-memory connection, renders the 1C-specific one-string quoting, and invokes
`Shell.Application.ShellExecute`. It returns only a bounded `started`
acknowledgement. The registration helper waits for task completion and
unregisters it before launch returns; no temporary script, wrapper or PID file
is created.

### Ownership is explicit

The host-agent waits for the requested TPort, resolves its owning PID through
the Windows TCP owner table, and reopens that 1cv8 process handle as the
ownership boundary. A post-create session mismatch terminates only that
just-created PID. Existing readiness dwell classifies early
exit/not-listening exactly as before, and later T4 cleanup targets the
explicitly owned station contour.

### The QA protocol version pins the Windows executable

The Python launch path sends its exact `QA_MCP_PLATFORM_VERSION` (or the
four-component version extracted from `PLATFORM_ROOT`). The host-agent accepts
only a four-numeric-component semantic value and resolves 1cv8 only from that
catalog version. A missing requested build fails closed instead of falling back
to the newest installed platform, because the TestManager captures are
version-coupled.

## Risks / Trade-offs

- Host-agent started outside the active console session → return bounded
  `testclient-interactive-session-unavailable` without creating a child.
- Shell-broker startup or TPort/PID discovery fails → return bounded
  `testclient-launch-start-failed`; never fall back to direct process creation.
- The task broker receives a password-bearing request → the value exists only
  in the authenticated loopback exchange and the required 1cv8 child command
  line, never helper argv, task metadata, disk or diagnostics.
- Password exists only in the child command line → retain existing bounded HTTP
  redaction and never write a wrapper/task action/log entry.

## Verification

- Offline Go tests cover 1C shell argument rendering, authenticated broker
  request separation, TPort-owner parsing, bounded launch context and
  redaction.
- Windows cross-build proves build-tagged code compiles.
- Resolver tests prove exact selection and invalid/missing-version rejection.
- Real station proof checks PID, TPort and window immediately and after >=60s,
  plus absence of transient task/wrapper artifacts and owned cleanup.
