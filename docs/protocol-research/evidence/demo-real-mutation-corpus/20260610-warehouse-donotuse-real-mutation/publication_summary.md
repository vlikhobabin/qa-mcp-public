# Demo Real Mutation — Executed (Warehouse "Не использовать" toggle)

Run id: `20260610-warehouse-donotuse-real-mutation`

## Decision

The first **real, recoverable business-data mutation** on a real demo form was
executed and confirmed. This breaks the prior `blocked` "successful nothing"
result of card 61.

A boolean attribute on a real catalog element was toggled, written to the
`vanessa_client` database, verified by an independent database reread, then
restored to its original value and verified again.

| Field | Value |
| --- | --- |
| Infobase | `C:\1C_BASES\vanessa_client` (disposable demo copy) |
| Object | `Справочник.Склады`, element `Средний` (code `000000003`) |
| Form | `Справочник.Склады.ФормаОбъекта` |
| Field | `НеИспользовать` ("Не использовать"), boolean |
| Operation family | `catalog_boolean_attribute_toggle` |
| `mutates_business_data` | `true` |
| Runtime route | vanessa-mcp reference oracle (manager pid 3228 + TestClient pid 20020) |
| Pre-state | `Нет` (false) |
| After mutation + DB reread | `Да` (true) — **persisted** |
| After recovery + DB reread | `Нет` (false) — **restored** |
| Residual demo data | none |
| Accepted protocol mapping | empty (intentional, see Scope) |

## Executed Sequence

1. Brought up the lab runtime (vanessa manager + TestClient on `vanessa_client`)
   via the vanessa-mcp lazy backend, connected the TestClient profile.
2. Navigated `Товарные запасы → Склады`, opened element `Средний`.
3. Read pre-state from the opened object form: `НеИспользовать = Нет`.
4. **Mutation:** set the `НеИспользовать` flag to true, verified in-form, pressed
   `Записать` (real write to the database).
5. **Persistence proof:** pressed `Перечитать` (reload object from the database,
   discarding form state) → `НеИспользовать = Да`. The new value came from the DB.
6. **Recovery:** cleared the `НеИспользовать` flag, pressed `Записать`, pressed
   `Перечитать` → `НеИспользовать = Нет`. Original state restored from the DB.
7. Closed the form with `Записать и закрыть`.

## Proof Class

`same_channel_db_reread`: after every write the object was reloaded from the
database (`Перечитать`) and the reloaded value matched the intended state. This
proves the write reached persistent storage, not just the form buffer.

An independent-channel probe via the live-mcp COM connection `client` was
attempted but the COM connector rejected credentials (its configured user/
password is not aligned with the empty-password TestClient user). That is a
separate connection-config concern and does not weaken the same-channel reread
proof. Aligning the COM credentials would add a fully independent read channel
and is a cheap follow-up.

## Scope And Honest Limitation

This run proves two things that were previously unproven end to end:

- the lab runtime can be brought up and driven against the real demo copy, and
- a real, reviewed, recoverable business-data mutation can be performed and
  cleaned up with database-level before/after evidence.

It does **not** yet decode a TestClient protocol frame. The action ran through
the vanessa **reference oracle** (the separate Vanessa TestManager), not through
the qa-mcp capture proxy, so no normalized protocol frames were captured. No
`accepted` protocol mapping is claimed; accepted output stays empty.

## Next Step (protocol decode of the same action)

To convert this proven action into protocol evidence, run the **same**
`catalog_boolean_attribute_toggle` through the qa-mcp capture pipeline
(`tools\protocol-research\run_protocol_capture.ps1`), which owns the TestClient
exclusively through the proxy (15382 → 15381) and captures frames:

1. Add a real-demo mutation command kind to the manager harness that opens
   `Справочник.Склады` element `Средний`, toggles `НеИспользовать`, writes,
   rereads and restores — mirroring the steps proven here.
2. Capture action / background / recovery frame ranges through the proxy.
3. Compare the captured frames against this vanessa-reference run to seed and
   then auto-confirm the API↔frame mapping (the reference oracle is the
   automatic comparison source, replacing manual seed review).

No raw captures, screenshots, platform logs or live data rows are included in
reviewed git.
