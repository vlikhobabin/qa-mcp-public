# Fixture Classification Summary 20260603-085618

## Inputs

- Corpus evidence:
  `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/`.
- Probe evidence:
  `docs/protocol-research/evidence/python-manager-probe/fixture-20260603-085618/python_manager_probe_result.json`.
- Source readiness:
  `docs/protocol-research/evidence/fixture-sources/20260603-opsx-do-readonly-fixture-source/source_summary.md`.

## Tool Output

The comparison command used one reviewed fixture corpus input and the compact
direct-probe result:

```powershell
python tools\protocol-research\compare_corpus_runs.py docs\protocol-research\evidence\corpus\20260603-085618-fixture-readonly --comparison-id fixture-readonly-20260603-085618 --probe-evidence docs\protocol-research\evidence\python-manager-probe\fixture-20260603-085618\python_manager_probe_result.json --accepted-output-dir docs\protocol-research\evidence\accepted-mappings\fixture-readonly-20260603-085618 --json
```

Result:

- input count: `1`;
- case count: `6`;
- accepted case ids: none;
- analyzer classification counts: `{"incomplete_hash": 6}`;
- accepted mapping output exists but contains no accepted rows.

## Delivery Classification

The analyzer classifies all rows as `incomplete_hash` because every fixture row
has no frame range, request bytes, normalized hash, operation token or response
markers. At the fixture-family delivery level, the rows remain `pending`: a
source candidate exists, but the capture/probe tools do not yet target one of
the candidate fixture forms.

| Case id | Family | Analyzer classification | Delivery status | Accepted | Evidence path | Reason | Next owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fixture-button-readonly` | `Button` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |
| `fixture-table-readonly` | `Table` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |
| `fixture-commandbar-readonly` | `CommandBar` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |
| `fixture-page-readonly` | `Page` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |
| `fixture-label-readonly` | `Label` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |
| `fixture-checkbox-readonly` | `CheckBox` | `incomplete_hash` | `pending` | no | `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/` | No captured fixture request frames or probe join | `project:qa-mcp`, `/opt/vanessa-mcp-stack` |

## Dynamic Fields And Hashes

No dynamic-field or normalized-hash rule is added by this classification. The
fixture rows have no request frames, so there is no reviewed byte range to
normalize and no stable hash to promote.

## Safety

No action/write semantics are accepted. The direct probe result is retained as
read-only probe-path evidence for the current dashboard `EditField` form only.
