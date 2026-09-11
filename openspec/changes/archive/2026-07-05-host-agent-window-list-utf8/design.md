## Context

The Windows host-agent enumerates desktop windows through Win32 APIs and returns
the list to qa-mcp display tools and `delivery/bootstrap.ps1`. A tester observed
that Russian 1C titles came back as mojibake even though PowerShell
`MainWindowTitle` showed readable text. That points to an encoding boundary in
the host-agent path, not to the 1C process itself.

## Goals / Non-Goals

**Goals:**

- Return `WindowInfo.title` as readable Unicode in JSON for Russian and ASCII
  titles.
- Retain existing authentication, CORS, and output-bounding behavior.
- Make the bootstrap window-selection diagnostic explicit when the title is weak
  or missing.
- Add unit tests that fail if non-ASCII titles are corrupted before JSON
  encoding.

**Non-Goals:**

- Do not add unauthenticated window enumeration.
- Do not introduce a new desktop automation backend.
- Do not require a live Windows desktop during Linux CI; retain that as a
  Windows-native smoke artifact.

## Decisions

- **Decode at the Win32 boundary.** The Windows driver must convert
  `GetWindowTextW` UTF-16 data to a Go string before any JSON response is built.
  This keeps later JSON encoding straightforward and avoids code-page guesses.
- **Keep JSON response UTF-8.** The HTTP handler returns normal JSON strings and
  relies on Go's JSON encoder for UTF-8 output. Tests assert decoded strings, not
  byte-level escape preferences.
- **Separate weak-match diagnostics from matching policy.** The bootstrap may
  still accept a generic fallback title, but it must warn and suggest
  `-WindowTitle` rather than silently presenting a weak match as robust.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Windows host-agent `/window_list` title enumeration | Go unit test with Russian title fixture and JSON response assertion | Go test output, Linux host-agent package test output | `.artifacts/openspec/host-agent-window-list-utf8/<run-id>/host-agent-window-list-utf8.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows 1C TestClient window matching | Read-only authenticated `/window_list` request against an operator-owned Windows host | Retained host-agent transcript with readable Russian title and selected title guidance | `.artifacts/openspec/host-agent-window-list-utf8/<run-id>/windows-window-list-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, GUI desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | The next Windows package run must retain this smoke before relying on Russian-title auto-selection. |

## Risks / Trade-offs

- **Windows-only behavior can drift from Linux tests.** Mitigate with a
  cross-compiled Windows test binary and a retained Windows smoke checklist.
- **Fallback matching may still choose the wrong generic window.** Mitigate by
  warning and preserving explicit `-WindowTitle` guidance.
