## Context

I11 is published at commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
Its tracked card, archived change and synced specification prove a private,
call-neutral main-predicate equivalence correction with focused/full Go tests,
vet, Linux repository coverage and deterministic unexecuted cross-builds. I11
explicitly excludes the exact-source execution matrix, marker derivation,
cleanup certification and downstream continuation required by the S4-R1
parent.

This decision uses only tracked published evidence. There are no protocol
captures, frame ranges, dynamic fields or replay traffic to inspect, and no
runtime resource is created by the decision payload. The old rejected I4/I9
workspaces remain immutable and are not needed beyond their already-published
lineage summaries.

## Goals / Non-Goals

**Goals:**

- Map every parent criterion to exact published evidence or a named remaining
  gap.
- Remove stale parent and roadmap instructions after I11 publication.
- Prepare one exact apply-ready successor for certification of the published
  bytes, with fail-closed cleanup and review requirements.
- Preserve the parent and downstream block until the missing evidence is
  independently reviewed and published.

**Non-Goals:**

- Treating I11's offline proof as execution or cleanup proof.
- Modifying the published predicate implementation or any product/test file.
- Reopening rejected I4/I9 workspaces or deriving new claims from them.
- Performing the successor's execution matrix in this payload.

## Decisions

### 1. Reconcile acceptance criterion by criterion

The decision records each top-level parent criterion as `closed_offline`,
`remaining_certification` or `preserved_block`. Published I11 may close only
claims directly supported by its tracked card/archive/specification and
retained public-safe summaries. Any criterion requiring fresh execution,
marker evidence or cleanup proof remains open.

Alternative: mark the parent complete because I11 passed its own acceptance.
Rejected because I11's acceptance and non-goals deliberately exclude the
parent's exact-source matrix.

### 2. Use one certification-only successor

I13 owns the exact-source S3/S4/S5 matrix, stable two-sample marker receipt and
exact-owned cleanup audit against the published I11 commit. It starts from
unchanged published product bytes and adds no implementation authority. A
behavioral failure, unavailable evidence, source drift or cleanup mismatch is
a fail-closed stop and requires a separately authorized investigation rather
than an implementation rescue inside I13.

Alternative: resume the broad parent directly. Rejected because separating
certification evidence keeps unavailable execution from being confused with
new implementation authority and produces one exact next card.

### 3. Keep downstream work blocked

The parent remains `2.todo` and its roadmap entry names I13 as the only next
S4-R1 step. Downstream continuation remains blocked until I13 and then the
parent have fresh independent review and scoped publication.

Alternative: unblock downstream work after the offline correction. Rejected
because the missing evidence is part of the parent's observable acceptance.

### 4. Publish only documentation and OpenSpec state

I12 may update the parent, roadmap, curated findings/decision, I12 artifacts
and I13 board/OpenSpec planning. It may not change code, tests, license,
runtime configuration or external state. RED evidence is not applicable to
this docs-only decision; strict parsing, graph, scope and whitespace checks
are the verification boundary.

## Risks / Trade-offs

- [Offline success is overstated] -> Bind every closed row to a published I11
  artifact and keep execution-dependent rows explicitly open.
- [I13 becomes implicit implementation authority] -> State that source drift
  or any behavioral failure stops for a separate investigation.
- [Roadmap and parent diverge] -> Verify exact I13 identity and status in both
  documents plus the machine-readable decision.
- [Scope crosses the hard boundary] -> Fail scope checks on any product/test,
  runtime or external-operation path.

## Migration Plan

1. Prove the published I11 identity and inspect only its tracked evidence.
2. Publish the criterion map and exact I13 certification contract.
3. Update parent/roadmap and create apply-ready I13 artifacts.
4. Sync and archive I12, then obtain a fresh ordinary review and publish.
5. Run I13 only in a separately authorized session with its required evidence
   surface available. Rollback is a scoped documentation commit revert.

## Open Questions

None. Missing execution access or any source/evidence mismatch remains a
typed stop for I13 and cannot widen I12.
