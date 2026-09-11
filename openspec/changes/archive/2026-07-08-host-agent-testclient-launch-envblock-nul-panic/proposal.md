## Why

The Windows host-agent TestClient launch path renders the child GUI
environment with `windowsEnvironmentBlock`, which built the block as
`syscall.StringToUTF16(strings.Join(env, "\x00") + "\x00")`.
`syscall.StringToUTF16` aborts (panics) on any interior NUL, and a Windows
environment block is by definition a NUL-delimited, double-NUL-terminated
string. So every launch with a non-empty child environment — i.e. every real
launch — panicked inside the HTTP handler.

This was invisible to the offline suite because the code lived in a
`//go:build windows` file exercised only when `CreateProcessAsUserW` actually
runs. Live .205 confirmation: with a host-agent granted the required
`SeTcbPrivilege`, `/testclient/launch` crashed the serving goroutine with
`panic: syscall: string with NUL passed to StringToUTF16`
(`windowsEnvironmentBlock` frame), closing the client connection before any
process was created. This blocks the interactive-session launch path
end-to-end.

## What Changes

- Render the Windows environment block with an interior-NUL-safe encoder:
  UTF-16 encode each `KEY=VALUE` segment independently, NUL-terminate each
  segment, and append one final block terminator. Never hand the joined,
  NUL-bearing block to a NUL-forbidding helper.
- Move `windowsEnvironmentBlock` into a platform-neutral file using
  `unicode/utf16` (no Windows-only syscall) so it is compiled and covered by
  the offline Go suite on every platform.
- Add offline Go coverage: multi-entry env yields intact NUL-delimited
  segments plus a double-NUL terminator without panicking; empty/all-empty env
  yields a nil block; empty interior segments are skipped; Unicode (Cyrillic)
  values survive encoding.
- Bump the host-agent version string to reflect the fixed launch build.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: the constrained TestClient launch
  endpoint MUST render the bounded GUI child environment as a valid Windows
  environment block whose interior NUL segment delimiters do not abort or
  corrupt the launch.

## Impact

- Touches Windows host-agent Go launch code under
  `host-agent/windows-display-agent/` (moves `windowsEnvironmentBlock` to a
  neutral, testable file; removes the panicking implementation).
- Adds focused offline Go tests for environment-block rendering.
- Updates OpenSpec artifacts, the main spec after sync, card status and the
  delivery manifest.
- Does not change native TestClient protocol frames, replay templates, Python
  manager transport semantics, MCP provider setup or runtime lab configuration.
- Live Windows .205 confirmation of the crash and the post-fix no-panic launch
  is recorded as retained evidence for this run.
