# Breadth Roadmap — growing accepted API coverage

Status: planning (2026-06-12). This is the durable plan for expanding the Python
manager from one accepted protocol mapping to broad coverage of the
160-member automated-testing API.

## Goal and current state

The capture -> decode -> probe -> compare pipeline is proven end to end on one
action (`TestedFormButton.Click`):

1. **capture** — drive the action via the Vanessa manager through the recording
   proxy (the reference/oracle);
2. **decode** — normalize dynamic fields to a `fully_stable` form (two reference
   runs byte-identical);
3. **probe** — the Python manager reproduces the action live (adaptive replay +
   command synthesis), no Vanessa manager in the loop;
4. **compare** — `compare_probe_reference.py --mode probe-ordinal` matches the
   probe's action frames to the Vanessa reference;
5. **promote** — accepted members land in `scope-tracker.md`.

`scope-tracker.md` currently shows **1/160 `accepted_reviewed`** (the warehouse
`НеИспользовать` toggle / `TestedFormButton.Click`). The breadth work runs this
loop systematically across the remaining members.

Denominator (`api-inventory/automated-testing-8.3.27.1786.json`): 160 members —
107 `read_only`, 29 `safe_ui_action`, 9 `mutation`, 11 `agent_runtime`,
4 `unsupported_initial`.

## Acceptance criterion (no overclaim)

A member is `accepted_reviewed` only when the Python-manager probe reproduces the
**same action** as the Vanessa reference with a matching normalized hash
(`probe-ordinal accepted`). Seed/candidate rows stay as such until probed. Real
mutations run only in `vanessa_client`.

## Phase 0 — Generalize the pipeline (enabler) — DONE

The warehouse-specific scenario is generalized; the loop now runs for an
**arbitrary** action given a manifest:

- **Manifest-driven capture**: `run_protocol_capture.ps1 -Scenario
  demo-action-manifest -ActionManifest <file>` drives a per-action step list
  (phases + Vanessa steps + a form-marker to read) and writes
  `action_capture_result.json` with a `phaseTimeline`. Reference manifest:
  `tools/protocol-research/action-manifests/warehouse-donotuse-toggle.json`
  (reproduces the hardcoded scenario; live-validated: 967 frames, 6 phases).
- **Generic compare**: `compare_probe_reference.py` reads
  `action_capture_result.json` and takes the manifest's `actionPhase` via
  `--phase`; the probe (`adaptive_replay_probe.py`) is already generic.
- **Auto-promotion**: `promote_member.py --api <member> --bucket
  accepted_reviewed --evidence <path>` updates `mutation-evidence-map.json` and
  regenerates `scope-tracker.md`.

Per-action loop is now: author a manifest -> capture (x2) -> probe ->
`compare --mode probe-ordinal --phase <actionPhase>` -> `promote_member.py`.

## Phases 1-4 — Execution by bucket (batches of 30-50 rows per capture run)

| Phase | Bucket | Count | Representative members / demo actions | Priority |
| --- | --- | ---: | --- | --- |
| 1 | `mutation` | **DONE 9/9** | Button.Click, Table.AddRow / ChangeRow / DeleteRow / CopyRow / SwitchRowDeleteMark, Window.Close / ExecuteCommand, Decoration.Click (hyperlink fixture) — all `accepted_reviewed` (2026-06-12) | **High** (V3 core) |
| 2 | `safe_ui_action` | **DONE 22 accepted / 7 candidate** | row-nav, cell-nav, SelectAllRows, SetOrder, GotoRow, hierarchy (GoOneLevel/Collapse), Activate (field/table/group/decoration/window), Form item-nav, Group Collapse/Expand, CloseUserMessagesPanel — accepted. Candidates (no driver/target): Table.Expand (dynamic-list), 4 window-nav, Form.Activate, Button.Activate (2026-06-13) | High (V2) |
| 3 | `read_only` | **IN PROGRESS 2 reviewed / 7 seed / 98 uncovered** | Different acceptance class (local reads, no wire opcode) → manager-fixture-v1 **result-contract**, not capture/probe. Runtime healthy; build-out needed (fixture markers, harness timeout/batching, per-member contracts, evidence policy). Plan: `phase3-readonly-plan.md`, card 72 (2026-06-13) | Medium (volume) |
| 4 | `agent_runtime` / `unsupported_initial` | 11 / 4 | Connection / runtime control; ambiguous members as needed | Low |

## Per-batch loop (repeatable)

1. Author a manifest: API member -> concrete demo action -> Vanessa steps.
2. Capture via Vanessa (x2 for `fully_stable`).
3. Decode + Python-manager probe + `probe-ordinal` compare.
4. Accepted -> auto-promote in the tracker; not accepted -> honest
   candidate/blocked with a precise reason.
5. Regenerate `scope-tracker.md` (the visible % toward 100).

## Estimate and bottleneck

By the methodology, ~5-8 batched capture runs cover the whole surface. The
bottleneck is **not** the runs but mapping each API member to a concrete demo
action plus review. The `mutation` bucket (8 members) is the highest-value and
most bounded - do it first.

## Honest caveats

- Each capture is Vanessa-driven (teacher); the probe is the Python manager
  (student), as today.
- The handshake replay does not constrain breadth - it is below the configuration
  layer, so it covers any forms/actions (see
  `evidence/.../handshake_synthesis_finding.json`).
- API-member count is not the same as distinct wire opcodes; many members share
  an opcode, so the true decode unit may be fewer than 160.

## First action

Phase 0 (generalize the capture scenario + auto-promotion). A board card should
own it; the warehouse toggle is the reference implementation to generalize from.
