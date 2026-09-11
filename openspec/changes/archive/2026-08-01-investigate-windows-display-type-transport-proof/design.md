## Context

S50-120 has green offline Python and Go verification and a source-bound Windows
proof that reaches the owned empty-title fixture. Screenshot, safe-key targeting,
and unrelated-foreground isolation pass, but the proof client reports only a
transport-level failure at `type_text`. The previous ignored proof harness and
its sanitized summaries are the investigation source.

This is HTTP proof-harness research, not native TestManager/TestClient protocol
research. Capture ids, frame ranges, protocol dynamic fields, normalized frame
hashes, and replay strategy are therefore `N/A`. The dynamic HTTP response body,
window/process identities, screenshots, credentials, and host-agent logs are
explicitly excluded; retained evidence is limited to status classes, normalized
error codes, source hashes, booleans, test outcomes, and cleanup state.

## Goals / Non-Goals

**Goals:**

- Preserve the HTTP status class and bounded structured error code at the
  failing `type_text` request.
- Distinguish client parsing/transport behavior from `foreground-denied`, typed
  desktop-session refusal, and unexpected host-agent or fixture exit.
- Repair only the ignored proof harness when that is the cause, then complete
  the five-route, explicit-override, weak-target, typed-session, isolation, and
  cleanup matrix required by S50-120.
- Produce a precise linked product-fix handoff if the host-agent is defective.

**Non-Goals:**

- Editing Python or Go product code, public documentation, or runtime
  configuration.
- Accessing a 1C infobase, changing business data, capturing native protocol
  traffic, or retaining raw HTTP bodies or desktop artifacts.
- Weakening or replacing the verification floor of S50-120.

## Decisions

### 1. Instrument the ignored proof-client boundary

The new run copies the prior source-bound proof into a new ignored, exact-name
evidence directory and changes only its HTTP error handling. The handler records
an integer HTTP status and a small allowlisted error code; it discards the body
after bounded in-memory parsing. Source hashes for the host-agent, native tests,
fixture, and proof are recorded so the result remains tied to the reviewed
S50-120 sources.

This is preferred to adding product logging because the missing boundary is in
the proof client and product logs are forbidden evidence. Reusing the original
evidence directory was rejected because it would erase the failed-run audit
trail.

### 2. Classify by independent observable signals

The diagnosis uses four independent signals: HTTP status/code, host-agent
liveness, owned-fixture liveness, and the existing desktop-session/native-test
rows. A client exception with an available typed response is a harness parsing
defect; `foreground-denied` or a typed desktop-session code is a safe product
refusal; unexpected process exit is a runtime/process failure; an unexpected
status/code from a live product becomes a product invariant failure.

No untyped message text, response payload, process id, HWND, title, or log text
is retained in the sanitized summary.

### 3. Keep the branch decision fail-closed

If the ignored harness is defective, repair it and rerun the complete existing
matrix. A green result is a proof handoff back to S50-120. If product behavior is
defective, this investigation creates a linked implementation card with the
failing route, expected typed boundary, source lineage, cleanup proof, and full
rerun floor; it does not change product code itself.

### 4. Preserve exact ownership and cleanup

Execution is limited to the authorized architect workstation, a unique
exact-name scheduled task/stage, the source-bound host-agent, and the two owned
fixtures. Cleanup stops only processes launched by that proof, removes the
exact task and stage, and records before/after booleans. No infobase or native
TestClient process is involved.

## Risks / Trade-offs

- [Risk] Parsing an error body could retain sensitive data. -> Parse a bounded
  in-memory body, copy only an allowlisted code, and never write the body or
  exception text.
- [Risk] A stale binary could make the diagnosis irrelevant. -> Rebuild or hash
  the source-bound binaries and record only normalized source/binary hashes.
- [Risk] A foreground race could make one run inconclusive. -> Use the existing
  owned fixtures and one bounded rerun after classification; do not expand into
  an open-ended retry loop.
- [Risk] Cleanup could affect an unrelated process. -> Track owned process
  objects and exact task/stage names; never use wildcard process cleanup.

## Migration Plan

1. Preflight the authorized host and confirm the prior proof is fully cleaned.
2. Copy and instrument the proof harness under a new ignored evidence run.
3. Run the bounded diagnostic reproduction and classify the failure.
4. Run the complete matrix if the repair is harness-local, or create the scoped
   product-fix card if the product invariant fails.
5. Perform exact cleanup and retain only the sanitized result and cleanup JSON.

Rollback is deletion of the exact ignored investigation stage/evidence run;
there is no durable product deployment to roll back.

## Open Questions

- The failure class is intentionally unresolved until the bounded diagnostic
  reproduction records its HTTP status/code and liveness signals.
