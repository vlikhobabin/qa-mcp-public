## 1. Evidence Inputs

- [x] 1.1 Collect reviewed corpus evidence directories for the fixture capture
  runs from `run-readonly-fixture-capture-probes`.
- [x] 1.2 Collect compact direct Python-manager probe evidence, if available.
- [x] 1.3 Confirm all six planned case ids are present as captured,
  unresolved or blocked rows.

## 2. Classification

- [x] 2.1 Compare repeated fixture corpus evidence when two or more runs
  exist, for example:
  `python tools\protocol-research\compare_corpus_runs.py docs\protocol-research\evidence\corpus\<capture-a>-fixture-readonly docs\protocol-research\evidence\corpus\<capture-b>-fixture-readonly --comparison-id fixture-readonly-<run-id> --probe-evidence docs\protocol-research\evidence\python-manager-probe\<probe-id>\python_manager_probe_result.json --accepted-output-dir docs\protocol-research\evidence\accepted-mappings\fixture-readonly-<run-id> --json`.
- [x] 2.2 If only one fixture run exists, produce a compact classification
  summary that keeps rows non-accepted unless the evidence contract is fully
  satisfied.
- [x] 2.3 Classify each family as `accepted`, `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked` with reason and evidence
  paths.
- [x] 2.4 Record any dynamic-field or normalized-hash divergence without
  adding unreviewed normalizer rules.

## 3. Verification

- [x] 3.1 Verify classification evidence includes capture ids, frame ranges,
  request/response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers and replay/probe status for accepted rows.
- [x] 3.2 Verify unresolved rows include explicit reason and next owner.
- [x] 3.3 Run `scripts\check.ps1`.
- [x] 3.4 Run
  `bin\openspec.cmd validate classify-readonly-fixture-evidence --strict`.
- [x] 3.5 Run
  `git diff --check -- openspec/changes/classify-readonly-fixture-evidence docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live read proof | Fixture corpus and direct-probe evidence for six read-only families | Classification rules and case status table | Corpus comparison, accepted-mapping report or classification summary with unresolved reasons | `docs/protocol-research/evidence/corpus-comparison/fixture-readonly-<run-id>/`; `docs/protocol-research/evidence/accepted-mappings/fixture-readonly-<run-id>/` | required | `project:qa-mcp` | N/A | Medium: one-run evidence or incomplete probe joins may prevent acceptance |
| Delivery or runtime apply | Optional second fixture capture only if repeatability evidence is missing | Repeat-run command plan and cleanup expectation | Compact corpus evidence and cleanup proof when a second run is executed | `docs/protocol-research/evidence/corpus/<capture-id>-fixture-readonly/`; `runtime/protocol-research/captures/<capture-id>/` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | Medium: live repeatability may fail due to lab timing or fixture availability |
| Managed form layout | Form-element families in classification table | Evidence-to-family mapping for each fixture case id | Form tree/source evidence links when classification depends on family identity | `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md` | required | `/opt/vanessa-mcp-stack`, `/opt/edt-lab` | N/A | Medium: ambiguous element identity keeps rows partial |
| Form module or command | Command execution, clicks and input handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Classification covers read-only query evidence only | Medium: accepted read-only command-bar metadata does not validate command action semantics |
