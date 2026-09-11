# Automated Testing API Inventory `8.3.27.1786`

This is the first machine-readable platform-help inventory for the protocol
corpus pipeline.

Source:

- provider: `help-mcp`
- help snapshot: `8.3.27.1786`
- lab runtime baseline: `8.3.27.2130`
- inventory JSON:
  `docs/protocol-research/api-inventory/automated-testing-8.3.27.1786.json`

Coverage:

- 8 automated-testing object surfaces are represented.
- 160 member rows are classified for first-stage planning.
- 6 explicit gap rows are retained instead of silently shrinking the matrix.
- Parameter signatures are not considered complete in this pass.

Primary read-only candidate families:

- `ТестируемоеПриложение.GetActiveWindow`
- `ТестируемоеПриложение.GetObject` / `FindObject`
- `ТестируемаяФорма.GetChildObjects`
- `ТестируемоеПолеФормы.GetDataPresentation`
- `ТестируемаяКнопкаФормы.CurrentEnable`
- `ТестируемаяТаблицаФормы.GetCellText`
- `ТестируемаяГруппаФормы.GetCurrentPage`

Primary safe-action candidates:

- `ТестируемоеОкноКлиентскогоПриложения.Activate`
- `ТестируемаяФорма.GotoNextItem`
- `ТестируемаяТаблицаФормы.GotoRow`
- `ТестируемаяГруппаФормы.Expand`
- `ТестируемаяГруппаФормы.Collapse`

Excluded from the first read-only corpus:

- Runtime/session control: `Connect`, `Disconnect`, UI log recording and
  file-dialog result methods.
- Business or arbitrary handlers: `ExecuteCommand`, `Click`.
- Row mutations: `AddRow`, `ChangeRow`, `DeleteRow`, `CopyRow`,
  `SwitchRowDeleteMark`.
- Ambiguous choices: menu/list choice methods and formatted-string hyperlink
  clicks until recovery semantics are reviewed.

Outcome:

The inventory is ready as an input to manifest planning, but not as accepted
protocol evidence. Accepted rows still require live frame ranges, normalized
hashes and replay or direct probe proof.
