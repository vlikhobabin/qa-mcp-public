# 50. V2 First Focused Safe-Action Proof

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
published candidate proof

## Order Index
50

## Source
- 2026-06-07 V2 planning discussion
- V2 safe-action tooling pipeline card
- Client and manager fixture V2 backlog cards

## Summary
Run the first focused manager fixture V2 safe-action proof after the client,
manager and tooling cards are implemented. The first proof should use the
simplest non-mutating fixture actions and publish accepted or candidate
evidence without touching real business data.

## Expected Scope
- Select one or two narrow fixture actions, preferably `switch_page` and/or
  `focus_element`, before attempting button-like behavior.
- Capture pre-read, action, post-read and recovery events.
- Join candidate action frame ranges separately from background refresh and
  recovery traffic.
- Publish compact evidence with normalized hash, request/response sizes,
  dynamic fields and action result markers.
- Attempt replay/probe or typed contract validation where feasible.
- Record accepted versus candidate status explicitly.

## Out Of Scope
- Real demo configuration buttons.
- Business command clicks.
- Text input, checkbox toggles or persisted value mutation.
- Treating a single joined frame range as accepted protocol knowledge without
  replay/probe or typed contract evidence.

## Acceptance
- At least one V2 safe-action case has reviewed compact evidence.
- The action frame range is isolated from bootstrap, background and recovery
  traffic.
- The report states whether the row is accepted or remains candidate, and why.
- V2 docs and evidence index link the proof.

## Change Set
- `openspec/changes/archive/2026-06-07-select-focused-v2-safe-action-subset/`
- `openspec/changes/archive/2026-06-07-capture-focused-v2-safe-action-run/`
- `openspec/changes/archive/2026-06-07-isolate-focused-v2-safe-action-frames/`
- `openspec/changes/archive/2026-06-07-probe-focused-v2-safe-action-contract/`
- `openspec/changes/archive/2026-06-07-publish-focused-v2-safe-action-proof/`

## Verify
- `bin\openspec.cmd validate select-focused-v2-safe-action-subset --strict`
- `bin\openspec.cmd validate capture-focused-v2-safe-action-run --strict`
- `bin\openspec.cmd validate isolate-focused-v2-safe-action-frames --strict`
- `bin\openspec.cmd validate probe-focused-v2-safe-action-contract --strict`
- `bin\openspec.cmd validate publish-focused-v2-safe-action-proof --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes/select-focused-v2-safe-action-subset openspec/changes/capture-focused-v2-safe-action-run openspec/changes/isolate-focused-v2-safe-action-frames openspec/changes/probe-focused-v2-safe-action-contract openspec/changes/publish-focused-v2-safe-action-proof openspec/board`

## Archive
- `openspec/changes/archive/2026-06-07-select-focused-v2-safe-action-subset/`
- `openspec/changes/archive/2026-06-07-capture-focused-v2-safe-action-run/`
- `openspec/changes/archive/2026-06-07-isolate-focused-v2-safe-action-frames/`
- `openspec/changes/archive/2026-06-07-probe-focused-v2-safe-action-contract/`
- `openspec/changes/archive/2026-06-07-publish-focused-v2-safe-action-proof/`

## Related
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/board/4.done/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `openspec/changes/archive/2026-06-07-select-focused-v2-safe-action-subset/`
- `openspec/changes/archive/2026-06-07-capture-focused-v2-safe-action-run/`
- `openspec/changes/archive/2026-06-07-isolate-focused-v2-safe-action-frames/`
- `openspec/changes/archive/2026-06-07-probe-focused-v2-safe-action-contract/`
- `openspec/changes/archive/2026-06-07-publish-focused-v2-safe-action-proof/`
- `docs/protocol-research/evidence/accepted-mappings/safe-action-20260603-134132/`
- `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-publication/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-first-focused-proof-20260607/`

## Result
done: first focused V2 safe-action proof published as candidate evidence. The
run executed 2 reviewed non-mutating rows, retained 12 phase events, isolated
action/background/recovery frame ranges, recorded normalized hash candidates
and published an explicit proof decision with 2 candidate rows and 0 accepted
rows.

## Next
- Future work: implement same-action V2 replay/direct-probe or stronger typed
  contract proof before promoting these rows to accepted mappings. Demo real
  buttons, text input, value toggles and business commands remain later
  mutation/recovery cards.

## Change Plan Notes
Change order:
1. `select-focused-v2-safe-action-subset`
2. `capture-focused-v2-safe-action-run`
3. `isolate-focused-v2-safe-action-frames`
4. `probe-focused-v2-safe-action-contract`
5. `publish-focused-v2-safe-action-proof`

## Change 1: `select-focused-v2-safe-action-subset`

### Why
The first proof needs a very small reviewed input set before any live V2 action
is attempted.

### Goal
Select one or two executable manager fixture V2 safe-action rows, preferably
`switch_page` first and `focus_element` second, with all safety and recovery
fields present.

### Scope
- Review the archived client V2 target map, manager V2 catalog and V2 tooling
  manifest contract.
- Keep only rows with `mutates_business_data=false`, an allowlisted action
  family, target marker, pre-state, post-state, recovery expectation and
  expected action result markers.
- Record rejected or deferred rows with reason, owner and residual risk.

### Acceptance
- The selected subset is no larger than two rows.
- Every selected row is reviewed and executable input for the manager V2
  runner.
- No button-like, text input, checkbox/value toggle or business command row is
  selected.

### Depends On
- none

### Related
- `openspec/changes/select-focused-v2-safe-action-subset/`

### Notes For `$openspec-ff-change`
- This change permits a focused proof run only; it does not accept protocol
  mappings.

## Change 2: `capture-focused-v2-safe-action-run`

### Why
The selected subset needs live phase-aware evidence before frame isolation or
acceptance review can mean anything.

### Goal
Run the manager fixture V2 safe-action scenario for the selected subset and
retain pre-read, action, post-read and recovery events without committing raw
runtime output.

### Scope
- Execute only the reviewed focused subset through the Windows-native
  `manager-fixture-v2-safe-action` path.
- Retain ignored runtime output under `runtime/protocol-research/`.
- Publish compact capture summaries under `.artifacts/openspec/...` or reviewed
  docs paths without raw TCP payloads.

### Acceptance
- The run records pre-read, action-start, action-end, post-read and recovery or
  recovery-read events for each attempted row.
- The client fixture returns to baseline or a documented known state after each
  row.
- Unsafe or unavailable rows fail closed with typed status.

### Depends On
- `select-focused-v2-safe-action-subset`

### Related
- `openspec/changes/capture-focused-v2-safe-action-run/`

### Notes For `$openspec-ff-change`
- This is the first live capture step; it must not broaden into demo buttons or
  mutating actions.

## Change 3: `isolate-focused-v2-safe-action-frames`

### Why
The proof must separate action traffic from bootstrap, background refresh and
recovery traffic before any protocol claim is reviewed.

### Goal
Join each selected action event to a candidate action frame range, keeping
background and recovery ranges explicit.

### Scope
- Use the V2 reporter/frame-join tooling on the focused run output.
- Record action frame range, background ranges, recovery range, request/response
  sizes, dynamic fields and normalized hash candidates.
- Mark ambiguous joins as candidate, partial, timeout, rejected or blocked
  rather than accepted.

### Acceptance
- Each reviewed row has an explicit action frame range or explicit non-accepted
  reason.
- Background and recovery traffic are not merged into the action range.
- Dynamic fields and normalized hash candidates are preserved compactly.

### Depends On
- `capture-focused-v2-safe-action-run`

### Related
- `openspec/changes/isolate-focused-v2-safe-action-frames/`

### Notes For `$openspec-ff-change`
- Frame isolation alone is candidate evidence only.

## Change 4: `probe-focused-v2-safe-action-contract`

### Why
Accepted V2 safe-action status requires more than a joined frame range.

### Goal
Attempt replay/probe or typed contract validation for the focused row and record
whether the row can be accepted or must remain candidate.

### Scope
- Select the feasible proof route for each focused row: replay, direct
  Python-manager probe or typed contract validation.
- Preserve normalized hash, dynamic fields, operation token and action result
  markers where available.
- Keep rows non-accepted when proof is infeasible or incomplete.

### Acceptance
- The proof attempt is retained with compact evidence and no raw replay payloads
  in reviewed git.
- Accepted status is used only when replay/probe or typed contract evidence is
  reviewed.
- Candidate status states the missing proof and residual risk.

### Depends On
- `isolate-focused-v2-safe-action-frames`

### Related
- `openspec/changes/probe-focused-v2-safe-action-contract/`

### Notes For `$openspec-ff-change`
- A failed or infeasible proof attempt is an acceptable result when the row is
  clearly labeled candidate.

## Change 5: `publish-focused-v2-safe-action-proof`

### Why
The lab needs a durable first V2 proof record that downstream V3/V4 and demo
pilot cards can cite safely.

### Goal
Publish the focused proof decision, evidence links, accepted/candidate status
and residual risk in protocol docs and evidence indexes.

### Scope
- Publish compact proof report and accepted-mapping or candidate outputs.
- Update V2 docs, evidence index and status/readiness references.
- Link ignored runtime paths only as sanitized summaries.

### Acceptance
- At least one row has reviewed compact evidence.
- The proof states accepted versus candidate status and why.
- V2 docs and evidence index link the proof and preserve the V2 safety
  boundary.

### Depends On
- `probe-focused-v2-safe-action-contract`

### Related
- `openspec/changes/publish-focused-v2-safe-action-proof/`

### Notes For `$openspec-ff-change`
- This is publication and status sync only; real demo button pilots remain in
  later cards.

## Log
- 2026-06-07T00:00:00Z card created
- 2026-06-07T18:08:54Z fast-forwarded into five OpenSpec changes and moved to
  `2.todo`
- 2026-06-07T18:42:23Z delivered and archived
  `select-focused-v2-safe-action-subset`; `capture-focused-v2-safe-action-run`
  is blocked at the live-run gate with dry-run evidence retained under
  `runtime/protocol-research/captures/20260607-first-focused-v2-safe-action-dry-run/`
  and blocked live summary under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-capture-gate/`
- 2026-06-07T19:18:11Z delivered live focused capture
  `20260607-first-focused-v2-safe-action-live-runner-2`; compact frame-join
  evidence retained under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/`
- 2026-06-07T19:40:00Z published candidate proof with accepted-mapping output
  intentionally empty under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-publication/`
  and
  `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-first-focused-proof-20260607/`
