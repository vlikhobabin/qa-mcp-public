## Context

Pure callbacks through real factories on `1046b9f` reproduce both root helpers
reading a third process root for A, B and explicit-empty Settings. Retained
baseline: `.runtime/qa-roadmap/oss-00/fix-04c-planning/reproduction.json`. This is
only defect confirmation; product consumers and ownership transitions need
stronger acceptance proof. FIX-03's native admission remains enforced.

## Goals / Non-Goals

One invariant: each composed application locates outputs and creates/discovers
ownership records only according to its own configured roots and existing bound
policy. Reuse FIX-04B's `active_application_settings` scope. Cover creation AND
lookup, not only a helper return value.
No socket/display routing, TTL/artifact receipt redesign, real file/process
cleanup, old-directory migration, new target observation or changes to FIX-05's
standalone screenshot retention. No protocol claim: captures, frames, dynamic
wire fields and replay classification are unchanged and N/A here.

## Decisions

1. Root helpers use active Settings when present; otherwise preserve their
   existing explicit legacy env adapter. An active Settings with empty fields
   is authoritative absence, not permission to fall back to process env. Keep
   existing static workspace/default ownership fallback. Avoid imports from
   low-level lifecycle into core/MCP or a second context registry.
2. Trace both local composed launch callsites, actual marker production and
   later discovery/cleanup. Explicit ownership root can differ from home;
   changing only `_ownership_root` leaves markers undiscoverable. Choose one
   coherent application-owned placement/discovery policy and reuse it through
   composed launches. Preserve explicit direct-call output contracts and marker
   identity fields; document any intentional placement distinction. Do not scan
   additional roots to compensate for wrong placement. Existing static fallback
   remains shared only when applications deliberately choose the same fallback.
3. Workspace selection does not override binding.evidence_root. Exercise actual
   bound default evidence production with valid target/session/attachment after
   FIX-03 and a synthetic backend; verify sanitized versus approved full_local
   policy, no raw roots in sanitized DTOs and no cross-root outputs. Plain unbound
   public paths remain useful under their existing contract; FIX-05 is separate.
4. Tests use real factory/context binding, capture/output consumers and marker
   serialization/discovery/cleanup policy. Fake sockets, subprocesses, process
   identity/signalling and display/native boundaries. Temporary directories only.
   Preserve foreign markers, PID reuse/start/group refusal and target/session
   policy. Include successful same-owner lookup after env drift; a test that
   merely refuses every stop does not prove coherent cleanup.
5. Verify A/B/explicit-empty settings against process root C, explicit ownership
   override versus workspace-derived fallback, actual launch-to-marker-to-stop,
   foreign marker and PID/start/group mismatches, admitted evidence authority and
   explicit legacy calls outside composition. Nested inner failure must restore
   exact outer root and application identity; compare complete paired observations
   and exact counts, not independent sets. Preserve caller context in the same
   execution scope; real MCP dispatch may itself isolate tasks/threads, so use
   the actual registered callback for a direct wrapper restoration control where
   required. Retain one meaningful sensitivity check for env fallback or marker
   root mismatch without modifying product during delivery evidence collection.

## Risks / Trade-offs

- Input safety: root precedence and empty settings could import ambient paths.
  C1/C3 use synthetic conflicting roots and explicit-empty/legacy partitions.
- Mutation/external effects: wrong-root cleanup could remove foreign files or
  signal a reused PID. C2 records before/after marker/process inventories and
  checks PID/start/group plus existing target/session ownership with fake signals.
- Restart: marker production and stateless later discovery may diverge. C2 uses
  real marker bytes across separate calls after env drift; no persistent format
  migration is planned and pre-existing directories are not migrated or scanned.
- Concurrency: scoped roots can leak during nesting/exceptional exits. C3 tests
  exact paired roots/context, including restored caller after an inner failure.
- Publication: no product release behavior changes. The installed runner owns
  independent review, archive, final floor and ordinary publication.

## Verification Matrix

| Surface | Required evidence | Boundary / limitation |
| --- | --- | --- |
| Real factory capture/output roots, C1 | Exact path/content/inventory assertions and verbose source-bound JUnit/nodes | Temporary paths; native/display boundary faked |
| Marker creation/discovery/cleanup, C2 | Real marker bytes, successful owner cleanup after env drift, foreign/PID/start/group refusals | No real process signal, deletion outside fixtures or launch |
| Precedence, bound privacy and context, C3 | Explicit/empty/fallback/legacy matrix; nested error restoration; complete paired observations | Existing bound evidence authority preserved |
| Affected integration consumers | Separate selected integration receipt | Stdio/process integration is not native 1C proof |
| Native Linux/Windows, BSL/metadata/forms/roles/posting/reports/migration | No changes to infobase source or wire contracts | Final native qualification remains FIX-11/FIX-12 |

Record exact selected node IDs with `pytest -v`, timestamps, source hashes,
before/action/after observations and mocked boundaries under
`.runtime/qa-verification/oss-fix-04c/` and runner-owned typed receipts. All C1-C3
rows are implementation-stage proof and must be current before aggregate handoff.
Run affected offline and integration lanes separately; no full suite implied.

## Migration Plan

One native change and one cohesive implementation checkpoint cover the entire
root family and its consumers. Accept and publish planning, then clean-start
runner. After all implementation tasks complete, the separate finalizer performs
semantic sync, refreshes current typed C1-C3 proof AFTER sync/Result/Log edits,
and completes handoff. Archive refresh similarly retains current verbose proof.
If recovery creates a new run, retain that run's own no-op semantic sync receipt
when canonical content is already correct. Missing/stale receipts are authorized
finalization work: refresh them and continue without changing accepted scope,
rewriting history or developing ChangeRail. No aggregate stage is a prerequisite
checkbox inside an implementation group. Rollback is a scoped code revert with
focused controls; no live resources or old marker directories are migrated.

## Open Questions

No operator decision remains. Resolve routine placement implementation within
this invariant and preserve direct explicit-output compatibility. Existing
FIX-03 admission and FIX-04B scope are completed dependencies of the source.
