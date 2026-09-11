# 07. Manager Fixture V1: Live Corpus Pipeline

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
07

## Source
- 2026-06-05 protocol research planning session
- `openspec/board/4.done/05-2026-06-04-manager-fixture-v1-readonly-runner.md`
- `docs/protocol-research/api-corpus-roadmap-2026-06-03.md`
- `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/`
- `tools/protocol-research/run_protocol_capture.ps1`
- `tools/protocol-research/protocol_corpus_runner.py`
- `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\`
- `C:\1C_BASES\EDT\vanessa_qa\vanessa_client\src\DataProcessors\ФикстураПротоколаTestClient\`

## Summary
Turn the manager fixture V1 work from source/dry-run readiness into a real
Windows-native live corpus pipeline. The pipeline must run the dedicated
manager harness against the client fixture through the TCP proxy, preserve
manager side-channel events and proxy traffic under one run id, join
read-only command boundaries to frame ranges, generate normalized corpus rows
and run the first small live smoke before the full read-only command catalog
is expanded.

This card is a prerequisite for manager fixture V2 safe-action work. V2 should
not start until V1 can produce live read-only frame evidence from the custom
manager harness instead of Vanessa MCP smoke probes.

## Current Gaps
- The retained manager V1 run is `dry_run_ok`: no `traffic.jsonl`, no frame
  ranges, no normalized hashes, no replay or direct Python-manager proof. The
  published frame-join report has five `blocked` rows, one `unresolved` row
  and no accepted case ids.
- `run_protocol_capture.ps1` has a `manager-fixture-v1-readonly` scenario, but
  the live branch currently executes standard Vanessa MCP smoke probes rather
  than invoking the custom manager harness as the source of all read-only
  case commands.
- `protocol_corpus_runner.py` does not yet accept
  `manager-fixture-v1-readonly` as `--capture-scenario`.
- The manager BSL source has a read-only command catalog and a function for
  one command, but it still needs a complete manifest-driven run loop that
  loads the manifest, connects through the proxy, executes every command and
  writes before/after events plus final result output.
- The PowerShell manifest and BSL command catalog are out of sync: the capture
  runner currently seeds six commands while the manager harness source defines
  eleven V1 commands.
- `docs/protocol-research/api-inventory/automated-testing-*.json` is still
  absent even though the API corpus roadmap treats the help-derived inventory
  as an input to the industrial corpus pipeline.
- The default Vanessa EPF path
  `releases\vanessa\single\vanessa-automation-single-51f920f-windows-screenshot-fixes.epf`
  is absent in this repository, so the current live capture route cannot
  start as-is without either restoring the runtime asset or adding an explicit
  operator-supplied path/preflight gap.

## Expected Scope
- Finish the manager harness run loop in `ProtocolFixtureTestManager`.
- Align the PowerShell-generated manifest with the manager BSL command
  catalog, or generate both from a single reviewed command list.
- Update `tools/protocol-research/run_protocol_capture.ps1` so the
  `manager-fixture-v1-readonly` live scenario launches the custom manager
  harness path, passes run id, proxy port, output directory and manifest path,
  and keeps Vanessa MCP probes only as optional/bootstrap evidence.
- Make the live route fail closed when the required Vanessa EPF/runtime asset
  is missing, while recording a compact provider/runtime gap if the operator
  cannot supply it.
- Extend `tools/protocol-research/protocol_corpus_runner.py` and reporting to
  accept manager fixture V1 captures and join `case_events.jsonl` with
  `traffic.jsonl`.
- Generate normalized corpus rows for joined manager V1 read-only cases.
- Run and publish a first bounded live smoke with two or three read-only
  commands before expanding to the full V1 command catalog.
- Generate and review the first automated-testing API inventory from
  `help-mcp` or the approved platform help source.

## Out Of Scope
- Safe UI action protocol acceptance.
- Text input, clicks, checkbox toggles, table edits, page switches or command
  execution as accepted protocol mappings.
- Business object writes, posting, saving, data exchange or settings mutation.
- Replacing Vanessa Automation as a full runtime manager.
- Promoting any mapping without frame ranges, dynamic-field evidence,
  normalized hashes and replay or direct Python-manager proof.

## Acceptance
- A non-dry-run `manager-fixture-v1-readonly` capture produces `traffic.jsonl`,
  `manager_harness_manifest.json`, `case_events.jsonl` and
  `manager_harness_result.json` under one runtime run directory.
- The manager harness, not Vanessa MCP smoke probes, executes the selected
  read-only case commands through the proxy TestClient port.
- The first live smoke executes two or three read-only commands and records
  before/after events for each command.
- Frame/chunk join evidence maps each smoke command to reviewed manager and
  client ranges, or records a precise unresolved reason per command.
- At least one smoke command produces a compact corpus row with non-null frame
  range, request size, response size and normalized hash; rows without
  sufficient evidence remain visible as `pending`, `partial`, `blocked` or
  another explicit non-accepted status.
- The PowerShell manifest and BSL catalog contain the same reviewed V1 command
  ids for the selected smoke scope.
- Replay or direct Python-manager proof is attempted for any command whose
  request family is supported by current tooling; missing support is recorded
  as `unsupported` or `pending`, not accepted.
- The reviewed evidence summary links the live run id, runtime paths, join
  report, corpus rows, unresolved gaps and raw-output policy.
- Cleanup stops only TestClient, proxy and manager PIDs created by the runner.
- If the required Vanessa EPF/runtime asset is absent, the card records a
  compact provider/runtime gap and does not claim live protocol evidence.

## Change Set
- `openspec/changes/archive/2026-06-05-finish-manager-fixture-v1-harness-run-loop/`
- `openspec/changes/archive/2026-06-05-align-manager-fixture-v1-command-catalog/`
- `openspec/changes/archive/2026-06-05-execute-manager-fixture-v1-live-capture/`
- `openspec/changes/archive/2026-06-05-join-manager-fixture-v1-case-events/`
- `openspec/changes/archive/2026-06-05-publish-manager-fixture-v1-live-smoke-evidence/`
- `openspec/changes/archive/2026-06-05-generate-automated-testing-api-inventory/`

## Verify
- `openspec validate finish-manager-fixture-v1-harness-run-loop --strict`
- `openspec validate align-manager-fixture-v1-command-catalog --strict`
- `openspec validate execute-manager-fixture-v1-live-capture --strict`
- `openspec validate join-manager-fixture-v1-case-events --strict`
- `openspec validate publish-manager-fixture-v1-live-smoke-evidence --strict`
- `openspec validate generate-automated-testing-api-inventory --strict`
- `openspec validate --all`
- `git diff --check -- openspec/changes openspec/board`

## Archive
- `openspec/changes/archive/2026-06-05-finish-manager-fixture-v1-harness-run-loop/`
- `openspec/changes/archive/2026-06-05-align-manager-fixture-v1-command-catalog/`
- `openspec/changes/archive/2026-06-05-execute-manager-fixture-v1-live-capture/`
- `openspec/changes/archive/2026-06-05-join-manager-fixture-v1-case-events/`
- `openspec/changes/archive/2026-06-05-publish-manager-fixture-v1-live-smoke-evidence/`
- `openspec/changes/archive/2026-06-05-generate-automated-testing-api-inventory/`

## Related
- `openspec/board/4.done/05-2026-06-04-manager-fixture-v1-readonly-runner.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `docs/protocol-research/api-corpus-roadmap-2026-06-03.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/runtime_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/frame_join_report.md`
- `tools/protocol-research/run_protocol_capture.ps1`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/report_manager_fixture_v1.py`
- `openspec/changes/archive/2026-06-05-finish-manager-fixture-v1-harness-run-loop/`
- `openspec/changes/archive/2026-06-05-align-manager-fixture-v1-command-catalog/`
- `openspec/changes/archive/2026-06-05-execute-manager-fixture-v1-live-capture/`
- `openspec/changes/archive/2026-06-05-join-manager-fixture-v1-case-events/`
- `openspec/changes/archive/2026-06-05-publish-manager-fixture-v1-live-smoke-evidence/`
- `openspec/changes/archive/2026-06-05-generate-automated-testing-api-inventory/`

## Result
Implemented and archived all six changes. The manager V1 harness now has a
manifest-driven run loop, the BSL and PowerShell command catalogs are aligned,
the live capture route invokes the custom harness path and fails closed on the
missing Vanessa EPF, manager case events can be joined into corpus rows, the
bounded three-command smoke publishes a provider/runtime gap, and the first
help-derived automated-testing API inventory is available under
`docs/protocol-research/api-inventory/`.

No live protocol mapping was accepted from this card because the default
Vanessa EPF runtime asset is still absent. Full V1 catalog expansion remains
blocked until the EPF/runtime profile is restored and a bounded smoke produces
joined frame ranges, normalized hashes and replay or probe status.

## Next
- Restore or configure the expected Vanessa EPF/runtime asset and rerun the
  three-command `manager-fixture-v1-readonly` smoke before expanding to the
  full V1 read-only command catalog.

## Change 1: `finish-manager-fixture-v1-harness-run-loop`

### Why
The manager V1 source currently defines helpers and one-command execution, but
not the complete manifest-driven loop required for live corpus generation.

### Goal
Finish the manager harness run loop that loads a manifest, connects through
the proxy, executes read-only commands and writes event/result output.

### Scope
- Manager harness BSL source in `ProtocolFixtureTestManager`.
- Manifest loading and validation.
- Before/after `case_events.jsonl`.
- `manager_harness_result.json`.
- Read-only rejection policy.

### Acceptance
- A valid manifest executes in order through the proxy port.
- Each command emits before and after events.
- Failures are retained as command/run evidence.
- Non-read-only commands fail closed.

### Depends On
- none

### Related
- `openspec/changes/finish-manager-fixture-v1-harness-run-loop/`

### Notes For `$openspec-ff-change`
- Preserve V1 read-only boundaries and do not introduce action semantics.

## Change 2: `align-manager-fixture-v1-command-catalog`

### Why
The PowerShell manifest seeds six commands while the BSL catalog defines eleven.
Live evidence needs one reviewed command catalog.

### Goal
Align the V1 read-only command catalog across BSL source, PowerShell manifest
generation and reviewed evidence.

### Scope
- Reviewed command ids, command kinds, target markers and expected markers.
- First-smoke subset definition.
- Offline catalog drift checks where feasible.

### Acceptance
- BSL catalog and generated manifest use the same reviewed command ids.
- The smoke subset is a filter over the reviewed catalog, not a competing
  catalog.
- Action and mutation command kinds remain rejected.

### Depends On
- none

### Related
- `openspec/changes/align-manager-fixture-v1-command-catalog/`

### Notes For `$openspec-ff-change`
- Keep target-map and live-open evidence linked as semantic support, not
  protocol proof.

## Change 3: `execute-manager-fixture-v1-live-capture`

### Why
The existing live scenario still uses Vanessa MCP smoke probes as the primary
driver. The custom manager harness must become the corpus generator.

### Goal
Update the Windows capture runner so non-dry-run
`manager-fixture-v1-readonly` invokes the manager harness and preserves shared
runtime outputs.

### Scope
- `tools/protocol-research/run_protocol_capture.ps1`.
- Harness invocation record.
- EPF/runtime preflight gap handling.
- Owned-PID cleanup.

### Acceptance
- A non-dry-run capture writes proxy traffic and manager harness outputs under
  one run id.
- Missing EPF/runtime assets fail closed or produce a compact provider gap.
- Cleanup stops only runner-owned PIDs.

### Depends On
- `finish-manager-fixture-v1-harness-run-loop`
- `align-manager-fixture-v1-command-catalog`

### Related
- `openspec/changes/execute-manager-fixture-v1-live-capture/`

### Notes For `$openspec-ff-change`
- Keep Vanessa MCP smoke probes secondary; the manager harness is the evidence
  source for command cases.

## Change 4: `join-manager-fixture-v1-case-events`

### Why
Live traffic is not reviewable corpus evidence until command events are joined
to proxy chunks/frames and normalized into rows.

### Goal
Extend corpus runner/analyzer/reporting to consume manager fixture V1 runtime
outputs and produce joined evidence rows.

### Scope
- `protocol_corpus_runner.py` capture scenario support.
- Runtime manifest/result/event loading.
- Event-to-traffic join logic.
- Join report and corpus row generation.
- Precise unresolved reasons.

### Acceptance
- Joined commands record reviewed manager/client ranges where possible.
- Unjoined commands retain precise unresolved reasons.
- Joined rows include request/response sizes, normalized hash fields and
  replay/probe status.

### Depends On
- `execute-manager-fixture-v1-live-capture`

### Related
- `openspec/changes/join-manager-fixture-v1-case-events/`

### Notes For `$openspec-ff-change`
- Do not promote a joined row to accepted without replay or direct
  Python-manager proof.

## Change 5: `publish-manager-fixture-v1-live-smoke-evidence`

### Why
The full V1 catalog should not run until a bounded live smoke proves the
custom manager harness -> proxy traffic -> join -> corpus path.

### Goal
Run and publish the first bounded live smoke for two or three read-only
commands, or publish a precise provider/runtime gap if live startup is blocked.

### Scope
- Smoke subset execution.
- Compact reviewed runtime summary.
- Join report and corpus row evidence.
- Replay/probe attempt summary.
- Evidence index/docs links.

### Acceptance
- The smoke produces live evidence with at least one joined normalized row, or
  a provider/runtime gap that blocks expansion.
- Raw payloads and logs stay under ignored runtime paths.
- Full catalog expansion remains blocked when the smoke lacks joined evidence.

### Depends On
- `finish-manager-fixture-v1-harness-run-loop`
- `align-manager-fixture-v1-command-catalog`
- `execute-manager-fixture-v1-live-capture`
- `join-manager-fixture-v1-case-events`

### Related
- `openspec/changes/publish-manager-fixture-v1-live-smoke-evidence/`

### Notes For `$openspec-ff-change`
- Treat provider gaps as valid reviewed outcomes, but not as protocol
  acceptance.

## Change 6: `generate-automated-testing-api-inventory`

### Why
The roadmap requires an API inventory before industrial full-catalog corpus
expansion, but the inventory artifact is absent.

### Goal
Generate the first reviewed automated-testing API inventory from `help-mcp` or
the approved platform help source.

### Scope
- `docs/protocol-research/api-inventory/`.
- Machine-readable inventory JSON.
- Compact summary and gap report.
- Conservative safety classification.

### Acceptance
- Inventory records source version, objects, members and safety classes where
  available.
- Missing help topics are explicit gaps.
- Inventory is treated as semantic planning support, not wire proof.

### Depends On
- none

### Related
- `openspec/changes/generate-automated-testing-api-inventory/`

### Notes For `$openspec-ff-change`
- Record actual help-source platform version; do not assume it matches the lab
  runtime.

## Log
- 2026-06-05T04:02:12Z card created
- 2026-06-05T04:15:00Z decomposed into six OpenSpec changes and moved to `2.todo`
- 2026-06-05T05:19:18Z all six changes implemented, verified, archived and
  card moved to `4.done`
