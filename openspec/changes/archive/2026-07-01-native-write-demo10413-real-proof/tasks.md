## 1. Target guard + stale default

- [x] 1.1 The proof resolves `target_infobase` from the demo10413 env and FAILS CLOSED unless it is
  the demo10413 1cd — via `lifecycle.require_target_infobase(env, "demo10413/1cd", purpose="proof")`
  (live: `TARGET GUARD OK: /opt/ai-dev-suite-for-1c/demo10413/1cd`).
- [x] 1.2 Stale-default concern addressed by the explicit target guard: the proof passes the demo10413
  env and `require_target_infobase` rejects any other base; `DEFAULT_ENV_FILE` stays the lab-wide
  default (changing it globally would break regression/measure/gates) but the vanessa-silent-default
  risk is flagged in the guard helper docstring.
- [x] 1.3 Guard test: `test_require_target_infobase_guards_wrong_base` (demo10413 accepted;
  vanessa_client and missing-INFOBASE_PATH rejected).

## 2. Author the catalog on demo10413 (recoverable)

- [x] 2.1 Pre-apply `cp -p` snapshot of `demo10413/1cd/1Cv8.1CD` (202924032 bytes).
- [x] 2.2 Re-apply `Catalog.ДоговорыКонтрагентов` (ibcmd import from the admin export-after source +
  `ibcmd config apply --force`): rc0, "Новый объект: Справочник.ДоговорыКонтрагентов", DB 194→233M.

## 3. UI create of two contracts

- [x] 3.1 Launched the demo10413 TestClient; created TWO contracts for owner «Корнет ЗАО» from the UI
  (Владелец + Наименование placeholder + Номер договора + Дата договора, saved) using the Changes 1–3
  primitives (`write_form_fields_by_label`, save=True). Both saved (Код 000000001 / 000000002).

## 4. Assert real object-module behaviour

- [x] 4.1 Read both saved records back via the UI card (the demo10413 OData publication targets a
  DIFFERENT infobase and the file base is held by the TestClient, so read-back is UI, not OData) and
  asserted the REAL rules — the module overwrote the placeholder Наименование:
  - contract 1 (QA-C1, 30.06.2026): Наименование = «Договор 30.06.2026 №QA-C1», **Основной = Да** (Истина, first for owner);
  - contract 2 (QA-C2, 15.07.2026): Наименование = «Договор 15.07.2026 №QA-C2», **Основной = Нет** (Ложь, second).
  Non-tautological (saved name ≠ typed placeholder «PLACEHOLDERQA»/«PLACEHOLDER2»).

## 5. Cleanup + restore + evidence

- [x] 5.1 Cleanup returns the owner's contract count to 0 via the snapshot restore (reverts the catalog
  + both contracts).
- [x] 5.2 Restored demo10413 from the pre-apply snapshot — cmp-identical back to 194M (202924032 bytes),
  snapshot removed, no leftovers.
- [x] 5.3 Retained bundle: create/save screenshots (both contracts), proof scripts, apply evidence.
  Evidence root: `.artifacts/openspec/card125-live-do-session/20260701T034037Z/`. Raw dumps/creds kept
  out of git.

## Verification Matrix

See `design.md` → Verification Matrix. Live results (2026-07-01): runtime apply rc0 (194→233M); UI
create of 2 contracts saved; module rules asserted by UI read-back (contract 1 Основной=Да + auto-name,
contract 2 Основной=Нет + auto-name); target guard OK (demo10413/1cd); cleanup via cmp-verified restore
to 194M. Evidence bundle `.artifacts/openspec/card125-live-do-session/20260701T034037Z/`.
