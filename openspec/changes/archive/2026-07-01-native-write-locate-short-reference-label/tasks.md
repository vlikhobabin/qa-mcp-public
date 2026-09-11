## 1. Harden label localization

- [x] 1.1 Add a short-label point-size fallback to `locate_text` (`src/qa_mcp/protocol/native_xtest.py`):
  on a strict-threshold miss for a short needle (`len(text) <= short_label_chars`), sweep
  `fallback_pointsizes` and accept the lowest-RMSE candidate up to `fallback_max_score`; the fast
  strict primary path is unchanged for longer labels.
- [x] 1.2 Record the chosen localization knob (`path`/`pointsize`/`score`) in a `diag` dict and surface
  it through `write_form_fields_by_label` results (`locate` field).

## 2. Click geometry

- [x] 2.1 The located owner/reference label's click reaches its input on the live create form
  (live-proven: «Корнет ЗАО» lands in «Владелец» on demo10413). Date fields click the input mask via a
  dedicated offset (delivered in `native-write-open-link-date-commit`). Two-pass input-column
  derivation for far-right-aligned short labels (e.g. «Код») is a documented follow-up — see
  `design.md` → Residuals.

## 3. Honest verification labeling

- [x] 3.1 Reference fields report an explicit `selected` check; open-link writes are marked
  `verification: screen_targeted` (located+typed), not a read-back-verified commit. Authoritative
  per-record commit verification is the post-save read-back in `native-write-demo10413-real-proof`.

## 4. Offline tests

- [x] 4.1 `test_locate_text_short_label_fallback`: a short needle just over the strict threshold is
  located via the fallback (measured 0.21 against a real create-form screenshot); long labels stay
  strict; a genuine miss and the fast primary path are covered.

## 5. Live verification (demo10413)

- [x] 5.1 With the catalog re-applied, `write_form_fields_by_label` locates «Владелец» via the fallback
  (`path=fallback, score=0.2105`) and «Корнет ЗАО» + «QA-001» land; «Номер/Дата договора» locate on the
  primary path. Evidence: `.artifacts/openspec/card125-live-do-session/20260701T034037Z/`.
- [x] 5.2 demo10413 restored to the 194M baseline (cmp-identical); evidence path recorded.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner |
| --- | --- | --- | --- | --- | --- | --- |
| managed form (label localize) | `locate_text`, `write_form_fields_by_label` short/reference labels | offline + live | offline fallback test; live «Владелец» located (path=fallback) | `.artifacts/openspec/card125-live-do-session/20260701T034037Z/` | done | qa-mcp |
| managed form (click geometry) | reference/owner label reaches its input | live | «Корнет ЗАО» lands in «Владелец» (selected:true) | `.artifacts/openspec/card125-live-do-session/20260701T034037Z/c1-vladelec-located-kornet-landed.png` | done (owner case); far-column two-pass = follow-up | qa-mcp |
| tool result contract | verification labeled honestly | offline | reference `selected` + `verification: screen_targeted` | (offline) | done | qa-mcp |
