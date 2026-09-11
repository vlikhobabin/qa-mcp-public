## Context

S1-R1 publishes opaque run/token/desktop identity and exact process creation.
S2-R1 publishes exact worker/child/listener ownership and idempotent cleanup.
S3/S4 publish exact hidden-window isolation and a sanitized passive observation
receipt. S5-R1 publishes a sanitized addressed-prompt receipt. None currently
forms a Python-consumable current-run receipt, and cleanup authority must not be
reconstructed from mutable PIDs or a supplied OS handle.

This change does not alter the TestClient protocol, capture tools or replay
logic. There are no protocol frames, capture sources or dynamic frame fields.
Dynamic PIDs remain exact Go `uint32` receipt values; raw run/token values and handles
never cross the boundary. Offline hostile/unit evidence is sufficient because
the published Windows action and cleanup implementations remain byte-identical.

## Goals / Non-Goals

**Goals:**

- validate the published S1/S2/S4/S5 successful typed outcomes before creating
  a cross-language receipt;
- bind one receipt to exact current-run hashes, port and worker/child/listener
  identity through an independently recomputable opaque SHA-256;
- make the bound value immutable in Python and detect any serialized mutation
  again immediately before cleanup;
- consume a caller-owned binding ledger before invoking one injected cleanup
  callback, so failure cannot authorize a retry;
- keep all rejected rows callback-free and all retained data privacy-safe.

**Non-Goals:**

- exporting an OS/job handle or letting Python discover cleanup targets;
- activating a host capability, MCP/tool/profile route or S7 integration;
- changing S1-S5 behavior, chooser/input/action behavior or Windows runtime;
- live prompt, protocol capture/replay or stable admission evidence.

## Decisions

### Use one internal envelope over published typed outcomes

Go constructs `qa-mcp.internal-hidden-direct-execute-receipt.v1` only after
the exact S2 lifecycle response and successful S4 receipt validate. The S5
receipt is optional: absent means the exact prompt-free S4 outcome; present
means S5 must validate and share S4's main-identity hash. Python repeats strict
schema, status, exact-type, hash and bounded-count validation rather than
treating JSON presence as success.

A loose dictionary accepted by shape alone was rejected because Python `bool`
is an `int`, unknown fields can hide schema drift and nested failed outcomes
could otherwise be mistaken for success.

### Bind cleanup identity without transferring cleanup authority

The envelope carries only run/token/desktop hashes, port and exact worker,
child and listener PIDs. Its `cleanup_identity_hash` is SHA-256 over one fixed
canonical ordering. Go keeps the actual cleanup closure/owned handles; Python
must receive the independently known current-run identity and compare every
field plus the recomputed hash. No receipt-supplied PID or handle selects a
cleanup target.

Exporting the job handle or accepting a lifecycle id from the receipt was
rejected because either would let foreign or stale serialized data choose
cleanup authority.

### Revalidate exact bytes and consume a shared ledger before cleanup

Both languages retain a canonical fingerprint of the admitted envelope.
`stop` receives the envelope again, rejects any post-bind mutation, atomically
checks and marks the binding in a caller-owned consumed-binding ledger, and only
then invokes the injected exact-owned cleanup once. Go binds a mutex to each
ledger and Python serializes ledger admission/consumption through one internal
lock. The consumed entry remains even when cleanup reports failure, preventing
repeated destructive attempts and concurrent replay.

A lease-local boolean alone was rejected because a second lease built from a
replayed receipt could bypass it. Retrying after callback failure was rejected
because incomplete cleanup needs explicit diagnosis, not implicit repetition.

### Keep the implementation isolated and dormant

S6 adds one portable Go file/test and one Python module/test. It does not import
the Python module from a public surface and adds no non-test Go caller. This
preserves Linux behavior, public profiles and every published predecessor byte,
and allows clean composition from published HEAD using exact S6 paths.

## Risks / Trade-offs

- [Python and Go canonicalization diverge] -> use a fixed delimiter/order,
  lowercase SHA-256, exact `1..4294967295` PID bounds and cross-language fixture
  expectations.
- [PID reuse makes a stale identity appear current] -> require independently
  supplied run/token/desktop hashes plus exact port/PID tuple and single-use
  ledger; PIDs alone are never sufficient.
- [Cleanup fails after ledger consumption] -> return the failure but retain
  consumption, leaving recovery to an explicit later workflow rather than a
  repeated stop.
- [Dirty S7 candidate contaminates S6] -> clean-compose only isolated S6 paths
  and hash every published S1-S5 source/test file against HEAD.

## Migration Plan

There is no public migration. S6 remains dormant until S7 explicitly wires the
already-reviewed internal boundary. Rollback removes the isolated four S6
source/test files and capability artifacts; published behavior is unchanged.

## Open Questions

- None for S6. Selecting the stable public route and mapping its lifecycle
  registry to this internal lease belongs exclusively to S7.
