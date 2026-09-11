# Fixture Capture And Probe Summary 20260603-085618

## Commands

Capture command:

```powershell
python tools\protocol-research\protocol_corpus_runner.py --run-capture --capture-scenario form-analysis --case-set fixture-readonly --case-manifest docs\protocol-research\evidence\fixture-plans\20260603-opsx-do-readonly-fixtures\fixture_case_manifest.json --vanessa-epf C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\releases\vanessa\single\vanessa-automation-single-51f920f-windows-screenshot-fixes.epf --json
```

Direct probe command:

```powershell
python tools\protocol-research\python_manager_probe.py --capture-dir runtime\protocol-research\captures\20260603-085618 --manager-templates docs\protocol-research\evidence\templates\20260602-frames08-106-utf16-managedform\manager_frame_templates.json --query form-element-details --output-dir runtime\protocol-research\python-manager-probe\fixture-20260603-085618 --json
```

## Retained Evidence

- Corpus evidence:
  `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/`.
- Raw capture output:
  `runtime/protocol-research/captures/20260603-085618/`.
- Reviewed direct-probe evidence:
  `docs/protocol-research/evidence/python-manager-probe/fixture-20260603-085618/`.
- Raw probe output:
  `runtime/protocol-research/python-manager-probe/fixture-20260603-085618/`.

## Result

The Windows-native `form-analysis` capture completed successfully and wrote
six fixture case rows from the planned manifest. All six rows remain
`pending` because the current runner can load the manifest but cannot open or
select one of the source-candidate fixture forms discovered by
`prepare-controlled-readonly-fixture-source`.

The direct Python-manager probe succeeded against the same lab and capture
bootstrap, but it returned the existing dashboard active form with two
`EditField` details. It does not target `Button`, `Table`, `CommandBar`,
`Page`, `Label` or `CheckBox`, so it is retained as probe-path evidence and a
fixture targeting gap, not as fixture-family acceptance evidence.

## Family Status

| Case id | Family | Capture id | Frame range | Request bytes | Response bytes | Normalized hash | Operation token | Response markers | Replay/probe status | Unresolved reason |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `fixture-button-readonly` | `Button` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |
| `fixture-table-readonly` | `Table` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |
| `fixture-commandbar-readonly` | `CommandBar` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |
| `fixture-page-readonly` | `Page` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |
| `fixture-label-readonly` | `Label` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |
| `fixture-checkbox-readonly` | `CheckBox` | `20260603-085618` | N/A | 0 | 0 | N/A | N/A | none | `pending` | Runner cannot target a candidate fixture form for this family yet |

## Cleanup

`runtime/protocol-research/captures/20260603-085618/capture_summary.json`
records owned-PID cleanup:

- stopped manager pid `15664`;
- stopped proxy pid `19876`;
- stopped TestClient pid `16272`.

The direct probe wrapper started a separate TestClient and wrote
`runtime/protocol-research/python-manager-probe/fixture-20260603-085618/cleanup.txt`,
which records that the owned TestClient PID was stopped.

## Safety

No click, command invocation, checkbox toggle, table edit, text input or
persisted business-data mutation was performed. All retained fixture-family
rows are non-accepted.
