# Python Manager Probe `fixture-20260603-085618`

## Scope

This probe was run after the fixture manifest capture to confirm the current
direct Python-manager read-only path still works with the new capture
bootstrap. It is not fixture-family acceptance evidence.

## Result

- Status: `ok`.
- Query: `form-element-details`.
- Source capture: `runtime/protocol-research/captures/20260603-085618/`.
- Active form returned by the probe:
  `Отчет.ДашбордПродажи.Форма.ФормаОтчета`.
- Element families returned by the probe: `EditField` only.
- Element detail count: `2`.
- Evidence status from the package descriptor: `incomplete_hash`.

## Fixture Gap

The current probe API replays fixed captured frame schedules and cannot choose
one of the source-candidate fixture forms. It therefore cannot directly
confirm `fixture-button-readonly`, `fixture-table-readonly`,
`fixture-commandbar-readonly`, `fixture-page-readonly`,
`fixture-label-readonly` or `fixture-checkbox-readonly`.

Raw sent/received payloads and step binaries remain under
`runtime/protocol-research/python-manager-probe/fixture-20260603-085618/`.
