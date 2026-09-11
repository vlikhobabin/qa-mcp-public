## Context

The headline product behaviour (auto-built `Наименование` + first-contract-of-owner ⇒ `Основной=Истина`)
lives in the `ДоговорыКонтрагентов` `ПередЗаписью` object module. The predecessor proof never exercised
it: it ran on the retired vanessa_client (stale `DEFAULT_ENV_FILE`, `lifecycle.py:30`), on a different
catalog (owner label «Контрагент», no auto-name module), with tautological asserts. demo10413 is back
to the 194M baseline without the catalog, so the real form must be re-created to prove anything.

Re-apply recipe (proven 2026-06-30, recoverable): the catalog source survives only in
`admin-mcp/.artifacts/e2e-contracts-2026-06-30-resume/import/export-after/` (full dump WITH the
catalog; Configuration.xml diff vs baseline = exactly the one catalog line). Steps: `cp -p` snapshot
1Cv8.1CD → `ibcmd config --database-path=.../demo10413/1cd import files --base-dir=<export-after>
Catalogs/ДоговорыКонтрагентов.xml + Ext/ObjectModule.bsl + Forms/{ФормаСписка,ФормаЭлемента}{.xml,/Ext/Form.xml}
Configuration.xml --user Администратор` → `ibcmd config apply --database-path=... --force --user
Администратор` (rc0, "Новый объект: Справочник.ДоговорыКонтрагентов", 194→233M). Restore = `cp -p`
snapshot back over 1Cv8.1CD (cmp-verify → 194M).

## Goals / Non-Goals

**Goals:**
- A target-guarded proof that fails closed off demo10413.
- A real UI create of two contracts for one owner, asserting the object-module rules through the
  data layer.
- Retained evidence and a cleanup that returns the owner's contract count to 0.

**Non-Goals:**
- Re-implementing the config-mcp/admin import path (reused as a recipe, not owned here).
- The UI write primitives themselves (owned by Changes 1–3, on which this depends).

## Decisions

- **Target guard:** resolve `target_infobase` from the proof env and assert it equals the demo10413
  1cd before any create; fail closed otherwise. Fix/flag `DEFAULT_ENV_FILE` so the default cannot be
  the retired vanessa env.
- **Authoring:** reuse the proven ibcmd import-from-export-after + apply recipe, always preceded by a
  pre-apply snapshot; restore from the snapshot at the end (cmp-verified back to 194M).
- **Assertions:** read the two created records back through the data layer (OData / `qa_mcp.data`),
  comparing `Наименование` to the auto-built value (NOT the literal Description), and `Основной`
  true/false for first/second contract.
- **Owner:** «Корнет ЗАО» (an existing demo10413 Контрагент).

## Risks / Trade-offs

- Mutating run: a controlled apply + a saved UI record. Mitigation: pre-apply snapshot + required
  cleanup + DB cmp/size verification; abort if the target guard fails.
- The proof depends on Changes 1–3 landing (locate «Владелец», owner label from live form, date
  commit); sequence it last.
- Apply side effect: the recipe also restructures `Справочник.ВидыЦен` (observed in the original and
  re-apply); harmless and reverted by the snapshot restore.
- Keep raw infobase dumps, screenshots and credentials out of git; retain only bounded evidence
  under ignored `.artifacts/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner |
| --- | --- | --- | --- | --- | --- | --- |
| runtime apply (re-apply catalog) | demo10413 1cd via ibcmd import+apply | controlled mutation + snapshot | apply rc0 + DB 194→233M; pre-apply snapshot recorded | `.artifacts/openspec/native-write-demo10413-real-proof/<run-id>/apply/` | planned | admin-mcp (recipe) / qa-mcp |
| managed form create | UI create of 2 contracts (Владелец/Номер/Дата, save) | live scenario | scenario log + UI screenshots of both saves | `.artifacts/openspec/native-write-demo10413-real-proof/<run-id>/ui/` | planned | qa-mcp |
| data-layer assert | auto-`Наименование`; first Основной=Истина, second Ложь | live data read | data-assertion.json reading back the real records (non-tautological) | `.artifacts/openspec/native-write-demo10413-real-proof/<run-id>/data-assertion.json` | planned | qa-mcp |
| target guard | proof fails closed off demo10413 | offline/guard test | a non-demo10413 target is rejected; `DEFAULT_ENV_FILE` fixed/flagged | `.artifacts/openspec/native-write-demo10413-real-proof/<run-id>/guard/` | planned | qa-mcp |
| cleanup / rollback | owner contract count → 0; DB restored | live cleanup | cleanup-summary + DB cmp back to 194M baseline | `.artifacts/openspec/native-write-demo10413-real-proof/<run-id>/cleanup/` | planned | qa-mcp |
