## Context

The host-agent is a long-running interactive scheduled task. Its inherited CWD
is not an application data directory. The native helper creates CWD-relative
state before its configured cache/log handling is fully available, and a cold
syntax-helper warmup takes about six minutes on the T4 workstation.

## Decisions

1. `cmd.Dir` is the absolute parent of the configured helper binary. The
   installer stages/points at an operator-writable location; no service CWD is
   inherited.
2. Child output is configured through `BSLHelperConfig.ChildLog`, with
   `QA_MCP_BSL_CHILD_LOG` and a matching CLI flag as inputs. The supervisor
   opens it append-only per launch and closes the parent handle after `Wait`.
3. Both constructor and CLI defaults are 480 seconds. Callers may raise or
   lower it explicitly, but the product default covers the proven cold warmup.
4. The installer accepts semantic BSL parameters and renders fixed host-agent
   flags without a shell. Cache and child log default below `InstallDir`.
5. Task Scheduler receives a bounded restart count/interval in addition to the
   in-process helper restart loop. This recovers the owning host-agent after an
   exceptional task exit such as `0xC000013A`.

## Safety

- No raw helper output is added to HTTP health or doctor results.
- Tokens remain in ACL-protected files and never enter the BSL arguments.
- The helper remains loopback-only and continues to use owned process groups.
- Offline tests use a disposable fake helper and never invoke 1C or a live base.

## Verification

- Go fake-helper test starts the supervisor from a non-helper parent CWD,
  verifies the observed child CWD and readiness.
- Early-exit fake writes a marker to stderr; the configured log contains it
  after multiple launches and can be renamed/removed after stop.
- Installer contract test asserts every required flag and restart setting.
- `go test ./...`, `go vet ./...`, focused Python tests and strict OpenSpec.
