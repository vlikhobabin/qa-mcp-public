# S35 QA Host-Agent Claude Effort Parity

## Status
4.done

## Owner
unassigned

## Order Index
350

## OpenSpec Stage
archived

## Source
- root `openspec/board/2.todo/s35-solo-post-install-readiness-010-agentic-rag-host-bridge-token-and-served-deadline.md`
- root `openspec/changes/s35-agentic-host-bridge-readiness-coordination`
- `agentic-rag/openspec/board/2.todo/s35-agentic-served-deadline-profile-and-smoke.md`

## Summary
Make Windows host-agent `/agent/complete` preserve `reasoning_effort` for
Claude as well as Codex, keep agent selection explicit, and expose bounded
effective profile metadata for S35 Agentic RAG readiness.

## Acceptance
- Claude requests with `reasoning_effort` render `claude --effort <level>`.
- Codex requests with `reasoning_effort` still render
  `model_reasoning_effort=<level>`.
- Unsupported effort behavior is fail-closed with a typed diagnostic and cannot
  return successful downgraded text.
- Missing or failing selected agents do not fallback to another installed CLI.
- Success and authenticated failure paths retain only bounded non-secret profile
  metadata.

## Change Set
- `s35-qa-host-agent-claude-effort-parity`

## Verify
- RED (expected failure): `go test ./... -run '^TestAgentComplete'` in
  `host-agent/windows-display-agent` failed five new behavior checks before
  implementation: effective profile metadata, typed unsupported-effort
  handling, and selected-agent no-fallback evidence.
- passed: `go test -count=1 ./... -run
  '^(TestAgentComplete|TestAgentPortable)'` in
  `host-agent/windows-display-agent` (`ok qa-mcp-host-agent`, 2.475s).
- passed: `go test -count=1 ./...` in `host-agent/windows-display-agent`
  (`ok qa-mcp-host-agent`, 15.631s).
- passed: `openspec validate s35-qa-host-agent-claude-effort-parity --strict`.
- passed: `openspec validate qa-mcp-windows-host-agent-security --strict`.
- passed: `openspec validate --all --strict` (18 passed, 0 failed).
- passed: `git diff --check`.
- passed: `go vet ./...` in `host-agent/windows-display-agent`.
- passed: scoped `python3 /opt/changerail/scripts/public-surface-scan.py
  --root .` for the card, archive, and synced spec (7 files, 0 findings).
- passed: source-bound Windows amd64 `TestAgentPortable*` suite on authorized
  host `HISTORICAL-LAB-HOST`; command rendering, typed effort failure, bounded
  profile metadata, and both failing-selected-agent no-fallback branches
  passed. Test-binary SHA-256:
  `99e5e15a1a42f1c6ac384efa79668908e027fc66fcbc11bc6c3da6a80d7065da`.
- passed: required read-only SSH contour check on `HISTORICAL-LAB-HOST` confirmed
  the demo infobase, host-agent protocol, and both CLI availabilities. Its
  running pre-S35 artifact was explicitly excluded as changed-source proof
  after a Claude effort probe returned bounded HTTP 502 `cli-failed`.
- retained ignored evidence:
  `.runtime/changerail/evidence/s35-qa-host-agent-claude-effort-parity/windows-native-verification.md`.
- product artifact note: no product host-agent executable was rebuilt,
  replaced, or deployed; the temporary source-bound Windows test executable
  was removed from the authorized E2E host after its hash-matched run.

## Archive
- `openspec/changes/archive/2026-07-29-s35-qa-host-agent-claude-effort-parity/`

## Related
- root `openspec/board/2.todo/s35-solo-post-install-readiness-010-agentic-rag-host-bridge-token-and-served-deadline.md`
- root `openspec/changes/s35-agentic-host-bridge-readiness-coordination`
- `agentic-rag/openspec/board/2.todo/s35-agentic-served-deadline-profile-and-smoke.md`
- archived origin: `openspec/changes/archive/2026-07-04-host-agent-agent-cli-execute`

## Result
completed: implementation, verification, spec sync, archive, and independent
review cycle 3 GO (8/8 acceptance criteria, no findings).

Published reviewed payload as `51c12607f94808c3f75f019b587b91076673a853`; push status `skipped` on `main`/`origin`.

## Next
- done

## Change 1: `s35-qa-host-agent-claude-effort-parity`

### Why
Agentic RAG host-bridge readiness depends on the selected agent/model/effort
profile being real. Silently ignoring Claude effort would make S35 readiness
evidence ambiguous even when the request succeeds.

### Goal
Make `/agent/complete` preserve or fail-closed on the requested effort profile
for both supported local model CLIs.

### Scope
- Host-agent command rendering and response/readiness metadata.
- Host-agent Go unit tests.
- Optional Windows artifact proof if delivery rebuilds the executable.

### Acceptance
- OpenSpec change validates under strict mode.
- Delivery proves command construction and no-fallback behavior with automated
  Go tests.
- Retained evidence documents whether Windows host-agent artifact rebuild was
  required.

### Depends On
- root S30 delivery and push complete.

### Related
- `openspec/changes/s35-qa-host-agent-claude-effort-parity`

## Log
- 2026-07-29T15:06:09Z card created from S35 root handoff; OpenSpec artifacts generated.
- 2026-07-29T15:09:34Z strict OpenSpec validation and diff-check passed during planning.
- 2026-07-29T16:55:46Z ChangeRail delivery started; card moved to `3.inprogress`.
- 2026-07-29T17:01:08Z RED/GREEN host-agent tests, strict OpenSpec validation,
  spec sync, and whitespace checks passed; Windows artifact smoke was not
  applicable because no executable was rebuilt.
- 2026-07-29T17:02:00Z change archived at
  `openspec/changes/archive/2026-07-29-s35-qa-host-agent-claude-effort-parity/`
  after the already-synced main capability passed strict validation.
- 2026-07-29T17:03:34Z Go vet and the scoped public-surface scan passed; three
  findings from a scan run without an explicit consumer root were initially
  misattributed as a repository baseline caveat.
- 2026-07-29T17:11:37Z review cycle 1 returned NO-GO on the unreproducible
  scanner caveat. Removed that caveat and reran the final-payload scan with the
  consumer root explicitly set; 7 files passed with 0 findings.
- 2026-07-29T17:25:59Z review cycle 2 returned NO-GO on missing mandatory
  Windows-native evidence and a failing-selected-agent test-depth finding.
  Added branch-sensitive portable tests, ran the source-bound Windows test
  binary on the authorized E2E host, retained the required COM-lab read-only
  contour evidence, and cleaned the exact temporary remote test file.
- 2026-07-29T17:33:22Z independent review cycle 3 returned GO with all 8
  acceptance criteria passing and no findings.
- 2026-07-29T17:36:13Z publish finalized card into `4.done` with commit `51c12607f94808c3f75f019b587b91076673a853` and push status `skipped`.
