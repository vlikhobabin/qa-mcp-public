## 1. Matrix And Preflight

- [x] 1.1 Run the matrix checker in preflight mode for `design.md` and retain `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/matrix-preflight.json`.
- [x] 1.2 Identify a usable demo10413 `Контрагент` owner value through a read-only fixture probe or retained prior evidence.

## 2. Implementation

- [x] 2.1 Add an explicit open-link reference field step or field mode for visible labels such as `Владелец`.
- [x] 2.2 Drive reference selection with variable-length requested values and return separate targeting/selection diagnostics.
- [x] 2.3 Ensure unsupported, missing or ambiguous reference selection fails before any save command.

## 3. Verification

- [x] 3.1 Add focused offline tests for reference step routing, variable-length values and fail-closed selection diagnostics.
- [x] 3.2 Run focused pytest for the touched write/scenario/MCP tests and retain output under `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/pytest.log`.
- [x] 3.3 Live-verify `Владелец` selection on the foregrounded `ДоговорыКонтрагентов` create form and retain scenario log, active-form evidence and screenshot or fallback diagnostics.
- [x] 3.4 Run the matrix checker in archive mode for `design.md` and retain `.artifacts/openspec/native-write-open-link-reference-owner/20260630T113200Z/matrix-archive-gate.json`.

## 4. OpenSpec

- [x] 4.1 Run `openspec validate native-write-open-link-reference-owner --strict`.
- [x] 4.2 Run `git diff --check -- openspec/changes/native-write-open-link-reference-owner openspec/board src tests`.
