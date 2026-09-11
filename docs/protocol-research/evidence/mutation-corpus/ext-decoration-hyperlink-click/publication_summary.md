# TestedFormDecoration.Click — accepted (Phase 1, breadth)

The sixth accepted mutation mapping, and the second outside the tabular-section
family (after Window.Close). It unblocks the member that was previously recorded as
`candidate` (see `../eventlog-filter-decoration-click/findings.md`): the action
itself was always reachable, but the demo configuration had no decoration with
`Гиперссылка = Истина`, and the platform's `Нажатие` method only fires on a hyperlink
decoration.

| Field | Value |
| --- | --- |
| API member | `TestedFormDecoration.Click` (method `Нажатие`) |
| Action | click a hyperlink label decoration |
| Manifest | `tools/protocol-research/action-manifests/ext-decoration-hyperlink-click.json` |
| Target | extension data processor `Расш1_Обработка1` (in `Расширение1`) on `vanessa_client` |
| `mutates_business_data` | false (the `OnClick` handler only calls `Сообщить`) |

## The fixture that unblocked it

A configuration fixture was added to `vanessa_client` (the TestClient's base, not
the manager — the TestClient renders its own config's forms): extension
`Расширение1` with data processor `Расш1_Обработка1`, whose main form carries two
`LabelDecoration`s with `Гиперссылка=Истина` — `Декорация1` ("Кликабельная ссылка 1")
and `Декорация2` ("Кликабельная ссылка 2"). Each `OnClick` handler only calls
`Сообщить(...)`, so the click is a real platform action with zero persistence — the
cleanest possible mutation target (like Window.Close). The fixture form module is
preserved here as `fixture_form_module.bsl`.

The earlier eventlog-filter attempt clicked a **plain** label and the platform
rejected it (`Неподходящий тип элемента управления для вызванного действия`),
proving `Нажатие` requires `Гиперссылка=Истина`. With this fixture the action step
executes.

## Loop result

- **bootstrap/action**: open `Обработка.Расш1_Обработка1` main form
  (`Я открываю основную форму обработки`), then click `Декорация1`
  (`я нажимаю на гиперссылку с именем 'Декорация1'`). Both steps succeed.
- **stability** (ref1 vs ref2, phase=action) → **`fully_stable`**
  (`all_hashes_match`, residual 0, `stability_ref1_vs_ref2.json`).
- **probe**: `adaptive_replay_probe.py` reproduced it live, **125/125** exchanges,
  zero divergence (`adaptive_replay_summary.json`), single clean connection (the
  `probe_runner.ps1` ready-file fix from the ChangeRow work).
- **acceptance** (probe-ordinal, phase=action) → **`accepted`**, both directions
  hash-match, `structural_match` (`python_manager_acceptance.json`).
- **promote** → `accepted_reviewed` (mutation **6/9**, total 6/160).

Raw captures stay under ignored `runtime/protocol-research/captures/`.
