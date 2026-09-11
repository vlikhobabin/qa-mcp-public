## 1. Planning And Matrix Preflight

- [x] 1.1 Create proposal, design, delta specs and tasks for
  `host-agent-testclient-launch-envblock-nul-panic`.
- [x] 1.2 Run `openspec validate host-agent-testclient-launch-envblock-nul-panic --strict`
  and `git diff --check -- openspec/changes/host-agent-testclient-launch-envblock-nul-panic openspec/board`.
- [x] 1.3 Retain the live .205 crash-and-fix evidence under
  `.artifacts/openspec/host-agent-testclient-launch-envblock-nul-panic/<ts>/`.

## 2. Test-First Environment-Block Coverage

- [x] 2.1 Add RED-first offline Go coverage where a multi-entry environment is
  rendered into a Windows environment block: it must yield each `KEY=VALUE`
  segment intact plus a double-NUL terminator and must not panic. (The prior
  `syscall.StringToUTF16` implementation panics under this test.)
- [x] 2.2 Add coverage for empty / all-empty env (nil block), skipped empty
  interior segments, and Unicode (Cyrillic) values.
- [x] 2.3 Confirm the coverage runs in the native (non-Windows) offline suite,
  proving the encoder is now platform-neutral and offline-observable.

## 3. Implementation

- [x] 3.1 Move `windowsEnvironmentBlock` into a platform-neutral file and encode
  each segment with `unicode/utf16`, NUL-terminating each segment and appending
  a final block terminator.
- [x] 3.2 Remove the panicking `syscall.StringToUTF16(strings.Join(...))`
  implementation from the `//go:build windows` file; leave the caller and its
  `len(envBlock) > 0` guard unchanged.
- [x] 3.3 Bump `AgentVersion` to reflect the fixed launch build.

## 4. Verify

- [x] 4.1 `go test ./...` in `host-agent/windows-display-agent/` is GREEN
  natively, including the new environment-block tests.
- [x] 4.2 `GOOS=windows go vet ./...` and `GOOS=windows go build` are clean.
- [x] 4.3 Live .205: with the fixed build the SYSTEM-context
  `/testclient/launch` no longer panics (advances to `testclient-exited-early`
  instead of crashing the serving goroutine); retained as evidence.

## 5. Sync And Archive

- [x] 5.1 Sync the delta into `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`.
- [x] 5.2 Archive the change and update the board card at publish (the scoped
  publish manifest reconstructs from git status; no manifest file is
  hand-authored).
