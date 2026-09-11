## Context

`tools/protocol-research/python_manager_client.py` already contains reusable
pieces for capture bootstrap loading, frame rendering, direct TCP sessions and
read-only probes. The accepted dictionary currently contains only
`active-window-context` and `active-form-context`; element details and typed
input are useful direct-probe paths but remain unresolved because reviewed
request hashes are incomplete.

## Goals / Non-Goals

**Goals:**

- Define a stable package contract for read-only TestClient protocol
  primitives before moving code.
- Preserve evidence status in the API surface: accepted mappings are distinct
  from partial, pending, unsupported and incomplete-hash rows.
- Keep package code stdlib-only and offline-testable.
- Make raw runtime paths non-public inputs unless an operator explicitly runs
  live capture/probe commands.

**Non-Goals:**

- Do not implement safe UI actions, clicks, text input or writes.
- Do not promote `form-element-details` or typed input as accepted mappings.
- Do not require EDT/meta services for protocol acceptance.
- Do not add package dependencies.

## Decisions

### Public Contract Starts With Evidence-Aware Operation Descriptors

The package should expose read-only operation descriptors that carry
`case_id`, accepted status, expected frame range, normalized hash when known,
probe evidence path and unresolved reason when not accepted. This keeps
callers from treating direct probe success as stable wire evidence.

### Accepted Scope Is Conservative

Only `active-window-context` and `active-form-context` may be marked accepted
from the current evidence set. `form-summary`, `form-element-details` and typed
input may be exposed as supported query paths, but they must retain partial or
incomplete evidence status until accepted corpus rows exist.

### Evidence Registry Reads Compact Files Only

The contract should reference committed compact evidence under
`docs/protocol-research/evidence/`. Raw captures, raw probe output and local
process logs remain under ignored runtime paths and are not needed for offline
package import or fixture tests.

## Risks / Trade-offs

- Package users may assume every exposed query is accepted protocol knowledge.
  Mitigation: status fields and docs must distinguish accepted from unresolved
  operations.
- Evidence paths may move as corpus IDs evolve. Mitigation: keep descriptors
  small and regenerate them from compact accepted-mapping evidence when needed.
- The contract adds structure before code movement. Mitigation: keep this
  change narrow and follow it immediately with primitive extraction.

## Migration Plan

Introduce the contract and tests first. Later changes move implementation
behind the contract and keep exploratory scripts as wrappers until the package
API is stable.
