# Semantic Map 20260603-opsx-do-semantic-mapping

Date: 2026-06-03.

This map links current expanded read-only corpus case ids to compact
help/meta/EDT references. It is semantic support only: capture frames,
normalized hashes, response markers and replay or direct Python-manager probe
status remain the protocol evidence of record.

## Source Evidence

- Source summary:
  `docs/protocol-research/evidence/semantic-mapping/20260603-opsx-do-semantic-mapping/source_summary.md`.
- Semantic-source inventory:
  `docs/protocol-research/semantic-source-inventory.md`.
- Primary corpus evidence:
  `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`.
- Accepted mapping evidence:
  `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`.

## Mapping Rows

| Case id | Mapping status | Semantic target | Provider sources | Primary wire evidence | Unresolved reason / residual risk |
| --- | --- | --- | --- | --- | --- |
| `active-window-context` | mapped | `TestedApplication.GetActiveWindow`, `TestedClientApplicationWindow`, active `MainFrame/HomePage` window | `help-mcp` platform version `8.3.27.1786` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`; accepted mapping evidence | Metadata object N/A: this row targets the application window, not a configuration object. |
| `active-form-context` | mapped | `Report.ДашбордПродажи.Form.ФормаОтчета`, synonym `Продажи`, form UUID `cb87512b-e166-46bf-8d8f-9a24fa9bc00a`, `TestedForm` | `meta-mcp` config `demo10413` build `2026-05-24T000000Z-demo10413-edt`; `help-mcp` platform version `8.3.27.1786` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`; accepted mapping evidence | Runtime managed-form GUIDs remain dynamic and are not replaced by metadata identity. |
| `form-element-details` | partial | Two current `EditField` chart controls on `Report.ДашбордПродажи.Form.ФормаОтчета`; `TestedFormField` | `meta-mcp` report form source locations; `help-mcp` `TestedFormField` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`; `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/` | Current compact metadata slice does not expose stable form element UUIDs for the two chart controls; keep runtime element names as semantic labels only. |
| `typed-input-field-readonly` | partial | Current `EditField`/typed field family on the active report form; `TestedFormField` | `meta-mcp` report form source locations; `help-mcp` `TestedFormField` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`; `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/` | Reuses the element-detail probe path; needs future metadata element identifiers before becoming a stable fixture target. |
| `button-family-readonly-gap` | unresolved_fixture_gap | Candidate `TestedFormButton` / managed `FormButton` family | `help-mcp` `TestedFormButton` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Current sales dashboard evidence exposes only `EditField` elements; controlled fixture authoring is required before wire capture. |
| `table-family-readonly-gap` | unresolved_fixture_gap | Candidate `TestedFormTable` / managed `FormTable` family | `help-mcp` `TestedFormTable` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Current sales dashboard evidence exposes only `EditField` elements; controlled fixture authoring is required before wire capture. |
| `commandbar-family-readonly-gap` | unresolved_fixture_gap | Candidate command bar family represented by `TestedFormGroup` plus `FormGroupType.CommandBar` or table/form command-bar properties | `help-mcp` `TestedFormGroup`; `help-mcp` `FormGroupType.CommandBar` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Needs a fixture with a visible command bar and read-only state probes; no command execution is in scope. |
| `page-family-readonly-gap` | unresolved_fixture_gap | Candidate page family represented by `TestedFormGroup` plus `FormGroupType.Page` | `help-mcp` `TestedFormGroup`; `help-mcp` `FormGroupType.Page` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Needs a fixture with page groups and read-only state probes; semantic search was unavailable, exact help lookup resolved the page enum. |
| `label-family-readonly-gap` | unresolved_fixture_gap | Candidate label/decorator family represented by `TestedFormDecoration` | `help-mcp` `TestedFormDecoration` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Current sales dashboard evidence exposes only `EditField` elements; controlled fixture authoring is required before wire capture. |
| `checkbox-family-readonly-gap` | unresolved_fixture_gap | Candidate checkbox field represented by `TestedFormField` plus `FormFieldType.CheckBoxField` | `help-mcp` `TestedFormField`; `help-mcp` `FormFieldType.CheckBoxField` | `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/` | Needs a fixture with a checkbox field and read-only state probes; no click or value mutation is in scope. |

## Review Notes

- `active-window-context` and `active-form-context` are accepted protocol
  mappings because repeated wire evidence and probe proof already support
  them, not because of this semantic map.
- `form-element-details` and `typed-input-field-readonly` remain useful
  `EditField` evidence, but metadata element identity is partial.
- All unsupported family rows stay visible and point to fixture planning rather
  than being promoted by help or metadata labels.
- English/transliterated metadata names did not resolve through `meta-mcp`;
  the stable metadata identity is `Report.ДашбордПродажи`.
