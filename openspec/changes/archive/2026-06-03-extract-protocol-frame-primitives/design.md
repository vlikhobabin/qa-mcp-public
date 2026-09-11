## Context

`python_manager_client.py` currently mixes low-level byte manipulation,
template rendering, capture bootstrap loading, response summarization and live
socket session logic. The first implementation step should extract stable
primitives while leaving live networking behavior in place until a later
change.

## Goals / Non-Goals

**Goals:**

- Provide package-owned frame constants and helpers for tail stripping,
  hashes, UTF-8 frame decoding, ACK GUID extraction and manager header
  adaptation.
- Provide package-owned capture bootstrap and protocol template renderers.
- Keep dynamic replacements observable in returned render metadata.
- Add offline tests that do not require a running TestClient.

**Non-Goals:**

- Do not change direct TCP session semantics.
- Do not regenerate protocol evidence.
- Do not introduce non-stdlib dependencies.
- Do not promote incomplete mappings as accepted.

## Decisions

### Split Primitives From Live Session

The extraction should create modules such as `frames.py`, `templates.py` and
`bootstrap.py` under `src/qa_mcp/protocol/`. Live socket code remains out of
scope for this change so tests can focus on deterministic bytes and template
metadata.

### Compatibility During Migration

`tools/protocol-research/python_manager_client.py` may keep a thin import
layer or compatibility aliases so existing probes keep running during the
multi-change promotion. Broad rewrites of all tools wait until the wrapper
change.

### Fixture Inputs Stay Small

Tests should use compact committed evidence or small synthetic frame fixtures.
Full `runtime/protocol-research/captures/*/traffic.jsonl` files remain ignored
and are not required for package tests.

## Risks / Trade-offs

- Moving helpers can break exploratory script imports. Mitigation: preserve
  compatibility aliases and run existing tests/compile checks.
- Byte-level fixture tests can become brittle. Mitigation: assert stable
  replacement metadata and hash behavior instead of full opaque payloads when
  possible.
- Some helpers depend on `extract_payloads.py`. Mitigation: either move the
  minimal shared helpers into package code or keep explicit import boundaries
  until the wrapper change.

## Migration Plan

Extract primitives behind package modules, add tests, and keep existing script
entrypoints operational. The later session change will import these primitives
instead of duplicating byte logic.
