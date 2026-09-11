# Host-agent file infobase active process probe

## Status
4.done

## Owner
qa-mcp host-agent

## OpenSpec Stage
done; reviewed and published locally without push

## Source
- Root coordination card:
  `../openspec/board/1.backlog/s20-live-admin-bridge-060-live-mcp-file-infobase-timeout-and-active-client-diagnostics.md`

## Summary
Live MCP timeout diagnostics need a host-side, secret-safe signal that a 1C
client may already be using the configured Windows file infobase.

## Acceptance
- Authenticated `/path/infobase` responses include best-effort active 1C
  process metadata for the supplied path.
- The signal reports counts and bounded process names only; command lines,
  PIDs, executable paths, raw infobase paths, credentials, and connection
  strings are never returned.
- Unavailable process inspection is marked explicitly and does not claim that
  no active client exists.

## Scope
- `qa-mcp` host-agent only.
- No desktop input, UI automation, 1C data writes, process termination, or
  arbitrary platform execution.

## Change Set
- `host-agent-infobase-active-process-probe`

## Change 1: `host-agent-infobase-active-process-probe`

### Why
The Windows host-agent is the only existing authenticated boundary that can
inspect host-side state for a file infobase used by Live MCP.

### Goal
Extend the marker-only path probe with a best-effort active 1C process signal.

### Scope
- `host-agent/windows-display-agent/path_probe.go`
- Windows/non-Windows process snapshot helper as needed.
- Focused host-agent tests.

### Acceptance
- Active process evidence appears only when host-side process metadata exists
  and matches the requested file infobase path.
- Unavailable process inspection is explicit and non-causal.
- Existing path-probe redaction and auth behavior remains intact.

### Depends On
- `openspec/changes/archive/2026-07-28-host-agent-infobase-path-probe/`

### Related
- `openspec/changes/host-agent-infobase-active-process-probe/`

## Verify
- `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent` -> passed.
- `go test ./...` in `host-agent/windows-display-agent` -> passed.
- Windows read-only evidence against `historical-user@192.0.2.205` /
  `HISTORICAL-LAB-HOST` -> passed; path probe confirmed
  `C:\1C_BASES\demo10413\1Cv8.1CD`, active-process inspection returned
  available with zero matching 1C processes at probe time, and redaction checks
  passed.
- `openspec validate host-agent-infobase-active-process-probe --strict` -> passed.
- `openspec validate qa-mcp-windows-host-agent-security --strict` -> passed.
- `openspec validate --all --strict` -> 17 passed, 0 failed.
- `git diff --check` -> passed.

## Archive
- `openspec/changes/archive/2026-07-28-host-agent-infobase-active-process-probe/`

## Related
- Live MCP dependent change:
  `../live-mcp/openspec/changes/live-com-active-client-timeout-guidance/`

## Result
Implemented the host-agent active-process signal for file infobase path probes,
synced specs, verified, archived the OpenSpec change, passed independent review
cycle 2, and published locally without push.

## Next
No further ChangeRail action.

## Log
- 2026-07-28T21:08:14Z card created from root coordination story.
- 2026-07-28T21:24:00Z implemented active-process diagnostics, retained
  Windows evidence, synced specs, validated OpenSpec, and archived
  `host-agent-infobase-active-process-probe`.
- 2026-07-28T21:32:28Z independent review cycle 1 returned NO-GO for
  substring path matching that could confuse sibling infobase paths.
- 2026-07-28T21:40:00Z replaced substring matching with `/F` argument
  extraction and exact normalized path comparison; added sibling-prefix
  regression coverage and reran Go/OpenSpec/diff checks.
- 2026-07-28T21:50:00Z independent review cycle 2 returned GO with fresh
  fingerprint
  `sha256:3686ed43a328d502ba4b26f8d32fc576ec68403c8858f8d97f56fe59c3f43b3c`.
- 2026-07-28T21:52:00Z published locally without push.
