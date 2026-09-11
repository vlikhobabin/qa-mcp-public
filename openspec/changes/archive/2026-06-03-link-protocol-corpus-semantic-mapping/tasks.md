## 1. Mapping Inputs

- [x] 1.1 Confirm the semantic-source inventory from `document-edt-meta-semantic-sources` is present or record the missing dependency as a provider/source gap.
- [x] 1.2 Inspect existing compact corpus evidence for current case ids, element families, UI targets, accepted mappings and unsupported fixture gaps.
- [x] 1.3 Use `meta-mcp` and `help-mcp` where available to identify the demo form, available form elements and tested API object-model terms relevant to current captures.

## 2. Mapping Artifacts

- [x] 2.1 Add a compact semantic map under `docs/protocol-research/evidence/semantic-mapping/<run-id>/` with `case_id`, semantic target, provider source, mapping status, primary evidence path and unresolved reason where applicable.
- [x] 2.2 Keep unmapped or partially mapped corpus rows visible instead of omitting them.
- [x] 2.3 Update `docs/protocol-research/evidence-index.md` and any relevant protocol methodology notes to link the semantic map.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 Run `bin\openspec.cmd validate link-protocol-corpus-semantic-mapping --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/link-protocol-corpus-semantic-mapping docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Current read-only corpus form targets, including active form and element-family gaps | Semantic map from corpus case ids to form/element targets with mapped, partial or unresolved status | Compact semantic map plus existing corpus/accepted-mapping evidence links; no raw provider dumps | `docs/protocol-research/evidence/semantic-mapping/<run-id>/semantic_map.md`; `docs/protocol-research/evidence/corpus/`; `docs/protocol-research/evidence/accepted-mappings/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: current captures expose limited element details and may leave rows partial |
| Metadata object | Demo configuration metadata for forms/elements relevant to corpus rows | `meta-mcp`/help summary connected to each mapped row | Sanitized metadata/help summary with provider id and source build/version when known | `docs/protocol-research/evidence/semantic-mapping/<run-id>/source_summary.md` | required | `/opt/finshtab-1c` | N/A | Medium: stable GUIDs or element names may be unavailable for some rows |
| Delivery or runtime apply | Runtime capture/replay and Python-manager probing | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change adds semantic labels only and does not execute live 1C runtime or mutate delivery state | Low: future fixture capture must still prove wire behavior independently |
