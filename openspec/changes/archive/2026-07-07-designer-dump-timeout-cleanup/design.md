## Context

The card comes from `docs/qa-mcp-connection-issues-2.md` finding #14: an
ordinary connection-diagnostics investigation tried to resolve a catalog name by
starting Designer with `/DumpConfigToFiles`, the command timed out, and an extra
`1cv8.exe DESIGNER` process had to be stopped manually.

Current qa-mcp diagnostics already have lighter routes: `qa_mcp_doctor` uses
host-agent `/version` and `/health`, TestClient TPort smoke, window evidence,
effective-user checks, and optional host-agent COMConnector doctor checks. The
host-agent already exposes `/platform/execute` for explicit platform commands
with allowlisting, mutation classification, operator intent, timeout and
process-group cleanup. The missing contract is that ordinary diagnostics do not
fall back to Designer metadata dumps, and that timeout/cancel responses make
spawned PIDs visible when cleanup is needed.

## Goals / Non-Goals

**Goals:**
- Keep ordinary connection diagnostics Designer-free.
- Preserve a safe path for explicit heavy platform operations through
  host-agent `/platform/execute`.
- Return spawned process PID evidence on platform timeout/cancel failures so
  operators can audit or manually clean up a suspected orphan.
- Cover behavior with offline Python and Go tests.

**Non-Goals:**
- Add a new Designer metadata dump helper.
- Execute a real Windows Designer dump during verification.
- Change host-agent executable allowlists, mutation policy, auth, or redaction
  semantics beyond the timeout/cancel diagnostic payload.
- Add a new native TestClient protocol claim or capture.

## Decisions

1. Treat the Designer-free diagnostic rule as an endpoint contract, not a new
   metadata resolver. Existing diagnostic flows should prefer host-agent health,
   descriptor/open-link input, metadata-provider input, and optional COM
   read-smoke evidence.
2. Extend host-agent platform execution errors to carry structured details for
   process identity. `writeError` stays available for existing simple errors,
   while platform timeout/cancel paths can return an error body with `pids` and
   bounded `detail`.
3. Report only the direct spawned PID in this change. Windows `taskkill /T /F`
   and Unix process-group kill still handle descendants, but enumerating child
   PIDs portably is a separate host-agent feature.
4. Keep live Windows proof as a planned runtime checkpoint. The Linux workspace
   can prove the HTTP/API contract and process cleanup behavior with fake
   executables; real Windows `1cv8.exe DESIGNER` orphan checks require an
   operator-owned Windows desktop.

## Risks / Trade-offs

- PID reporting proves what the host-agent spawned, not that Windows killed
  every descendant. Mitigation: keep the existing process-group cleanup contract
  and retain a Windows-host smoke checkpoint for package validation.
- The current diagnostics code does not contain a Designer dump fallback, so the
  Designer-free behavior is partly a regression guard. Mitigation: add tests and
  docs that make the allowed diagnostic routes explicit.
- `/platform/execute` still permits explicit Designer operations when declared
  mutating with operator intent. Mitigation: this is intentional for approved
  platform work; ordinary diagnostics must not call that path.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/platform/execute` timeout/cancel cleanup | Offline fake platform command tests proving timeout/cancel response shape, PID reporting, and no secret leakage | Go unit test output, retained verification summary | `.artifacts/openspec/designer-dump-timeout-cleanup/20260707T205910Z/host-agent-timeout-evidence.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | `qa_mcp_doctor` and connection diagnostics guidance | Offline Python doctor/tool-reference tests proving diagnostics do not call Designer/platform execute and guidance stays light-weight | Pytest output, retained verification summary | `.artifacts/openspec/designer-dump-timeout-cleanup/20260707T205910Z/doctor-designer-free-evidence.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows host with 1C platform installed | Operator-owned smoke for an explicit host-agent platform timeout confirming no leftover Designer process | Windows smoke transcript when available | `.artifacts/openspec/designer-dump-timeout-cleanup/<run-id>/windows-designer-timeout-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows desktop or licensed Windows 1C platform is available inside this Linux workspace. | First Windows package run should execute the smoke before relying on real Designer timeout cleanup evidence. |
| BSL-only module edit | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | This change edits Python/Go diagnostics and documentation only; no BSL source is modified. | No BSL runtime behavior is expected. |
