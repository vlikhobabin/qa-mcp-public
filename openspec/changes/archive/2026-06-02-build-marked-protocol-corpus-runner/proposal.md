## Why

The current capture/replay tools can prove specific frame families, but broad
protocol decoding needs a repeatable runner that creates short labeled cases
instead of one large unsegmented traffic log. A marked corpus runner will let us
build a practical dictionary from 1C testing API calls to protocol bytes and
then confirm mappings through Python replay.

## What Changes

- Add a Windows-native protocol corpus runner for short read-only cases using
  the verified Vanessa attach-running capture path.
- Extend capture/proxy/analyzer output with case markers and normalized per-case
  evidence rows.
- Seed the first corpus matrix for active window, active form and basic form
  element read-only operations.
- Add replay/probe hooks so accepted case mappings are confirmed against a live
  TestClient without a 1C TestManager instance where feasible.
- Generate compact reviewed evidence and update the evidence index while
  keeping raw captures in ignored runtime directories.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: Add requirements for running marked protocol corpus
  captures and generating normalized corpus evidence.

## Impact

- Touches protocol tools under `tools/protocol-research/`.
- Touches protocol research docs and curated evidence index.
- May add tests or fixtures for offline normalization and manifest parsing.
- Uses live 1C runtime and Vanessa MCP for end-to-end capture verification.
- Does not promote reusable Python manager APIs into `src/qa_mcp`; that remains
  a later P1 card after the corpus evidence model is proven.
