## Context

The blocked S50-120 payload already resolves an exact process-owned,
empty-title `V8TopLevelFrame*` target and calls the existing fixed UI
Automation reader. Sanitized Windows evidence shows a successful endpoint
response with no named cells for both a static-marker fixture and a native
`LISTBOX` marker. Screenshot, key, text, click, selector precedence, unrelated
foreground isolation, weak-target refusal, and typed-session checks all pass.

The current reader starts a fixed Windows PowerShell UIA query, obtains an
`AutomationElement` from the resolved HWND, enumerates descendants, and returns
non-empty names for a bounded set of allowlisted control types. The missing
marker can therefore be caused by the descendant-view/apartment/execution
boundary or by a fixture that does not expose the expected accessible element.
The change must distinguish those cases on the authorized interactive Windows
host before choosing the narrow fix.

This is Windows host-agent/runtime-fixture research, not native
TestManager/TestClient protocol research. Capture sources, frame ranges,
dynamic protocol fields, normalized frame hashes, and replay strategy are
`N/A`. No protocol capture, 1C infobase, or business data is involved.

## Goals / Non-Goals

**Goals:**

- Add a Windows-native regression that creates an owned empty-title target and
  a visible named native descendant, then exercises the production reader.
- Retain a genuine RED outcome before changing the reader or fixture contract.
- Make the production visible-cell route return the marker through the exact
  lifecycle/client target while preserving targeting and session fail-closed
  behavior.
- Re-run the complete S50-120 source-bound Windows matrix and exact cleanup.

**Non-Goals:**

- Changing Python MCP/display-backend behavior or lifecycle target validation.
- Adding caption, wildcard, generic 1C-window, arbitrary HWND, or foreground
  fallback behavior.
- Accessing a TestClient infobase, mutating business data, capturing native
  protocol traffic, or retaining raw cells, screenshots, identities, logs, or
  response bodies.

## Decisions

### 1. Reproduce at the production reader boundary

A Windows-only Go regression will create the target and marker with owned
Win32 resources and invoke the same `readVisibleListCells` implementation used
by `/uia/visible_list_cells`. The UI thread and UIA query run on separate
execution threads so the test does not depend on cross-thread message pumping.
The assertion checks only marker presence and reports bounded counts/types on
failure.

This is preferred to a fake-driver endpoint test because existing fake tests
already prove route targeting but cannot detect a real Windows UIA descendant
failure. Testing only the ignored PowerShell proof was rejected because it
would not leave a durable regression tied to product code.

### 2. Diagnose views and execution state without retaining UI content

The RED run may compare bounded marker-presence and element-count results for
the current descendant query and an alternative UIA tree/view or apartment
boundary. Raw names, handles, process ids, titles, screenshots, and PowerShell
output are never retained. The narrowest source change that makes the
production reader observe the owned marker becomes the implementation:

- if the current fixture does not expose an accessible named descendant, fix
  the fixture contract and keep the production reader unchanged;
- if UIA exposes the marker through another standard view/query boundary,
  adjust only the fixed reader script/launch contract;
- if neither case is proven, stop with a sanitized provider/runtime gap rather
  than broadening target resolution.

### 3. Preserve target and session gates unchanged

The reader remains downstream of exact lifecycle/PID/TPort/window validation
and `requireInteractiveDesktop`. The fix will not move UIA before those gates
or retry with a weaker target. Existing focused tests and the complete Windows
matrix must remain green.

### 4. Keep the rescue publish scope separable from its predecessor

The pre-existing S50-120 Python, Go, docs, tests, and active OpenSpec change
remain predecessor-owned. S50-120B owns its OpenSpec/card/spec payload, new
Windows regression, the minimal UIA-reader or fixture-contract hunk, and
sanitized ignored evidence. If a product hunk shares an already-dirty file,
review and publish must isolate that exact hunk; inability to separate it is a
safety stop, not permission to publish the predecessor payload.

### 5. Retain a bounded verification matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason | Residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows host-agent UIA visible-cell reader against an owned empty-title native fixture | Windows-only RED/GREEN regression, source-bound full route/session/cleanup scenario, exact cleanup model | `scenario_file`, `scenario_log`, Windows-native test result, source hashes, `cleanup_evidence` | `.runtime/changerail/evidence/fix-windows-visible-list-cell-runtime-proof/` | required | N/A | A native fixture proves the reader boundary; S50-120 still owns final lifecycle-window integration over its full payload. | qa-mcp repository |

BSL, metadata, managed-form, role, posting, report, and migration surfaces are
`N/A`: no 1C source, metadata, role, persisted state, report, or data is read or
changed. Residual risk is limited to the later S50-120 integration proof, which
this card explicitly reruns before handoff.

## Risks / Trade-offs

- [Risk] A same-process fixture can behave differently from a real 1C window.
  -> Keep the durable regression at the production UIA boundary and require the
  separate source-bound S50-120 route matrix before completion.
- [Risk] Diagnostic enumeration could retain UI content. -> Retain only
  booleans, counts, allowlisted type categories, hashes, test outcomes, and
  cleanup state under ignored runtime paths.
- [Risk] A weaker selector could make the marker appear while breaking safety.
  -> Do not change selector resolution; re-run explicit precedence,
  unrelated-foreground isolation, weak-target refusal, and typed-session rows.
- [Risk] Cleanup could affect unrelated Windows resources. -> Use unique exact
  task/stage names and stop/remove only processes and files created by this run.

## Migration Plan

1. Preflight the authorized Windows host, identity, interactive session, and
   absence of the exact prior task/stage.
2. Add and run the Windows-native regression against the current reader and
   retain the failing RED summary.
3. Apply the narrow reader or fixture-contract fix selected by the bounded
   diagnostic, then rerun the same regression GREEN.
4. Build source-bound Windows artifacts, verify their hashes, and run the full
   S50-120 route/session/cleanup matrix.
5. Run offline Go/OpenSpec/whitespace checks, sync the capability, archive the
   change, and hand the combined lineage back to independent review.

Rollback is removal of the exact UIA-reader/fixture hunk and Windows regression.
Ignored proof stages are deleted by exact name; no runtime or data rollback is
needed.

## Open Questions

- Resolved during delivery: the production reader ran in STA, and the original
  `LISTBOX` target exposed one unnamed container with no named or allowlisted
  descendants in true/raw/control/content views. Selecting the item and using a
  common-controls list view remained RED. An explicitly named WPF UIA
  `ListBoxItem` passed through the unchanged production reader, selecting the
  fixture-contract correction branch without any reader or targeting change.
