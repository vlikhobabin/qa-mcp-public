## Context

R7 owns the immutable schema, sealed provenance, context-local evidence ledger
and bounded normalizer. The current `execute_operation` entrypoint bypasses all
of them and calls the configured executor directly; both MCP extension tools
and ScenarioRunner therefore expose the old path. The published R5-R2 design
requires route admission before evidence or adapter calls, and A5 authorizes
only this exact R8 successor with a machine ceiling of 301 while this card keeps
the stricter 300-line production cap.

No protocol frames or dynamic fields change. Capture sources, frame ranges and
replay strategy are not applicable: verification is offline with fake
Local/Windows adapters plus an exact-source Windows wheel run.

## Goals / Non-Goals

**Goals:**

- Keep declared unbound compatibility unchanged and integrate only operations
  present in the frozen positive-schema catalog of a bound application.
- Snapshot and validate request, runtime binding, target, session, attachment,
  generation and route endpoint before opening an evidence scope or invoking
  an adapter.
- Admit one sealed provenance value, execute the adapter exactly once inside
  one ledger operation scope, and normalize exactly once before `finally`
  closes the scope.
- Return identical bounded DTOs through the real FastMCP extension seam and
  ScenarioRunner for all verdicts, mismatches and the exact 40-cell URL table.

**Non-Goals:**

- Lifecycle composition/admission, creation of trusted attachments, additional
  operation schemas, public tools, wire fields, protocol behavior or authority.
- Live TestClient/1C, Docker, host-agent, capture/replay, mutation or external
  action.

## Decisions

### 1. Integrate only frozen schema operations in bound applications

An unbound context or an operation absent from the immutable application
catalog keeps the existing executor compatibility path. This prevents R8 from
changing lifecycle or widening the R7 schema. A bound catalog operation enters
the new path and cannot fall back after any validation or execution failure.

### 2. Route admission is a pure snapshot

Admission reads only exact built-in request arguments and application-owned
state. A current bound operation requires the runtime binding target, an exact
session bound to that target, and a matching attachment target/session/
generation. If host, port or display is supplied, its exact built-in value must
equal the current attachment value. Missing/malformed/foreign/asymmetric state
returns one fixed blocked result with zero adapter calls. Both-absent
pre-session lifecycle and declared unbound behavior remain outside R8's
schema-integrated path for OSS-04E.

The admitted provenance is reconstructed only from the validated binding and
request snapshot. Executor content cannot supply or replace it.

### 3. Evidence scope surrounds exactly one adapter call and normalization

After route admission, `EvidenceLedger.operation()` opens one scope. The
adapter is called once; its returned DTO and any application-owned receipts are
passed once to `normalize_operation_result`; the scope closes in `finally` for
success, every non-success verdict and every exceptional edge. Sanitized mode
never passes path authority. Full-local mode can use only receipts already
recorded by the current application scope; R8 creates no new receipt source.

### 4. Public paths share the same entrypoint and complete DTO

`execute_mcp_operation` and `execute_scenario_operation` remain thin aliases of
the shared entrypoint. FastMCP verification uses its existing `extra_tools`
extension seam, so no public tool/schema is added. ScenarioRunner returns the
same normalized DTO before adapting success to a preview or non-success to a
step error. Tests compare the complete serialized result at the operation
boundary and the real public-path observations.

### 5. Fixed route failure and total containment

The implementation snapshots only fixed fallback kind/name values before
touching mutable input. Unexpected route, adapter, normalization or encoding
edges return a bounded fixed result without retry, alternate adapter calls,
exception text or input fragments. Serialization cannot reopen the evidence
scope or change route/disclosure authority.

## Risks / Trade-offs

- [Risk] Existing callers use incomplete bound state. → They fail closed only
  for the one currently schema-declared operation; unbound and non-schema
  compatibility remains unchanged until OSS-04E owns lifecycle admission.
- [Risk] Attachment objects can raise during field access. → Snapshot inside
  the outer total boundary and reject before scope/adapter invocation.
- [Risk] ScenarioRunner converts non-success DTOs to step errors. → Assert the
  shared operation DTO independently and the real runner taxonomy/provenance
  source together; do not introduce a second serializer.
- [Risk] Full-local artifacts lack a receipt producer in R8. → Never derive a
  receipt from executor path data; later evidence work may record receipts
  through the application-owned scope.

## Migration Plan

1. Add RED matrices for route isolation, verdict/provenance, declared mismatch,
   bounds and the exact 40 public URL cells.
2. Implement the shared bound-operation path within 300 added production LOC.
3. Run focused/full Linux gates and exact-source Windows offline integration;
   retain only owned staging and cleanup evidence.
4. Sync/archive, obtain fresh independent review and publish before OSS-04E.

Rollback is one scoped commit. No runtime resource or protocol migration is
required.

## Open Questions

- None. Adding schemas, lifecycle attachment authority or receipt production is
  a later reviewed scope.
