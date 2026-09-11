## 1. Matrix And Preflight

- [x] 1.1 Run the matrix checker in preflight mode for `design.md` and retain `.artifacts/openspec/native-write-bare-create-foreground/<run-id>/matrix-preflight.json`.
- [x] 1.2 Confirm existing list and record-link foreground tests or add focused coverage before changing foreground routing.

## 2. Implementation

- [x] 2.1 Add a bare-create data-link classifier for `e1cib/data/<metadata>` links without `?ref=`.
- [x] 2.2 Route bare-create write foregrounding through a create-safe foreground helper while preserving the existing list/record replay path.
- [x] 2.3 Return `foreground_method`, opened-form details when available, and stable failure reasons from the open-link label writer.

## 3. Verification

- [x] 3.1 Add focused offline tests for create, list and record-link foreground route selection.
- [x] 3.2 Run focused pytest for the touched write/MCP tests and retain output under `.artifacts/openspec/native-write-bare-create-foreground/20260630T104800Z/pytest.log`.
- [x] 3.3 Run Linux runtime preflight before any live TestClient proof and retain the preflight summary.
- [x] 3.4 Live-verify bare-create foregrounding for `e1cib/data/Справочник.Валюты` and `e1cib/data/Справочник.ДоговорыКонтрагентов`, retaining scenario log, active-form evidence and screenshot or fallback diagnostics.
- [x] 3.5 Run the matrix checker in archive mode for `design.md` and retain `.artifacts/openspec/native-write-bare-create-foreground/20260630T104800Z/matrix-archive-gate.json`.

## 4. OpenSpec

- [x] 4.1 Run `openspec validate native-write-bare-create-foreground --strict`.
- [x] 4.2 Run `git diff --check -- openspec/changes/native-write-bare-create-foreground openspec/board src tests`.
