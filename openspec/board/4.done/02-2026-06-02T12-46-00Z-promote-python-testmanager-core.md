# Promote Python TestManager Core

## Status
4.done

## Priority
P1 - promote stable primitives after accepted read-only corpus mappings are
available.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 qa-mcp repository bootstrap
- 2026-06-02 protocol dictionary strategy discussion
- 2026-06-02 expanded read-only corpus result review

## Summary
Move accepted read-only protocol session code from `tools/protocol-research`
into the `qa_mcp.protocol` package with typed APIs, tests and fixture-backed
replay coverage. Promotion should follow the corpus runner schema so package
APIs are driven by stable evidence rather than exploratory script internals.

Current accepted wire mappings are limited to `active-window-context` and
`active-form-context`. The package may expose form summary and element-detail
query paths, but those paths must retain unresolved evidence status until
reviewed request hashes are accepted.

## Acceptance
- `qa_mcp.protocol` exposes a reusable read-only TestClient session API.
- Existing `initial-ui`, `active-window-context`, `active-form-context`,
  `form-summary` and `form-element-details` probes are available through
  package code.
- Offline tests cover template rendering, response parsing and read-only
  session behavior from curated evidence or synthetic fixtures.
- The package can consume the corpus runner's template/evidence model or
  expose an equivalent stable model.
- Promoted APIs are based on accepted direct-probe/corpus evidence from
  `Accept Readonly Corpus Probe Mappings`.
- Only `active-window-context` and `active-form-context` are classified as
  accepted from the current evidence set.
- Exploratory tools remain available as wrappers until package behavior is
  fixture-covered.

## Change Set
- `openspec/changes/define-python-protocol-package-contract/`
- `openspec/changes/extract-protocol-frame-primitives/`
- `openspec/changes/promote-readonly-testclient-session-api/`
- `openspec/changes/wrap-protocol-research-tools-around-package-api/`

## Verify
- `bin\openspec.cmd validate define-python-protocol-package-contract --strict` passed
- `bin\openspec.cmd validate extract-protocol-frame-primitives --strict` passed
- `bin\openspec.cmd validate promote-readonly-testclient-session-api --strict` passed
- `bin\openspec.cmd validate wrap-protocol-research-tools-around-package-api --strict` passed
- `python -m py_compile` passed for promoted package, wrapper tools and focused tests
- focused offline smokes passed for package contract, frame primitives, session API and wrappers
- `python tools\protocol-research\python_manager_probe.py --help` passed and includes `active-window-context`
- `scripts\check.ps1` passed; `pytest` is not installed and was skipped by the script
- `scripts\check-protocol-lab.ps1` passed
- live read-only smoke was not run because the lab check reported no started manager/TestClient; retained explicit environment gap evidence
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed
- `bin\openspec.cmd validate --all` passed
- `git diff --check -- openspec\changes openspec\specs openspec\board src tools\protocol-research tests docs\protocol-research` passed with CRLF warnings only

## Archive
- `openspec/changes/archive/2026-06-03-define-python-protocol-package-contract/`
- `openspec/changes/archive/2026-06-03-extract-protocol-frame-primitives/`
- `openspec/changes/archive/2026-06-03-promote-readonly-testclient-session-api/`
- `openspec/changes/archive/2026-06-03-wrap-protocol-research-tools-around-package-api/`

## Related
- `openspec/board/4.done/2026-06-02T13-50-55Z-define-protocol-dictionary-strategy.md`
- `openspec/board/4.done/2026-06-02T12-45-00Z-build-protocol-corpus-runner.md`
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`
- `tools/protocol-research/python_manager_client.py`
- `tools/protocol-research/python_manager_probe.py`
- `src/qa_mcp/protocol/`
- `tests/test_protocol_contract.py`
- `tests/test_protocol_primitives.py`
- `tests/test_protocol_session.py`
- `tests/test_protocol_tool_wrappers.py`
- `docs/protocol-research/python-protocol-package.md`
- `docs/protocol-research/evidence/python-manager-package-smoke/20260603-offline-gap/`
- `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `openspec/changes/archive/2026-06-03-define-python-protocol-package-contract/`
- `openspec/changes/archive/2026-06-03-extract-protocol-frame-primitives/`
- `openspec/changes/archive/2026-06-03-promote-readonly-testclient-session-api/`
- `openspec/changes/archive/2026-06-03-wrap-protocol-research-tools-around-package-api/`
- publish commit recorded in git history

## Result
Implemented and archived all four planned changes. `qa_mcp.protocol` now owns
the evidence-aware read-only operation contract, frame/template/bootstrap
primitives, response parsing, reusable read-only `TestClientSession` API and
compatibility wrappers for the existing protocol research tools.

Accepted protocol status is intentionally limited to `active-window-context`
and `active-form-context`. `form-element-details` and typed input field
read-only paths remain unresolved with `incomplete_hash` status until request
hashes are accepted from follow-up evidence.

Live read-only smoke was deferred because the lab environment did not have a
started manager/TestClient pair. The environment gap is retained as compact
evidence under `docs/protocol-research/evidence/python-manager-package-smoke/`.

Published by the `feat(protocol): promote python testmanager core` commit.

## Next
- none

## Change Plan Notes
Execution order:

1. Define the package contract and evidence status boundary.
2. Extract deterministic frame, bootstrap and template primitives into
   `src/qa_mcp/protocol`.
3. Promote the read-only direct TestClient session/query API.
4. Refactor exploratory protocol research tools into compatibility wrappers
   around the package API.

Verification expectations:

- `scripts\check.ps1`
- `scripts\check-protocol-lab.ps1`
- focused package contract, primitive, session and wrapper tests
- `python -m py_compile` for touched package/tools/test modules
- optional live read-only smoke when a TestClient is available, otherwise an
  explicit provider/environment gap
- `bin\openspec.cmd validate --all`
- `git diff --check`

## Change 1: `define-python-protocol-package-contract`

### Why
The package needs an evidence-aware contract before exploratory protocol code
is moved into `src/qa_mcp`.

### Goal
Define public read-only operation descriptors, accepted/unresolved status
rules and compact evidence boundaries for `qa_mcp.protocol`.

### Scope
- Package contract shape and docs.
- Offline descriptor tests.
- Spec requirements for accepted versus unresolved mappings.
- No live runtime or socket implementation changes.

### Acceptance
- Accepted active-window and active-form descriptors link compact evidence.
- Element-detail and typed-input descriptors remain unresolved, not accepted.
- Contract import/tests require no live TestClient and no raw runtime capture.

### Depends On
- none

### Related
- `openspec/changes/define-python-protocol-package-contract/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 2: `extract-protocol-frame-primitives`

### Why
Byte-level helpers and template rendering need package ownership before live
session code can be promoted safely.

### Goal
Move deterministic frame constants, bootstrap loading and template rendering
primitives into `src/qa_mcp/protocol`.

### Scope
- Package frame/template/bootstrap modules.
- Compatibility imports for existing exploratory client code.
- Offline tests for dynamic field replacement and bootstrap loading.
- No live socket behavior changes.

### Acceptance
- Template rendering returns payload plus replacement metadata offline.
- Bootstrap loading separates manager/client frames and rejects incomplete
  data.
- Existing research scripts still compile.

### Depends On
- `define-python-protocol-package-contract`

### Related
- `openspec/changes/extract-protocol-frame-primitives/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 3: `promote-readonly-testclient-session-api`

### Why
Future QA manager/MCP runtime work needs a reusable package session API for
direct read-only TestClient communication without 1C TestManager.

### Goal
Promote direct TCP `TestClientSession` and read-only query APIs into
`qa_mcp.protocol`.

### Scope
- Package session lifecycle and read-only query methods.
- Typed/evidence-status preserving query results.
- Offline fake-socket/fixture tests.
- Optional live read-only smoke with compact retained evidence or explicit
  environment gap.
- No actions, writes or business-data mutation.

### Acceptance
- Package code exposes read-only queries for initial UI, active window/form,
  form summary and element details.
- Accepted status is limited to current accepted mappings.
- Session cleanup closes only the socket it owns.

### Depends On
- `extract-protocol-frame-primitives`

### Related
- `openspec/changes/promote-readonly-testclient-session-api/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 4: `wrap-protocol-research-tools-around-package-api`

### Why
Exploratory tools must keep working while sharing the promoted package
implementation, otherwise research scripts and runtime package behavior will
diverge.

### Goal
Refactor protocol research CLIs into compatibility wrappers around
`qa_mcp.protocol`.

### Scope
- `python_manager_client.py`, `python_manager_probe.py` and relevant imports.
- CLI compatibility tests and docs.
- Evidence index updates only if new compact evidence is generated.
- No removal of exploratory tools.

### Acceptance
- Existing CLI arguments and output schemas continue to work or have an
  explicit migration note.
- Wrapper tests prove package imports and CLI smoke behavior.
- Raw regenerated output stays under ignored runtime paths.

### Depends On
- `promote-readonly-testclient-session-api`

### Related
- `openspec/changes/wrap-protocol-research-tools-around-package-api/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Log
- 2026-06-02T12:46:00Z card created
- 2026-06-02T13:50:55Z reprioritized as P1 behind corpus runner schema
- 2026-06-02T18:01:06Z ordered after accepted read-only corpus mapping work
- 2026-06-03T06:19:03+03:00 decomposed into four OpenSpec changes and prepared artifacts
- 2026-06-03T06:45:37+03:00 implemented package promotion, synced specs, archived all four changes and moved card to done
- 2026-06-03T06:56:49+03:00 published by `$opsx-pub`
