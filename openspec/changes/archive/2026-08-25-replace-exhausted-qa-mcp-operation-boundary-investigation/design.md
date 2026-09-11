## Context

Published `main` at replacement start is
`00a7190c45d55ca1f6c353848f4b2563982ac081`. No OSS-04D operation-boundary
runtime has been published after OSS-04C. Two exact unpublished sources remain
read-only evidence:

- R3 implementation: tree `2fb0ad5b7a55aa2575314b33ea56f4dfd4510d98`,
  fingerprint
  `sha256:e75d981bc6c39c8724ffe8f57b4e6679ab7a63c82ee5fd9ffcac47a5239a44aa`,
  stash `oss04d-r3-exhausted-review-payload-20260825`;
- R4 investigation: tree `d09f7b834e415d08b43e6be3da1ed63edfe0109c`,
  fingerprint
  `sha256:05aa7a5edd265d08330c9ddec5830ec32bb40297e590a126d03954264e608be8`,
  stash `oss04d-r4-exhausted-review-payload-20260825`.

Each stash independently reconstructs its claimed tree/fingerprint from its
recorded baseline. Both histories end at review cycle 3 with rescue budget
`2/2`. R4's final review accepted seven of eight card criteria and retained one
blocker: exact userinfo encoding depths and paired controls were stricter in the
durable document than in design/spec/R6.

This replacement restates accepted R4 decisions from published `main` and
closes that one handoff gap. It has no capture source, protocol frame, dynamic
field, replay plan or runtime cleanup because it changes no runtime behavior
and performs no external action.

## Goals / Non-Goals

**Goals:**

- retain exact R3/R4 lineage without using failed code/design as a baseline;
- specify context-local evidence authority and total public reconstruction;
- specify field-specific provenance and actual encoded output bounds;
- make URL credential and userinfo cases exact at depths 1–5 with controls;
- recreate independently reviewable A2 → R5 → A3 → R6 delivery.

**Non-Goals:**

- implement, restore or publish either exhausted payload;
- add a runtime authority, evidence policy, wire protocol or artifact store;
- defend against arbitrary code execution inside the Python process;
- start OSS-04E/04F, live 1C, Windows, Docker or TestClient work.

## Decisions

### 1. Rebuild from published main

Successors SHALL use published `main` plus this archived design. Stashes may be
read for exact lineage and RED-oracle derivation only. Production hunks SHALL
NOT be restored wholesale.

Alternative rejected: one more R4 edit. Its independent rescue budget is
exhausted, so policy requires this linked replacement.

### 2. Use explicit context-local evidence scopes

Each `ApplicationContext` SHALL own an internal `EvidenceLedger`; each admitted
operation opens a distinct scope and closes it in `finally`. No module global,
`ContextVar`, active flag, closure registrar or executor-returned object grants
path authority. Two overlapping contexts cannot observe or change each other's
receipts or failure state.

First-party composition may record a typed receipt. Executor result data,
including artifact path/policy/provenance/callbacks, remains hostile. This is a
data boundary, not an in-process Python sandbox.

### 3. Derive full-local paths only from current receipts

`sanitized` artifacts never emit a path. Approved `full_local` artifacts may
emit only a same-operation receipt that resolves strictly below the frozen
evidence root at serialization time. Missing, duplicate, foreign, stale,
symlinked or out-of-root receipts fail with a fixed typed result. A matching
executor-supplied path provides no authority.

### 4. Validate every provenance field with its own grammar

A common physical-form filter rejects controls, whitespace drift, slash and
backslash, UNC/device/URI/assignment forms and every `^[A-Za-z]:` drive prefix,
including drive-relative paths. Then exact full-match rules apply:

- operation: `[a-z][a-z0-9_.-]{0,63}`;
- target/session/binding: `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`;
- fingerprint: lowercase `sha256:` plus exactly 64 hexadecimal digits;
- generation: exact positive built-in `int`, excluding `bool` and subclasses.

Path-form candidates and paired valid controls SHALL be tested separately for
operation, target, session, binding, fingerprint and generation before either
adapter is called.

### 5. Bound structure and the complete canonical JSON bytes

Traversal limits are depth 8, 64 items per container, 512 total nodes and 2048
Unicode scalar values per string. The authoritative envelope is the complete
public DTO encoded using canonical `json.dumps` options and UTF-8; it SHALL be
at most 65,536 bytes.

If the candidate exceeds the envelope, all executor content is replaced by one
fixed `result-too-large` error while admitted core provenance remains. The
fallback is encoded again and asserted below the ceiling. No per-input
sentinels are emitted after exhaustion.

### 6. Decode URL authority and path to a bounded fixed point

Only registered documentation aliases use URL admission. Input is limited to
2048 Unicode scalars. Scheme is HTTP(S); port is valid; host is canonical
global IP, admitted documentation fixture or bounded public DNS; query and
fragment are omitted.

Authority/userinfo and path are checked as separate components. For each
component, percent decoding runs at most four rounds, and every intermediate is
checked. Authority rejects any literal or decoded username, password, `@`,
encoded userinfo delimiter or credential assignment. Path rejects decoded
credential/connection assignment but permits a benign `@` as path data. The
input is admitted only when both components reach a fixed point; a remaining
valid `%HH` after round four rejects the URL. Output is one canonical encoding
of the fully decoded safe components, never the original representation.

The exact required depth matrix is:

| Depth | Credential-path hostile | Authority/userinfo hostile | Paired safe control |
| ---: | --- | --- | --- |
| 1 | assignment encoded once | `user@` and `user:pass@` delimiter encoded once | benign path encoded once, canonical authority without userinfo; hostile absent with no original/decoded fragment, control canonical |
| 2 | assignment encoded twice | both userinfo forms encoded twice | benign path encoded twice, canonical authority without userinfo; hostile absent with no original/decoded fragment, control canonical |
| 3 | assignment encoded three times | both userinfo forms encoded three times | benign path encoded three times, canonical authority without userinfo; hostile absent with no original/decoded fragment, control canonical |
| 4 | assignment encoded four times | both userinfo forms encoded four times | benign path encoded four times, canonical authority without userinfo; hostile absent with no original/decoded fragment, control canonical |
| 5 | assignment encoded five times | both userinfo forms encoded five times | benign path encoded five times; reject as non-fixed solely by the four-round bound |

For every depth, neither hostile nor rejected-control fragments may emit. The
depth 1–4 safe controls emit one identical canonical URL. The complete table
SHALL run at the core boundary and through both real MCP and ScenarioRunner.
The public-path table is exactly
`40 = 5 × (3 hostile + 1 control) × 2 paths` cells.

### 7. Keep one stable seven-row matrix

| Row id | Hostile cases | Controls | Oracle |
| --- | --- | --- | --- |
| isolation | overlapping contexts, one exceptional mapping | two ordinary concurrent results | isolated typed results and deterministic teardown |
| provenance | physical/path candidates in all six fields | exact valid value for each field | block before Local/Windows; controls preserve |
| structure | depth/item/node/string/wide UTF-8/aggregate overflow | below and exact bounds | complete JSON within 65,536 or fixed typed fallback |
| URL | exact credential and userinfo depth table 1–5 | exact paired controls in the table | hostile absent; depths 1–4 canonical; depth 5 bounded rejection |
| artifact | forged path/policy/provenance, stale/foreign/duplicate receipt | current contained receipt | path only from current ledger under approved policy |
| public verdicts | success/blocked/ambiguous/failure | identical request | MCP/scenario taxonomy and provenance identical |
| public URL paths | complete URL depth table through MCP and ScenarioRunner | every paired table control through both | identical absence/preservation and total JSON |

Each runtime successor SHALL retain RED evidence for its assigned rows before
implementation. A row is complete only when its stable id, hostile set,
controls, public surface and oracle are all present.

### 8. Route before evidence and serialization

Pure route admission accepts only a current bound target/session/attachment/
generation/endpoint tuple, true both-absent pre-session lifecycle or declared
unbound compatibility. Malformed, foreign and asymmetric states block with
zero adapter calls. The evidence scope opens after admission; serialization
cannot repair, retry or change route authority.

### 9. Contain the whole reconstruction

Snapshot, exact-type checks, mapping iteration, scalar conversion, receipt
lookup, URL parsing and final encoding stay inside one outer exception
boundary. Unexpected failures become a fixed `invalid-executor-result` with no
cause, context, traceback, attribute or input-bearing text.

### 10. Recreate one-to-one bounded successors

The replacement SHALL create:

1. A2 authorization, bound only to R5's future exact `3.inprogress` path,
   machine ceiling 301, authority/wire false;
2. R5 core boundary, stricter implementation cap 300;
3. A3 authorization after R5, bound only to R6's future exact `3.inprogress`
   path, machine ceiling 301, authority/wire false;
4. R6 route/MCP/ScenarioRunner integration, stricter implementation cap 300.

The 301 ceiling is the minimum authorization schema value; implementations may
not use the extra line. R6 alone unblocks OSS-04E. Each runtime card needs its
own fresh review; if it exceeds 300 lines it returns to investigation.

## Risks / Trade-offs

- [Risk] Strict URL fixed-point handling rejects deeply encoded benign paths. →
  The depth-5 safe control explicitly proves bounded rejection; depths 1–4
  prove canonical preservation.
- [Risk] Ledger lifecycle adds composition state. → Scope it per admitted
  operation and require concurrent teardown tests.
- [Risk] Strict field grammars reject legacy ids. → Expand only one field with
  paired hostile neighbors through a reviewed spec change.
- [Risk] Whole-envelope fallback drops benign partial content. → Preserve
  deterministic provenance/error taxonomy rather than ambiguous truncation.

## Migration Plan

1. Publish this design-only replacement.
2. Deliver/publish A2, then R5.
3. Deliver/publish A3, then R6 with exact-source Windows offline proof.
4. Mark R3/R4 superseded and unblock OSS-04E only after R6 GO/publish.

Rollback is documentation-only. Exact failed stashes remain ignored evidence
and are never merged. Runtime rollback belongs to R5/R6.

## Open Questions

- None. Query/fragment preservation, another provenance syntax or executor-
  supplied local-path authority is a new design scope.
