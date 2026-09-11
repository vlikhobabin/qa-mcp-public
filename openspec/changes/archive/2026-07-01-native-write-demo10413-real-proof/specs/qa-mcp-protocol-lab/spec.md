## ADDED Requirements

### Requirement: The owner-create proof is target-guarded to demo10413

The live owner-create proof SHALL resolve its target infobase and FAIL CLOSED unless that target is
the demo10413 file infobase (`/opt/ai-dev-suite-for-1c/demo10413/1cd`, env
`/opt/ai-dev-suite-for-1c/demo10413/.ai/qa-demo10413.env`). A run resolved against any other infobase
(in particular the stale `.ai1c/vanessa-qa-mcp.env` default → retired `vanessa_client`) SHALL be
rejected, not accepted. The stale default SHALL be fixed or flagged so a proof cannot silently run on
a retired infobase.

#### Scenario: Proof rejected on a non-demo10413 infobase

- **WHEN** the proof is launched with a resolved `target_infobase` that is not demo10413
- **THEN** the proof fails closed with a clear target-mismatch diagnostic
- **AND** no UI create or data assertion is recorded as passing

#### Scenario: Proof runs only on demo10413

- **WHEN** the proof resolves `target_infobase` = demo10413 1cd
- **THEN** it proceeds to the UI create and data assertions
- **AND** the live summary records the demo10413 target and env file

### Requirement: The proof asserts the real object-module behaviour

The proof SHALL create two `ДоговорыКонтрагентов` contracts for one owner from the UI and assert the
real object-module rules read back through the data layer: the auto-built
`Наименование == "Договор " + Формат(ДатаДоговора, "ДЛФ=D") + " №" + НомерДоговора`, the first
contract of the owner `Основной=Истина` and the second `Основной=Ложь`. Literal-equals-written
tautologies SHALL NOT count as the assertion.

#### Scenario: Auto-name and first-owner Основной are verified

- **WHEN** two contracts are created from the UI for one owner («Корнет ЗАО») with «Владелец»,
  «Номер договора» and «Дата договора» set and saved
- **THEN** each record's `Наименование` equals the auto-built value (not the literal Description)
- **AND** the first contract reads back `Основной=Истина` and the second `Основной=Ложь`
- **AND** the proof retains UI screenshot, scenario log and data-assertion evidence

#### Scenario: Cleanup returns the owner contract count to zero

- **WHEN** the proof completes
- **THEN** cleanup removes the created contracts and the owner's contract count returns to 0
- **AND** the demo10413 infobase is restored to its pre-apply baseline with no unresolved leftovers
