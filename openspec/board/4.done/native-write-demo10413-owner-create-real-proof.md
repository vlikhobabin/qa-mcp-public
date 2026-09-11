# qa-mcp native write: REAL demo10413 owner-create proof (locate + owner-label + date) — correct the invalid vanessa_client proof

## Status
4.done

## Owner
qa-mcp

## OpenSpec Stage
archived

## Order Index
125

## Source
- Follow-up / correction of `openspec/board/4.done/native-write-subordinate-owner-create-cleanup.md`
  (delivered `dfe51e0`, three archived changes 2026-06-30).
- 2026-06-30 fresh-session e2e re-run of `Catalog.ДоговорыКонтрагентов` on **demo10413** (root cockpit, all providers on
  delivered code: qa-mcp `dfe51e0`, config-mcp `c395a09`, admin-mcp `eebefea`). Stages 1–3 GREEN (catalog authored with
  `Владелец` on the element form #15-verified → imported → DB-applied LIVE, 1cd 194→233M); **Stage 4 UI-create did not
  work** and inspection of the prior delivery's retained evidence showed its "live proof" never exercised the real target.

## Summary
The predecessor card is in `4.done` and its requirements are sound, but its **"live create/data/cleanup proof passed"
is invalid for the headline goal**: it ran against the **retired `/opt/1c-dev/vanessa_client`** infobase (a different,
pre-existing `ДоговорыКонтрагентов` catalog), not demo10413, and its data assertions were tautological — so the actual
product behavior (auto-built `Наименование` + first-contract-of-owner ⇒ `Основной=Истина`) was never verified, and on the
real demo10413 catalog the UI create still fails. This card makes the proof real and fixes the three concrete blockers.

## Live Verification (2026-06-30) — both runtime blockers CONFIRMED on the real form
After re-applying the catalog to demo10413 (ibcmd import from the admin `export-after` source + apply; restore from a
pre-apply snapshot, cmp-verified back to 194M), both blockers reproduce **exactly** on the real
«Договоры контрагентов (создание)» form. Evidence:
`.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/` (shot `07-REAL-FORM-*`, `09-real-form-date-empty-*`).

- **Blocker #1 confirmed:** `write_form_fields_by_label` → «Владелец» `targeted:false, "label not located"` (the label is
  visible on the form), while «Номер договора»/«Дата договора» locate fine. Refinement found: even when a short label *is*
  located (e.g. «Код» on Валюты), the fixed `input_offset(170)` from the label center misses the right-aligned input column
  → the value lands in the wrong field, and the tool falsely reports `targeted/all_selected:true`.
- **Blocker #2 confirmed:** typing the date via the tool opens the calendar picker and leaves «Дата договора» empty (no
  commit). The date field itself commits when digits are typed directly into the focused field (proven on the КурсыВалют
  «Период» field), so the failure is the tool's locate+`input_offset` click hitting the calendar button, not the field.
- Note: substitute forms (Валюты/Курсы валют) gave misleading partial signals; faithful repro required the real catalog.

## Findings — invalid prior proof (evidence-grounded)
Retained evidence: `qa-mcp/.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/`
(`live-summary.json`, `data-assertion.json`, `ui_results` block).

- **Wrong target infobase.** `live-summary.json` → `cleanup_route.target_infobase = /opt/1c-dev/vanessa_client`,
  `env_file = .ai1c/vanessa-qa-mcp.env`. The proof ran on the **retired vanessa_client** IB (the stale qa-mcp default env
  target), not demo10413. The done card's own Verify line admits it: "cleanup proof restored `/opt/1c-dev/vanessa_client`
  from a file-infobase snapshot".
- **Wrong catalog / why the UI write "worked" there.** vanessa_client already has a `ДоговорыКонтрагентов` with a
  DIFFERENT schema (fields `Организация`, `ВидДоговора="Продажа"`, `Валюта="EUR"`, `ДатаНачала/ДатаОкончания`, `Подписан`)
  whose **owner field is labelled «Контрагент»**, not «Владелец». `write_form_fields_by_label` targeted+saved there
  (`ui_results.all_targeted/all_selected/saved = true`) precisely because that form's owner label is «Контрагент» — which
  is also why a vanessa-specific alias `(open_link,"reference","Владелец") → "Контрагент"` is hard-coded at
  `src/qa_mcp/mcp_server.py:251`.
- **Tautological assertions.** `data-assertion.json.assertions` assert `Наименование == "QA_CONTRACT_…"` (the literal typed
  into `Description`) and `Основной expected=false, actual=false` ⇒ ok. The **headline rules were never checked**:
  auto-built `Наименование == "Договор <ДЛФ=D> №<номер>"` and **first contract of owner ⇒ `Основной=Истина`**. The data even
  shows the opposite of a real run on our module: first contract `Основной=false`, `ДатаДоговора=0001-01-01` (empty),
  `Наименование` = the literal string. That catalog has no `ПередЗаписью` auto-name/owner module, so the rules can't hold
  there. The done card rationalized `Основной=false` as "matching the live object-module behavior" — true only for the
  wrong catalog.

## Findings — real blockers on demo10413 (qa-mcp tooling, #16-class)
On the real demo10413 `Catalog.ДоговорыКонтрагентов` (owner field labelled «Владелец»), the UI create cannot be driven:

- **`locate_text` fails on the short/reference label.** `read_form_descriptor(open_link="e1cib/data/Справочник.ДоговорыКонтрагентов")`
  opens "Договоры контрагентов (создание)" with all 8 fields incl. an empty editable `Владелец`. But
  `write_form_fields_by_label` reports `"label not located"` for «Владелец» on every attempt (settle_sec up to 6, while the
  longer labels «Номер договора»/«Дата договора» locate fine). Root cause: `locate_text`
  (`src/qa_mcp/protocol/native_xtest.py:252`) is **not OCR** — it renders the label as a Liberation-Sans 13pt needle and
  runs ImageMagick `compare -subimage-search` with `max_score=0.2` (normalized RMSE). The short «Владелец:» needle exceeds
  the threshold vs the on-screen render; longer multi-word labels pass. (LIVE-CONFIRMED 2026-06-30.)
- **Owner-label alias is vanessa-specific.** The `Владелец → Контрагент` alias (`mcp_server.py:251`) is correct only for the
  vanessa_client form; on demo10413 the visible owner label is «Владелец», so the scenario route
  (`_open_link_visible_label`, `mcp_server.py:607`) targets a non-existent «Контрагент» label.
- **Date field does not commit on open_link create.** Text-typing `30.06.2026` into «Дата договора» opens the calendar
  picker (navigated to 30 June 2026) but leaves the field empty — no commit. Without `ДатаДоговора` the auto-name handler
  (`Если ЗначениеЗаполнено(ДатаДоговора) И ЗначениеЗаполнено(НомерДоговора)`) won't build `Наименование`. (LIVE-CONFIRMED
  2026-06-30; the field itself commits on direct digit typing, so the fault is the tool's drive.)
- **No non-locate reference primitive for an arbitrary form.** `set_reference_field` is capture-bound to the card96 fixture
  form, so it can't set `Владелец` on the live demo10413 create form.

## Problem
qa-mcp cannot create a `ДоговорыКонтрагентов` record from the UI on **demo10413** and verify the real object-module
behavior, because (a) `locate_text` can't target short/single-word/reference labels like «Владелец» (and even when a short
label is located, the fixed input_offset misses the input column), (b) the owner label is resolved from a hard-coded
vanessa-specific alias instead of the live form, (c) a date value won't commit on an open_link create form (the click hits
the calendar button), and (d) the create/proof flow defaults to the retired vanessa_client IB and accepts tautological
assertions, so a passing proof can be produced without exercising the real catalog at all.

## Change Set (all delivered + archived 2026-07-01)
1. `native-write-locate-short-reference-label` → `openspec/changes/archive/2026-07-01-native-write-locate-short-reference-label/`
2. `native-write-owner-label-from-live-form` → `openspec/changes/archive/2026-07-01-native-write-owner-label-from-live-form/`
3. `native-write-open-link-date-commit` → `openspec/changes/archive/2026-07-01-native-write-open-link-date-commit/`
4. `native-write-demo10413-real-proof` → `openspec/changes/archive/2026-07-01-native-write-demo10413-real-proof/`

Post-delivery follow-up (added 2026-07-01; DELIVERED + archived 2026-07-01 via `$opsx-do`):
5. `native-write-dynlist-read-refresh-poll` → `openspec/changes/archive/2026-07-01-native-write-dynlist-read-refresh-poll/` — dynlist reads force «Обновить»/F5 refresh + poll-until-stable so a `0` is only ever a genuinely empty list.

## Result
Delivered + LIVE-verified on the real demo10413 `Catalog.ДоговорыКонтрагентов` create form (catalog
re-applied via the ibcmd recipe, restored after). All three tooling blockers fixed and the real proof
passed:
- **Locate «Владелец»** — short-label point-size fallback in `locate_text` locates it (`path=fallback,
  score=0.2105`); «Корнет ЗАО» + «QA-001» land.
- **Owner label** — vanessa `Владелец→Контрагент` alias removed; the owner field targets its real live
  label.
- **Date commit** — `field_mode="date"` clicks the input mask (not the calendar button) and types
  digits; «Дата договора»=30.06.2026 commits.
- **Real proof (target-guarded)** — two contracts for «Корнет ЗАО» created + saved from the UI; the
  `ПередЗаписью` module was proven live by UI read-back: contract 1 Наименование=«Договор 30.06.2026
  №QA-C1» **Основной=Да**, contract 2 Наименование=«Договор 15.07.2026 №QA-C2» **Основной=Нет**
  (non-tautological — the module overwrote the typed placeholders). `require_target_infobase` guard OK
  (demo10413/1cd). Cleanup via cmp-verified snapshot restore to 194M.
- 570 offline tests green; +7 requirements synced into `qa-mcp-protocol-lab`.
- Evidence: `.artifacts/openspec/card125-live-do-session/20260701T034037Z/` (+ the recheck bundle
  `.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/`).
- Residuals (documented follow-ups, non-blocking): two-pass input-column click for far-right-aligned
  short labels (e.g. «Код»); a stubbed offline date-input test + calendar-pick fallback; full pre-save
  read-back in the writer (authoritative check is the post-save read-back).

## Change 1: `native-write-locate-short-reference-label`

### Why
On the real demo10413 create form «Владелец» is not located while longer labels are; and where a short label IS located
(«Код»), the fixed `input_offset(170)` misses the right-aligned input column so the value lands in the wrong field — with a
false-positive `targeted/all_selected` (LIVE-CONFIRMED 2026-06-30).

### Goal
Make short/single-word/reference labels reliably writable from the UI, with honest verification.

### Scope
- Capability: form-field label localization (`qa-mcp-protocol-lab`).
- Harden `locate_text` (`native_xtest.py:252`) for short needles (scale/threshold per length, multi-pointsize, or OCR
  fallback when RMSE > `max_score`); expose the chosen knob.
- Click into the field's input box for short labels (not a fixed offset from the label center).
- Honest verification: success only when the value is verified in the targeted field (read-back / field crop).

### Acceptance
- «Владелец» (and «Код»/«Основной») on the live demo10413 create form locate reliably and write into their own field.
- Offline tests cover a short-label needle the current default would miss, the offset/geometry case, and a missed-write →
  `targeted:false` (no false positive).

### Depends On
- none

### Related
- `openspec/changes/native-write-locate-short-reference-label/`

## Change 2: `native-write-owner-label-from-live-form`

### Why
The owner label is resolved from a hard-coded vanessa alias `Владелец → Контрагент` (`mcp_server.py:251`,
`_open_link_visible_label:607`); on demo10413 the real label is «Владелец», so the scenario route targets a non-existent
«Контрагент».

### Goal
Resolve the owner/reference label from the live form, with no fixture-specific constant.

### Scope
- Capability: open-link reference-field resolution (`qa-mcp-protocol-lab`).
- Remove/parametrize the alias; derive the on-screen owner label from `read_form_descriptor` / the requested field name so
  both «Владелец» (demo10413) and «Контрагент» (vanessa) forms work.

### Acceptance
- The open_link reference write targets the owner field by its real on-screen label on demo10413; no fixture-specific
  owner-label constant remains; offline test asserts label resolution for both forms.

### Depends On
- Change 1 (the scenario route can only target «Владелец» once short/reference-label localization works).

### Related
- `openspec/changes/native-write-owner-label-from-live-form/`

## Change 3: `native-write-open-link-date-commit`

### Why
Typing a date via the open-link route opens the calendar and leaves «Дата договора» empty (LIVE-CONFIRMED 2026-06-30). The
date field itself commits on direct digit typing (proven on КурсыВалют «Период»), so the fault is the locate+offset click
hitting the calendar button.

### Goal
Commit a `DD.MM.YYYY` value on an open_link create form, verified by read-back.

### Scope
- Capability: form date input on open_link create (`qa-mcp-protocol-lab`).
- Drive `ДатаДоговора` so the date commits (masked-input digit typing into the input, or a deterministic calendar pick),
  avoiding the calendar button; integrate with `write_form_fields_by_label` / `write_form_date(open_link=…)`.

### Acceptance
- On the demo10413 create form `ДатаДоговора=30.06.2026` reads back committed (not empty / calendar left open).

### Depends On
- Change 1 (shared input-column click geometry).

### Related
- `openspec/changes/native-write-open-link-date-commit/`

## Change 4: `native-write-demo10413-real-proof`

### Why
The predecessor proof is invalid (wrong IB, wrong catalog, tautological asserts); demo10413 ships without the catalog, so a
passing proof can be produced without exercising the real target.

### Goal
A real, target-guarded demo10413 proof that asserts the actual object-module behavior and is rejected on the wrong IB.

### Scope
- Capability: persistence + cleanup proof with target guard (`qa-mcp-protocol-lab`).
- The live proof MUST use `env_file=/opt/ai-dev-suite-for-1c/demo10413/.ai/qa-demo10413.env` (demo10413 1cd); fail closed
  if the resolved `target_infobase` is not demo10413. Fix/flag the stale `.ai1c/vanessa-qa-mcp.env` default
  (`DEFAULT_ENV_FILE`, `lifecycle.py:30`).
- Author `Catalog.ДоговорыКонтрагентов` on demo10413 (config-mcp/admin re-apply recipe, snapshot-recoverable — proven this
  session: ibcmd import from the admin `export-after` source + apply; restore from snapshot), create TWO contracts for one
  owner («Корнет ЗАО») from the UI (set `Владелец`, `НомерДоговора`, `ДатаДоговора`, save), assert the REAL rules:
  `Наименование == "Договор " + Формат(ДатаДоговора,"ДЛФ=D") + " №" + НомерДоговора`; first contract `Основной=Истина`,
  second `Основной=Ложь`. Retain UI screenshot, scenario log, data assertion and cleanup evidence; cleanup returns the
  owner's contract count to 0.

### Acceptance
- A passing proof exists ONLY when run on demo10413 and ONLY when the auto-name + first-owner⇒`Основной=Истина` assertions
  hold against the live record (read back through the data layer); a run against any non-demo10413 IB is rejected.

### Depends On
- Change 1, Change 2, Change 3.

### Related
- `openspec/changes/native-write-demo10413-real-proof/`

## Change 5: `native-write-dynlist-read-refresh-poll`
> **POST-DELIVERY FOLLOW-UP — added 2026-07-01 after the live re-run; DELIVERED + archived 2026-07-01 via `$opsx-do`
> (`openspec/changes/archive/2026-07-01-native-write-dynlist-read-refresh-poll/`). Delivered: shared
> `_ensure_list_fresh` refresh-and-poll engine (`_force_list_refresh` «Обновить»/F5 + poll-until-stable +
> `_list_zero_reason`/`_list_refresh_summary`) wired into `read_list_grid`/`read_list_row`/`read_list_column` (refresh
> on by default, `refresh=False` opt-out, `read_list_grid(wait_for_rows=N)`) and a refresh-only pass on `search_list`;
> the `0-rows` diagnostic reworked to "empty (refreshed)" vs an honest could-not-refresh/opt-out message. 588 offline
> tests green (9 new dynlist refresh/poll/opt-out/wait_for_rows/empty-vs-not-loaded tests; 2 card-124 tests reworked to
> the new semantics); +2 requirements synced into `qa-mcp-protocol-lab` (190→192). Optional live confirmation deferred
> (offline capture-backed gate is authoritative per the proposal; the false-`0` repro is already retained). The card
> stays in `4.done` (all 5 changes now archived).**

### Why
The 2026-07-01 live re-run's INDEPENDENT list read (`read_list_grid` on the freshly-created auto-generated
`ФормаСписка`) returned a false `0 rows` — **even as the FIRST read after a fresh `launch_test_client`** (so not the
cold-client boundary) — while both persisted contracts were visibly present in a screenshot of that same list. Root
cause is 1C dynamic-list currency: a dynamic list is an async, eventually-consistent view, and a just-created record is
not shown until the list query re-runs (the user-level fix is F5 / the «Обновить» command). The current dynlist read
replays a next-row capture with NO forced refresh and NO retry, so a single early / mis-bound snapshot reports 0. The
primitive even emits "EITHER empty OR cold-boundary violation" — i.e. it cannot disambiguate empty from not-yet-loaded.

### Goal
Make dynlist reads self-refresh and poll-until-stable, so `0 rows` means genuinely empty — never "asked too early" or
"stale open list".

### Scope
- Add a shared `_ensure_list_fresh(open_link)`: issue an explicit «Обновить» (prefer a protocol form-command replay of
  the list's Обновить/F5 command; `send_keys(["F5"])` into the focused list window as the fallback), then poll the row
  read until the count is **stable** (two equal successive reads) or non-zero, up to a bounded timeout.
- Wire it into `read_list_grid` / `read_list_row` / `read_list_column` / `search_list` via that one helper.
- `refresh=True` by default, with an opt-out for the rare test that asserts "row absent WITHOUT a refresh".
- Add a `wait_for_rows` / `expected_min_rows` option so a verification read asserts "≥N rows within T" instead of a
  single snapshot.
- Rework the 0-rows diagnostic: after a forced refresh + settle, report `0` as "empty (refreshed)"; drop the
  cold-boundary guess for the post-refresh path.
- Offline tests for the refresh + poll-until-stable loop and the empty-vs-loading disambiguation.

### Acceptance
- Reading a freshly-created catalog's list (e.g. `ДоговорыКонтрагентов` immediately after a UI create) returns the
  persisted rows, not a false `0`.
- A genuinely empty list still returns `0` after the forced refresh, with no cold-boundary ambiguity in the message.
- `wait_for_rows=N` blocks until ≥N rows are read or the timeout elapses.

### Depends On
- None (independent of Changes 1–4; extends the existing dynlist read primitives).

### Related
- `openspec/changes/native-write-dynlist-read-refresh-poll/` (proposal/design/specs/tasks — created + `--strict` valid)
- Repro (2026-07-01 live re-run): `read_list_grid(open_link="e1cib/list/Справочник.ДоговорыКонтрагентов")` → `0 rows`
  as the first read after launch, while a `capture_screenshot` of the same list showed both rows
  (Код 000000001 «Договор 30.06.2026 …», Код 000000002 «Договор 15.07.2026 …»).

## Scope
- qa-mcp Python runtime + protocol/xtest + scenario engine and their offline tests only.
- demo10413 authoring/import/apply reuses the existing config-mcp/admin-mcp controlled-mutation recipe (not re-implemented
  here); this card owns the qa-mcp UI write + proof, not the platform import path.
- Read-only/UI-create against demo10413 only; no broad live-write surface; cleanup/rollback evidence required before a
  save proof is accepted; no raw runtime logs/screenshots/dumps/credentials committed.

## Acceptance
- On **demo10413**, qa-mcp creates a `ДоговорыКонтрагентов` contract from the UI: `Владелец` set by its real on-screen
  label, `НомерДоговора` and `ДатаДоговора` filled+committed, saved, read back through the data layer.
- The proof asserts the live object-module behavior — auto-built `Наименование` and first-contract-of-owner ⇒
  `Основной=Истина` (second ⇒ `Ложь`) — NOT a literal-equals-written tautology.
- The proof fails closed unless its target is demo10413; the stale vanessa_client default env no longer lets a proof run
  on the wrong infobase.
- Cleanup is retained and returns the owner contract count to 0 with no unresolved leftovers.

## Evidence (this session, read-only)
- Invalid prior proof: `qa-mcp/.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/`
  (`live-summary.json` → vanessa_client target; `data-assertion.json` → tautological asserts, `Основной=false`).
- demo10413 Stages 1–3 GREEN this run: `admin-mcp/.artifacts/e2e-contracts-2026-06-30-resume/`
  (`apply/main-command/evidence.json` → "Новый объект: Справочник.ДоговорыКонтрагентов", DB apply rc0).
- Live re-verification 2026-06-30 (both blockers on the real form, catalog re-applied + restored):
  `qa-mcp/.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/`.

## Next
- run `$opsx-pub openspec/board/4.done/native-write-demo10413-owner-create-real-proof.md` (update docs, scoped commit + push)

## Related
- `openspec/board/4.done/native-write-subordinate-owner-create-cleanup.md` (predecessor; left in `4.done` but **annotated
  2026-06-30** with an invalid-proof correction pointing here — its live proof is superseded by this card)
- `openspec/board/4.done/native-write-engine-config-agnostic-form-create.md`
- `openspec/board/4.done/testclient-launcher-libgcc-and-attach.md` (#1 libgcc — confirmed fixed this run)

## Log
- 2026-06-30T18:40:00Z `$opsx-ff`: live-verified both blockers on the real demo10413 form, decomposed into 4 OpenSpec
  changes (artifacts created + validated --strict), moved card 1.backlog → 2.todo.
- 2026-07-01T04:00:00Z `$opsx-do`: implemented all 4 changes (locate fallback, alias removal, date field_mode, target
  guard + proof); 570 offline tests green; live-verified on the re-applied demo10413 catalog (both contracts saved,
  module rules proven by UI read-back); demo10413 restored to 194M; synced +7 reqs into `qa-mcp-protocol-lab`;
  archived all 4 changes; card → 4.done. (Data-layer read-back was UI, not OData — the demo10413 OData pub targets a
  different infobase. Change 4 premise correction: fill a Наименование placeholder; the module overwrites it.)
- 2026-07-01T05:45:00Z follow-up round (pre-push, architectural correction — OData cannot read a test-client-held base):
  new change `native-write-ui-readback-verification` capturing **#2** two-pass click geometry (short «Владелец»/«Код»
  reach the shared right-aligned input column, not their own under-reaching offset), **#4** honest protocol value-read
  of the writer's OPEN form (`committed:true` only when the value reads back from the form model — the «стал равен»
  read-back, retry past the cold-client boundary — replacing the false `committed==targeted`), and **#1** OData tools
  (`assert_data`/`assert_data_count`/`role_data_matrix`/`ODataClient`) deprecated+guarded for a test-client-held base
  (additive, not removed — cleanup deferred). 578 offline tests green (+5). LIVE-proven on a fresh cold client + the
  re-applied demo10413 `ДоговорыКонтрагентов` create form: all 4 fields clicked the shared column x=378, value-read
  returned all 8 fields, every written field `committed:true` (Наименование=QA-PROOF-125, НомерДоговора=QA-DOG-001,
  Владелец=«Корнет ЗАО», ДатаДоговора=30.06.2026); demo10413 restored to 194M (cmp-identical). Evidence:
  `.artifacts/openspec/card125-followup-readback-live/20260701T054358Z/`. Synced (1 MODIFIED + 3 ADDED reqs) into
  `qa-mcp-protocol-lab`; change archived.
- 2026-07-01T06:00:00Z `$opsx-pub`: scoped commit «Deliver native demo10413 owner-create proof + protocol read-back
  verification» (35 files — the whole card-125 delivery: 5 archived changes + src/tests/spec + README note) pushed to
  `origin/main` (public repo, user-approved). Excluded the pre-existing out-of-scope dirty files
  (`.claude/settings.json`, `native-write-subordinate-owner-create-cleanup.md`) and all runtime evidence
  (`.artifacts/`, `.runtime/`, `.ai/`). README `assert_data` bullet annotated with the test-client-held-base
  deprecation. Card → published.
- 2026-07-01T06:30:00Z post-publish review (independent adversarial pass): confirmed the change clean except the
  read-back matcher. **Fixed HIGH:** `_value_matches_readback` matched a field's value against the WHOLE form's
  values with bidirectional substring → a failed field could borrow an unrelated committed field's value (false
  `committed`). Now each field is confirmed against its OWN read-back value (label→field, «Номер договора»→
  `НомерДоговора`), equivalence = equals / read-back starts-with requested (drops substring-anywhere + backward);
  whole-form check only as fallback. **Fixed LOW/MED:** `verified` now gated on `field_count>0` so a resolved-but-
  empty read is inconclusive (not an authoritative non-commit); `all_committed` requires `verified`. Documented the
  default-value caveat (a date defaulting to today can read back as committed even if unchanged). 579 tests green
  (+2). Pushed as a follow-up scoped commit.
- 2026-07-01 INDEPENDENT re-run on fresh qa-mcp (`/mcp` reconnect → `c909686`): re-authored + imported + applied the
  demo10413 catalog, then created TWO «Корнет ЗАО» contracts FROM THE UI — Владелец via short-label fallback locate,
  date via `field_mode=date` mask, honest read-back. #1 → Основной=Да, #2 → Нет; auto-names built; both persisted
  (list screenshot). Confirms Changes 1–4 live end-to-end. Two side findings: (a) product-authoring — required
  `Наименование` blocked the first UI save because ПроверитьЗаполнение runs before ПередЗаписью; fixed in the catalog's
  object module with `ОбработкаПроверкиЗаполнения` (not a qa-mcp issue); (b) `read_list_grid` false `0 rows` on the
  fresh auto list form → captured as **Change 5** (post-delivery follow-up) above. demo10413 restored to 194M.
- 2026-07-01 `$opsx-ff` (Change 5 only): created OpenSpec change `native-write-dynlist-read-refresh-poll`
  (proposal/design/specs `qa-mcp-protocol-lab` delta/tasks + Verification Matrix); `openspec validate --strict` = valid,
  `git diff --check` clean. Card kept in `4.done` (Changes 1–4 archived); Change 5 pending `$opsx-do`.
- 2026-07-01 `$opsx-do` (Change 5): implemented the shared `_ensure_list_fresh` refresh-and-poll engine
  (`_force_list_refresh` protocol-«Обновить»-preferred/`F5`-fallback + poll-until-stable, `_list_zero_reason`,
  `_list_refresh_summary`) and wired it into `read_list_grid`/`read_list_row`/`read_list_column` (`refresh=True`
  default + opt-out; `read_list_grid(wait_for_rows=N)`), with a refresh-only pass on `search_list`; reworked the
  `0-rows` diagnostic to disambiguate "empty (refreshed)" from an honest could-not-refresh / opt-out message; scrubbed
  the shipped tool docstrings of the internal card token (R&D-scrub gate). Verify: `uv run pytest tests/` = **588
  passed** (9 new dynlist tests; the two card-124 grid tests reworked to the new semantics), `compileall src/qa_mcp`
  OK, `openspec validate --strict` valid, matrix archive-gate `ok`, `git diff --check` clean. Synced +2 requirements
  into `qa-mcp-protocol-lab` (190→192); archived to
  `openspec/changes/archive/2026-07-01-native-write-dynlist-read-refresh-poll/`. Optional live confirm (task 4.3)
  deferred — offline capture-backed gate is authoritative per the proposal; the false-`0` repro is already retained.
  Commit/push intentionally left to `$opsx-pub`.
