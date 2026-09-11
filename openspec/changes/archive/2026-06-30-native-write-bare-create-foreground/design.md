## Context

The existing write foreground helper replays `listform-read` with
`_FOREGROUND_CAPTURE_NAV = "e1cib/list/Справочник.Товары"` retargeted to the
requested link. That path is live-proven for lists and `?ref=` record links, but
the fresh-code retest showed bare-create links diverge and return
`foregrounded=false`. The read opener `_open_form_by_link` already opens and
resolves the same bare-create form through splice navigation.

## Goals / Non-Goals

**Goals:**
- Detect bare-create data links before foreground replay.
- Foreground bare-create forms without changing list and existing-record
  behavior.
- Keep the manager socket or equivalent active-form hold open until label-based
  XTEST input completes.
- Return structured diagnostics and evidence paths for foreground failures.

**Non-Goals:**
- Reference selection, save semantics, persistence verification and cleanup are
  handled by later card-owned changes.
- No raw capture streams or platform logs are committed.

## Decisions

- Use a narrow link classifier for `e1cib/data/<metadata>` links without
  `?ref=`. This prevents a create-specific path from affecting list and record
  links.
- Use a create-scoped foreground helper that reuses the proven full
  activate/render foreground sequence, but allows the captured list-read tail to
  time out after a create form has rendered. The subsequent label localization
  is the proof that the form is visually foregrounded.
- Keep the default `_foreground_form_by_link` list/record behavior strict.
  Partial foreground replay is enabled only through the bare-create helper.
- Surface failure as `foregrounded=false` with a stable `foreground_method`,
  `reason`, and retained screenshot/log path where available.

## Risks / Trade-offs

- Bare-create foreground may still vary by metadata object render timing.
  Mitigation: use a create-scoped partial replay only after the form has had the
  full activate/render sequence and verify on `Справочник.Валюты` plus
  `Справочник.ДоговорыКонтрагентов`.
- Holding a create opener socket may leave a form active after failure.
  Mitigation: close only the owned socket and keep cleanup limited to resources
  qa-mcp created.
- Live proof is write-path UI evidence, not persisted-data evidence.
  Mitigation: this change gates only foregrounding; persistence proof is a
  later change.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI | `write_form_fields_by_label` foreground for bare-create links | Live scenario opens `Справочник.Валюты` and `Справочник.ДоговорыКонтрагентов` create forms and captures active form evidence | `qa_testclient_bundle`, `active_window`, `form_tree`, `screenshot/fallback`, `scenario_log` | `.artifacts/openspec/native-write-bare-create-foreground/20260630T104800Z/live-summary.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Static/BSL | Python-only qa-mcp code and tests | Offline pytest and source diff review | `source_preflight`, focused pytest output | `.artifacts/openspec/native-write-bare-create-foreground/20260630T104800Z/pytest.log` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Runtime apply | 1C configuration import/deploy | No 1C metadata or BSL source is changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | qa-mcp Python runtime only; no configuration apply surface | no runtime apply residual risk |
| Cleanup audit | Foreground-only UI interaction | No record is saved by this change | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | no persisted test data is created in this slice | cleanup required by later save proof |
