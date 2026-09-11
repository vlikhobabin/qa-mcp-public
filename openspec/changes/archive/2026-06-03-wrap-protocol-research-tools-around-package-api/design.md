## Context

The repository keeps exploratory research tooling under
`tools/protocol-research/` until behavior is promoted into `src/qa_mcp/`.
Once package APIs exist, scripts should become wrappers or adapters. Keeping
duplicate logic would make future protocol evidence hard to trust.

## Goals / Non-Goals

**Goals:**

- Make exploratory scripts import package-owned protocol primitives and
  session APIs.
- Preserve existing CLI names, arguments and output schema compatibility unless
  a change is explicitly documented.
- Keep `compare_corpus_runs.py` and `protocol_corpus_runner.py` behavior
  stable while they can consume package descriptors or helpers where useful.
- Update docs with the package-versus-tools boundary.

**Non-Goals:**

- Do not remove exploratory scripts in this card.
- Do not add new protocol mappings.
- Do not require live Vanessa or EDT/meta services for wrapper compatibility.
- Do not change committed evidence schemas unless tests and docs are updated.

## Decisions

### Tools Become Wrappers Gradually

Not every script must move at once. The implementation should prioritize
`python_manager_client.py` and `python_manager_probe.py`, then only touch
corpus/comparison scripts where promoted helpers reduce duplication without
changing reviewed evidence.

### CLI Compatibility Is A Gate

Existing Windows-native commands should keep working. Tests can use `--help`,
fixture-backed commands and import checks to verify compatibility without
starting a live TestClient.

### Evidence Outputs Remain Reviewed Artifacts

Wrapper changes must not silently regenerate historical evidence. New compact
evidence should use a new run/comparison id and update the evidence index.

## Risks / Trade-offs

- Refactoring scripts can change output schemas accidentally. Mitigation:
  compatibility tests compare expected keys and run CLI help/smoke commands.
- Keeping wrappers may leave some duplication. Mitigation: defer low-risk
  cleanup until package APIs prove stable.
- Live probe wrapper smoke may be unavailable. Mitigation: record an explicit
  environment gap and keep offline checks mandatory.

## Migration Plan

Refactor scripts after package APIs are stable. Keep CLI entrypoints in place,
run offline compatibility checks, then optionally run live read-only probe
smoke if the lab TestClient is available.
