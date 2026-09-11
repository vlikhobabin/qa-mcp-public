# 1C TestClient Protocol Research

This directory documents **how the native 1C TestClient protocol was decoded** — the research internals, not how
to *use* qa-mcp. You do **not** need anything here to use the tool.

> **⚠ Most of this directory is HISTORICAL AUDIT.** It is a reproducible record of the protocol-decode journey
> (early-to-mid June 2026), kept for provenance. Status reports, roadmaps, plans and the "Manager Fixture V1"
> material below describe intermediate states that have since been **superseded**. Read them as history, not as
> current status. Dates in headings indicate vintage.
>
> **Current, live documentation lives in the parent `docs/`:**
> - [`../qa-mcp-tool-reference.md`](../qa-mcp-tool-reference.md) — the consumer reference (the 59 MCP tools).
> - [`../vanessa-mcp-parity.md`](../vanessa-mcp-parity.md) — the Gherkin step library + authoring guide.
> - [`../program-102-native-superset-handoff.md`](../program-102-native-superset-handoff.md) — development handoff.
> - `../../openspec/board/3.inprogress/111-2026-06-22-epic-productize-harden-extend.md` — the active roadmap.
>
> **The still-live docs IN THIS directory** (the closed capture-free protocol epic 82 — decoded model + recipe):
> - [`capture-free-epic-session-handoff.md`](capture-free-epic-session-handoff.md) — START HERE for epic 82.
> - [`capture-free-epic-state.md`](capture-free-epic-state.md) — consolidated state, decoded protocol model, code map, capture recipe.
> - [`capture-free-epic-next-roadmap.md`](capture-free-epic-next-roadmap.md) — the E1–E5 roadmap (now largely delivered via epic 102).
>
> Everything else in this directory (the milestone below, the status reports, the early roadmaps/plans, the
> Manager-Fixture-V1 sections) is **historical**.

## Historical milestone (2026-06-12): mutation decoded, Python manager synthesizes the flow

A real, recoverable business-data mutation (warehouse `НеИспользовать` toggle in
`vanessa_client`) was executed, captured, decoded to a `fully_stable` normalized
form, and reproduced live by the Python manager - the first `accepted_reviewed`
protocol mapping (`TestedFormButton.Click`). The manager now **synthesizes** the
navigation and write commands (open_list / select_row / open_card + the write),
re-targets parameters of **arbitrary length**, **minimizes** the flow to 252
frames (-71%, the essential floor), and the **write-synthesis gate is resolved**
(offset-2 is the per-session ack GUID; `render_form_command` global rebind + a
fresh nonce produces accepted writes). The **7-frame handshake is the irreducible
replay** (its manager-originated GUIDs are client-validated; regenerating them
fails) - but it is below the configuration layer, so the captured handshake works
for any configuration/server/OS; only a different platform protocol version would
need a one-time re-capture. See:

- `scope-tracker.md` - generated full 160-member API status (the progress view).
- `evidence/demo-real-mutation-corpus/20260610-warehouse-donotuse-protocol-capture/`
  - the full chain: `publication_summary.md`, `decode-findings.md`,
  `python_manager_probe_accepted.md`, `native_semantic_navigation.md`,
  `frame_minimization_result.json` and the comparison/acceptance JSONs.
- tools: `compare_probe_reference.py` (stability/acceptance), `scope_tracker.py`,
  `adaptive_replay_probe.py`, `native_navigation_probe.py`; package
  `src/qa_mcp/protocol/{mutation,native_mutation,navigation}.py`.

Documents:

- `breadth-roadmap.md` - the plan to grow accepted API coverage from 1/160
  across the whole inventory (pipeline generalization + bucketed execution).
- `scope-tracker.md` - generated per-member API status across the 160-member
  inventory (accepted_reviewed / accepted_seed / candidate / uncovered).
- `status-report-2026-06-06.md` - manager fixture V1 read-only state, accepted
  replay/probe mappings, pending rows and next route.
- `status-report-2026-06-03.md` - historical replacement-readiness estimate,
  approach review and recommended route.
- `api-corpus-roadmap-2026-06-03.md` - historical roadmap for moving from
  manual frame research to a finite API-driven protocol corpus pipeline; its
  `edt-mcp` references are legacy context, superseded in active work by
  `config-mcp`, `meta-mcp`, `bsl-mcp`, `admin-mcp` and `live-mcp`.
- `interim-summary.md` - current progress, known gaps and near-term estimate.
- `methodology.md` - recommended hybrid research approach.
- `evidence-index.md` - curated compact protocol evidence index.
- `research-plan.md` - imported running plan from the original research.
- `protocol-corpus-runner.md` - corpus runner, manager fixture V1 live-join
  route and acceptance rules.
- `python-protocol-package.md` - package boundary for reusable read-only
  Python protocol APIs.
- `safe-ui-action-scope.md` - safety gate for the first non-mutating UI action
  protocol cases.
- `api-inventory/automated-testing-8.3.27.1786.json` - first
  machine-readable automated-testing API inventory from the available
  `help-mcp` platform help snapshot, including safety classes and explicit
  source gaps.
- `evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/` - compact
  manager fixture V1 reviewed summary and frame-join report for the retained
  dry-run evidence.
- `evidence/manager-fixture-v1-live-smoke/20260605-live-smoke-runtime-gap/` -
  bounded three-command manager fixture V1 smoke result. It is a provider gap,
  not accepted protocol evidence, because the default Vanessa EPF is absent.
- `evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/` -
  current 17-command manager fixture V1 cleanup run with joined traffic ranges,
  normalized hashes and accepted replay/probe rows folded in.
- `evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/` -
  final pending-promotion publication for the current cleanup run. It records
  17 joined rows, 8 accepted rows, 0 newly promoted rows, 9 pending rows and
  blocked V2 live safe-action readiness.
- `evidence/manager-fixture-v1-replay-probe/20260606-cleanup-readonly-fields/` -
  retained replay/probe proof for the version and string field reads.
- `evidence/manager-fixture-v1-replay-probe/20260606-cleanup-commandbar-main/` -
  retained replay/probe proof for the main command bar read.
- `evidence/manager-fixture-v1-replay-probe/20260606-cleanup-summary419-uipath/` -
  retained replay/probe proof for active window, active form, diagnostic
  field-marker rows and pages.
- `evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/` -
  row-by-row classification for the nine pending cleanup rows.
- `evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/` -
  retained negative replay observations and runtime gap for pending-row probes.
- `evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`,
  `evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/`
  and
  `evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/` -
  blocker evidence explaining why no pending row was promoted in the final pass.
- `evidence/manager-fixture-v1-marker-contracts/20260606-promote-candidate-marker-contracts/` -
  manifest/catalog marker-contract correction for five candidate rows, with
  drift check, dry-run manifest and focused proof links.
- `evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/` -
  focused proof after the contract correction. It accepts six former pending
  rows and initially leaves three former pending rows blocked.
- `evidence/manager-fixture-v1-side-channel-count-contracts/20260606-side-channel-count-contracts-focused-proof/` -
  typed side-channel count contract proof for the two diagnostic count rows.
- `evidence/manager-fixture-v1-side-channel-form-path-contract/20260606-side-channel-form-path-focused-proof/` -
  typed side-channel form-path contract proof for the remaining diagnostic
  form-path row.

## Current Manager Fixture V1 State

The baseline cleanup run is
`20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`. All 17 manifest
command windows are joined to proxy traffic. The cleanup publication now has
nine accepted rows after the restored-runtime checkbox proof:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-diag-window-find-field-marker`
- `tm-v1-diag-form-find-field-marker`
- `tm-v1-field-version`
- `tm-v1-field-string`
- `tm-v1-checkbox-true`
- `tm-v1-commandbar-main`
- `tm-v1-pages-main`

A follow-up manifest/catalog correction promoted five candidate marker
contracts and reran a focused proof over active-window plus the nine formerly
pending rows. Six former pending rows are accepted in that focused proof:

- `tm-v1-diag-window-find-form-marker`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

Three diagnostic rows are accepted by typed side-channel contracts:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-get-form-path`

Joined rows without accepted replay/probe or typed side-channel evidence are
not accepted protocol mappings. The diagnostic side-channel rows are explicitly
accepted as manager `case_events.after.result_preview` evidence, not as direct
wire marker observations.

All nine formerly pending V1 readonly rows now have contract-backed accepted
mappings. V2 safe-action work is no longer blocked by the V1 pending-row gap.
The first focused V2 safe-action proof is published as candidate evidence:

- `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-publication/`
- `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/`
- `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/`

It executed `safe-switch-fixture-page-b` and
`safe-focus-existing-edit-string` live and isolated action/background/recovery
frames, but accepted V2 safe-action mappings remain empty until same-action
replay, direct Python-manager probe or accepted typed contract proof exists.

Keep general project documentation out of this directory. It should contain only
protocol research notes, evidence indexes, schemas and roadmaps.
