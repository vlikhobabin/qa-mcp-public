## Why

The predecessor proof (archived `native-write-persistence-cleanup-proof`) is invalid for the headline
goal. Retained evidence (`.artifacts/openspec/native-write-persistence-cleanup-proof/20260630T121500Z/`)
shows it ran against the retired `/opt/1c-dev/vanessa_client` (the stale `.ai1c/vanessa-qa-mcp.env`
default → `DEFAULT_ENV_FILE`, `src/qa_mcp/protocol/lifecycle.py:30`), on a different
`ДоговорыКонтрагентов` whose owner label is «Контрагент», with tautological assertions
(`Наименование == ` the literal typed `Description`; `Основной expected=false`). The real
object-module rules — auto-built `Наименование == "Договор " + Формат(ДатаДоговора,"ДЛФ=D") + " №" +
НомерДоговора` and first-contract-of-owner ⇒ `Основной=Истина` — were never checked.

demo10413 ships WITHOUT the catalog (rolled back to the 194M baseline), so a passing proof can be
produced without exercising the real catalog at all. A real, target-guarded proof is needed.

## What Changes

- The live proof MUST resolve `target_infobase` = `/opt/ai-dev-suite-for-1c/demo10413/1cd`
  (env `/opt/ai-dev-suite-for-1c/demo10413/.ai/qa-demo10413.env`) and FAIL CLOSED if the resolved
  target is not demo10413, guarding against the stale `.ai1c/vanessa-qa-mcp.env` default. Fix/flag
  that stale default so a proof cannot silently run on a retired infobase.
- Author `Catalog.ДоговорыКонтрагентов` on demo10413 (config-mcp/admin re-apply recipe, recoverable
  via a pre-apply snapshot — proven this session: `ibcmd config import files` from the admin
  export-after source + `ibcmd config apply --force`; restore = copy the snapshot back, cmp-verified).
- Create TWO contracts for one owner («Корнет ЗАО») from the UI (set «Владелец», «Номер договора»,
  «Дата договора», save) and assert the REAL rules read back through the data layer: auto-built
  `Наименование`; first contract `Основной=Истина`, second `Основной=Ложь`.
- Retain UI screenshot, scenario log, data assertion and cleanup evidence; cleanup returns the
  owner's contract count to 0.

## Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: add requirements for a target-guarded persistence+cleanup proof that asserts
  the real object-module behaviour and is rejected on any non-demo10413 infobase.

## Impact

- Python manager: the proof harness / live-summary route; `src/qa_mcp/protocol/lifecycle.py:30`
  (`DEFAULT_ENV_FILE`) and any proof path that defaults to it.
- demo10413 authoring/import/apply reuses the existing config-mcp/admin-mcp controlled-mutation recipe
  (not re-implemented here); this change owns the qa-mcp UI write + proof + target guard.
- Depends on `native-write-locate-short-reference-label`, `native-write-owner-label-from-live-form`,
  `native-write-open-link-date-commit` (all three are needed to drive the UI create).
- Live 1C runtime required (demo10413 TestClient + data-layer read). Mutating: a controlled,
  snapshot-recoverable apply + a saved UI record with required cleanup; no broad live-write surface.
