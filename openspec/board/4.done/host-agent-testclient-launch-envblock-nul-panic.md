# Fix the host-agent TestClient launch environment-block NUL panic

## Status
4.done

## Owner
unassigned

## Order Index
131

## OpenSpec Stage
done. Apply-ready single change delivered. Live-.205-confirmed crash fix in the
F2 interactive-session launch path; independent OPSX review verdict = go
(cycle 2, after restoring 3 spec scenarios dropped by the cycle-1 delta).

## Source
- 2026-07-08 live .205 test of the F2 build
  (`host-agent-testclient-persistence-fresh-session-context`, `777bd3b`): with a
  host-agent granted `SeTcbPrivilege`, `/testclient/launch` crashed the serving
  goroutine with `panic: syscall: string with NUL passed to StringToUTF16` in
  `windowsEnvironmentBlock`. Invisible offline because the code is
  `//go:build windows` and the offline suite mocks the launcher.

## Problem
`windowsEnvironmentBlock` built the Windows environment block as
`syscall.StringToUTF16(strings.Join(env, "\x00") + "\x00")`.
`syscall.StringToUTF16` panics on any interior NUL, and a Windows environment
block is by definition NUL-delimited, so every non-empty child environment
panicked — i.e. every real interactive-session launch aborted before any process
was created.

## Scope
1. Render the environment block with an interior-NUL-safe, platform-neutral
   encoder (`unicode/utf16`), one NUL-terminated segment per entry plus a final
   block terminator.
2. Move the helper into a neutral file so the offline Go suite covers it on every
   platform; remove the panicking implementation.
3. Add offline Go coverage (multi-entry / empty / skip-empty / Unicode).
4. Bump the host-agent version string.

## Acceptance
- The offline Go suite covers environment-block rendering and is GREEN natively;
  the multi-entry case does not panic and yields intact NUL-delimited segments
  plus a double-NUL terminator.
- `GOOS=windows go vet` + build clean.
- Live .205 evidence: the fixed build's SYSTEM-context launch no longer panics
  (advances to `testclient-exited-early`).
- Regression: no change to protocol frames, replay templates, Python manager,
  MCP setup or runtime lab config.

## Change 1: `host-agent-testclient-launch-envblock-nul-panic`

### Why
The F2 interactive-session launch cannot create a TestClient at all while the
environment-block renderer panics on the NUL segment delimiters.

### Goal
Render a valid, interior-NUL-safe Windows environment block from a neutral,
offline-tested encoder and remove the panicking implementation.

### Acceptance
- As in the card Acceptance.

### Related
- `host-agent-testclient-persistence-fresh-session-context` (F2; the launch path
  this crash lives in — note that even with the panic fixed and `SeTcbPrivilege`
  present, the CreateProcessAsUser client still exits early, so F2's persistence
  hypothesis is separately disproven on the live host).
- Capability `qa-mcp-windows-host-agent-security`.

## Log
- 2026-07-08 filed from the live .205 Proof-B session after the F2 build crashed
  on launch; fix implemented + offline-tested + live no-panic confirmed.
- 2026-07-08 delivered: change archived, spec synced. Independent fresh-context
  OPSX review (claude subagent, not the implementer): cycle-1 no-go caught a
  silent spec regression (the delta dropped 3 unrelated scenarios on sync);
  restored them in the main spec + delta; cycle-2 verdict = go, all 4 acceptance
  criteria pass. .205 left on the fixed host-agent build (0.1.3-testclient-envblock).
