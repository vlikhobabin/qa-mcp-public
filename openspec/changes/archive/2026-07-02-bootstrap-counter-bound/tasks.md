## 1. Implementation

- [x] 1.1 Update `src/qa_mcp/protocol/bootstrap_synth.py` so default random `counter_base` selection leaves room for
      the maximum generated bootstrap counter delta.
- [x] 1.2 Derive the maximum delta from the bootstrap template/frame metadata rather than hard-coding `3`.
- [x] 1.3 Preserve explicit invalid `counter_base` validation through the existing render path.

## 2. Offline Tests

- [x] 2.1 Add `tests/test_bootstrap_synth.py` coverage for the highest generated random base rendering frames 1..4.
- [x] 2.2 Add or preserve coverage proving explicit out-of-range bases still raise.
- [x] 2.3 Keep existing independent-session and platform-version synthesis tests green.

## 3. Verification

- [x] 3.1 `uv run pytest tests/test_bootstrap_synth.py -q` — 10 passed.
- [x] 3.2 `uv run pytest tests/ -q` — 603 passed.
- [x] 3.3 `uv run python -m compileall -q src/qa_mcp` — passed.
- [x] 3.4 `openspec validate bootstrap-counter-bound --strict` — passed.
- [x] 3.5 `git diff --check` — passed.
- [x] 3.6 Windows-native verification: not run in this Linux delivery; no platform-specific code is planned. The
      equivalent Windows gate is `uv run pytest tests/test_bootstrap_synth.py -q` before a Windows release build.

## Verification Matrix

Card scope: qa-mcp Python bootstrap synthesis. No BSL, metadata, managed form, role, posting, source import, live
infobase mutation, QA/TestClient UI interaction, or runtime apply is required.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python protocol bootstrap synthesis | `src/qa_mcp/protocol/bootstrap_synth.py::synthesize_bootstrap` | random default base leaves room for all generated counter deltas | `uv run pytest tests/test_bootstrap_synth.py -q` (10 passed), `uv run pytest tests/ -q` (603 passed), `uv run python -m compileall -q src/qa_mcp` (passed) | `tests/test_bootstrap_synth.py` | provided | qa-mcp | none for offline synthesis behavior | — |
| QA/TestClient live runtime | live bootstrap against a running client | no live behavior required; generated frames are validated offline | N/A | N/A | N/A | qa-mcp | a future live smoke could prove end-to-end attach, but the defect is deterministic frame rendering | no live 1C required because this is a random range guard |
| OpenSpec/spec contract | `qa-mcp-protocol-lab` delta | bootstrap counter requirement added and synced | `openspec validate bootstrap-counter-bound --strict` (passed), `git diff --check` (passed) | `openspec/changes/bootstrap-counter-bound/` | provided | qa-mcp | none | — |
