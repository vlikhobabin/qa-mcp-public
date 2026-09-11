## Context

The installed host-agent is a `windowsgui` binary running as a Limited,
InteractiveToken scheduled task. That parent subsystem is not itself a durable
promise that console children remain invisible. Most fixed helpers already call
`hideChildWindow`, but `configureProcessGroup` replaced `SysProcAttr` afterward
and silently removed the no-window flag. BSL is a special case: previous live
proof showed that its workstation warmup fails under `CREATE_NO_WINDOW`, so it
needs console semantics without an operator-visible window.

## Decisions

1. `configureProcessGroup` allocates `SysProcAttr` only when absent and ORs
   `CREATE_NEW_PROCESS_GROUP` into existing flags.
2. Normal console helpers retain `CREATE_NO_WINDOW`. The BSL supervisor instead
   sets `SysProcAttr.HideWindow=true`, preserving the console required by its
   warmup while requesting `SW_HIDE` at process creation.
3. The installer reconciles stale BSL ownership by exact executable path. It
   does not use process-name-wide termination and does not touch any helper
   outside its staged install path.
4. The host-agent tasks remain stopped until a source-bound artifact passes
   offline tests/cross-build; live verification then checks health, restart
   count and visible top-level windows on both T4 stations.

## Safety

- No command line, environment, token or credential is added to evidence.
- Exact-path process reconciliation is limited to the installer-owned artifact.
- Windowless behavior does not weaken loopback, authentication or process-group
  cleanup boundaries.
- A failed live proof stops both station tasks again before further diagnosis.

## Verification

- Windows-only Go tests assert both process-group/no-window flags survive and
  BSL uses hidden-console rather than no-console semantics.
- Installer contract tests assert exact-path stale-helper cleanup before copy.
- Full Go tests, Windows test cross-build, artifact builder and strict OpenSpec
  validation run before station install.
- Live evidence checks both host/BSL readiness, stable restart count and absence
  of visible console windows owned by the host-agent helper tree.
