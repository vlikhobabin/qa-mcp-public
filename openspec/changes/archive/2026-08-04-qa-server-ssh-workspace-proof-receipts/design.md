## Context

The root server SSH workspace lifecycle contract routes optional runtime proof
to qa-mcp only when a project policy or card requires QA/TestClient evidence for
a workspace delivery phase. Other providers publish readiness over immutable
commit/tree/source identities; qa-mcp needs the same identity boundary for
scenario proof without reading mutable workspace paths or retaining runtime
payload bodies.

## Goals / Non-Goals

**Goals:**
- Provide a small Python receipt builder that classifies QA proof as
  `not-required`, `missing`, `current`, `stale` or `unavailable`.
- Require explicit project policy before missing QA proof becomes a readiness
  gap.
- Sanitize and validate receipt inputs so retained diagnostics are bounded and
  secret-safe.
- Cover the behavior with offline unit tests and OpenSpec requirements.

**Non-Goals:**
- No live TestClient launch, UI action, capture, replay or protocol claim.
- No 1C infobase, business-data, screenshot, raw protocol log or source-body
  retention.
- No provider readiness federation outside qa-mcp's receipt payload.

## Decisions

1. Add a pure-Python receipt module under `src/qa_mcp/`.
   - Rationale: the contract is useful from CLI, MCP or future orchestration
     paths without coupling to a live TestClient session.
   - Alternative considered: embed the shape into `mcp_server.py`; rejected
     because this is identity/proof classification, not a protocol tool wrapper.

2. Fail closed on forbidden source routes before receipt creation.
   - Rationale: mutable workspace paths, host binds, network shares, source-body
     payloads and raw evidence bodies would weaken the pushed source identity
     boundary.
   - Alternative considered: accept and redact arbitrary values; rejected
     because the receipt should not normalize unsafe transport into acceptable
     evidence.

3. Store only evidence references and bounded scenario metadata.
   - Rationale: QA evidence may be screenshots or protocol/runtime transcripts
     in other contexts, but workspace receipts must only point to retained proof
     by id/path and summary state.
   - Alternative considered: include compact raw proof fragments; rejected to
     avoid source/customer data and protocol-log retention.

## Risks / Trade-offs

- Policy input ambiguity -> Receipt status defaults to `not-required` unless
  policy explicitly requires QA proof.
- Stale proof misclassification -> The receipt compares both commit SHA and
  tree SHA when proof is present; mismatches become `stale`.
- Over-redaction limiting diagnostics -> Diagnostics keep stable reason codes,
  source identity fields and evidence references while dropping raw paths and
  bodies.

## Migration Plan

This is additive. Existing runtime and MCP tools do not change behavior until a
future policy-gated path calls the receipt builder. Rollback is removing the new
module, tests and spec/archive entries.

## Open Questions

- Which future root or project policy surface will call the receipt builder from
  an MCP tool versus a CLI/reporting helper?
