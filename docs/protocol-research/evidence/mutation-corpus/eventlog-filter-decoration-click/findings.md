# TestedFormDecoration.Click — candidate (blocked on a config fixture)

> **RESOLVED (2026-06-12):** the member is now `accepted_reviewed` via a hyperlink
> decoration fixture added to `vanessa_client`. See
> `../ext-decoration-hyperlink-click/`. This document is retained for the root-cause
> analysis it captured (why a plain label is rejected).

Phase 1, mutation bucket. This member is **reachable and well-understood** but
**cannot be accepted against the current `vanessa_client` configuration** because
that configuration contains no decoration with `Гиперссылка = Истина`, and the
platform's `Нажатие` method only fires on a hyperlink decoration.

## What was proven

| Field | Value |
| --- | --- |
| API member | `TestedFormDecoration.Click` (method `Нажатие`, no params) |
| Manifest | `tools/protocol-research/action-manifests/eventlog-filter-decoration-click.json` |
| Target form | filter sub-form `ОтборЖурналаРегистрации` of the event-log data processor in `vanessa_client` |
| Decoration | `НадписьВажность` (`ВидДекорацииФормы.Надпись`, unconditionally visible) |

The bootstrap is fully validated against the live TestClient (capture run
`decoration-click-ref1`):

- **step 1** — open the event-log processor main form
  (`Я открываю основную форму обработки "ЖурналРегистрации"`) → `Шаг выполнен успешно`
  (`mcp_act_step_1.json`).
- **step 2** — open the filter sub-form via its command
  (`я нажимаю на кнопку с именем 'УстановитьОтбор'`) → `Шаг выполнен успешно`
  (`mcp_act_step_2.json`).
- **pre_read** — confirms `ОтборЖурналаРегистрации` is the active form (its
  `Важность` table and filter fields are present) (`pre_read_filter_form_active.json`).
- **action** — `я нажимаю на гиперссылку с именем 'НадписьВажность'` → **rejected**
  by the platform (`action_step_rejected.json`):
  `ACTION_FAILED: Ошибка при вызове метода контекста (Нажать): Неподходящий тип
  элемента управления для вызванного действия.`

## Root cause (decisive)

`TestedFormDecoration.Нажатие` is only valid on a decoration whose `Гиперссылка`
property is `Истина`. The Vanessa step's element finder
(`ОставитьВМассивеТолькоПоляГиперссылок`) keeps **any** `ВидДекорацииФормы.Надпись`
regardless of the `Гиперссылка` flag, so the label is found and activated — but the
subsequent `.Нажать()` (`НажатьНаКнопкуФормы` non-mouse-emulation path) is rejected
at the platform layer because the control is an ordinary, non-hyperlink label.

A full `DumpConfigToFiles` of `vanessa_client`
(`runtime/protocol-research/config-dump/`) contains **zero** decorations with
`<Hyperlink>true</Hyperlink>` across every `Form.xml` (config + common forms). The
only label/picture decorations present are plain labels or SSL formatted-string
`<link>` labels (whose clicks route through `URLProcessing` /
`ClickFormattedStringHyperlink`, a different, `unsupported_initial` member — not
`Нажатие`). Every one of those is also behind conditional visibility that is false
for the headless `Администратор` TestClient (role gate, interaction-system gate, or
PWA-support gate).

## To accept this member

Add a **hyperlink-decoration fixture**: one always-visible `LabelDecoration` with
`Гиперссылка = Истина` (and a safe no-op / navigation `OnClick`) on a simple,
nav-reachable form in `vanessa_client`, then re-run this manifest (pointing the
action step at that decoration's name). That is a configuration change to the shared
test base (Designer/extension load + DB restructure, exclusive access, license-drift
risk per the `license-drift-blocker` memory), so it is a deliberate scope decision —
left for the maintainer rather than taken unilaterally.

Status recorded as `candidate` (partial evidence: reachable + understood, action
blocked by config) in `api-inventory/mutation-evidence-map.json`.
