## 1. Source Inventory

- [x] 1.1 Add `docs/protocol-research/semantic-source-inventory.md` with approved `help-mcp`, `meta-mcp` and `edt-mcp` uses, provider owners, source build/version fields and external workspace/snapshot boundaries.
- [x] 1.2 Document the required EDT workspace or metadata snapshot location policy, including that generated EDT workspaces, infobase exports and provider payload dumps stay outside git.
- [x] 1.3 Record how semantic sources can inform corpus case selection and labels while capture, normalization, replay and direct Python-manager probing remain independent.

## 2. Evidence And Indexing

- [x] 2.1 Add or reference a compact provider readiness or provider-gap summary under `docs/protocol-research/evidence/semantic-sources/<run-id>/`.
- [x] 2.2 Update `docs/protocol-research/evidence-index.md` to link the semantic-source inventory evidence without copying raw provider output.
- [x] 2.3 Review `docs/protocol-research/corpus-evidence-contract.md` and update it only if the inventory introduces a new compact field or source-boundary rule.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 Run `bin\openspec.cmd validate document-edt-meta-semantic-sources --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/document-edt-meta-semantic-sources docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Metadata object | `demo10413` metadata/help source inventory and optional source build identifiers | Source inventory with provider ids, owner routes, allowed use and external boundaries | Compact provider readiness or provider-gap summary; no raw metadata payloads | `docs/protocol-research/semantic-source-inventory.md`; `docs/protocol-research/evidence/semantic-sources/<run-id>/source_readiness.md` | required | `/opt/finshtab-1c` | N/A | Low: readiness can drift after capture; evidence records run id/build when known |
| Delivery or runtime apply | EDT workspace/snapshot and generated fixture-output boundary | Documented external/ignored locations and raw-output exclusion policy | Reviewed doc plus diff check proving no generated workspace/export/raw output is committed | `docs/protocol-research/semantic-source-inventory.md`; `git diff --check` output | required | `/opt/edt-lab` | N/A | Low: path may be unresolved on a new machine and must be recorded as a gap |
| Managed form layout | Live managed forms and UI elements | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | This change documents source policy only and does not inspect or mutate form layout | Medium: later mapping/fixture changes must supply form-specific evidence |
