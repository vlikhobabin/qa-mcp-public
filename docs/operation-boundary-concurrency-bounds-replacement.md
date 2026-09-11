# Operation Boundary Concurrency And Bounds Replacement

## Lineage

OSS-04D-R5-R2 is the publishable design source extending the reviewed R4-R1
foundation and replacing four exact unpublished payloads:

- R3 tree `2fb0ad5b7a55aa2575314b33ea56f4dfd4510d98`, fingerprint
  `sha256:e75d981bc6c39c8724ffe8f57b4e6679ab7a63c82ee5fd9ffcac47a5239a44aa`;
- R4 tree `d09f7b834e415d08b43e6be3da1ed63edfe0109c`, fingerprint
  `sha256:05aa7a5edd265d08330c9ddec5830ec32bb40297e590a126d03954264e608be8`.
- R5 tree `d8489cac98416b446c26932677dab4cff347b2ed`, fingerprint
  `sha256:96a36a0d655653516fbf05652f24a5b41bcbd7b8437ecca90df485b33bd38575`;
- R5-R1 tree `66533b545db9acd4b7f922633ac773e8810c5190`, fingerprint
  `sha256:607a1d1bbaa2b090ca7f5701fc7fcfeca0882a863c9095e5e6ea1ec262554044`.

Named stashes `oss04d-r3-exhausted-review-payload-20260825`,
`oss04d-r4-exhausted-review-payload-20260825`,
`oss04d-r5-exhausted-review-payload-20260826` and
`oss04d-r5-r1-exhausted-review-payload-20260826` independently reconstruct
those snapshots. They remain ignored evidence and are never merged or restored
wholesale.

## Closed Design

- Evidence authority belongs to an `ApplicationContext` ledger and a distinct
  admitted-operation scope, never module-global or executor-returned state.
- Sanitized artifacts never expose paths; approved full-local paths require a
  current same-operation receipt strictly contained under the evidence root;
  canonical path scalar cells are 2,047/2,048/2,049.
- Operation, target, session, binding, fingerprint and generation each have a
  separate exact grammar after universal physical/path-form rejection.
- Public reconstruction uses an immutable application-owned schema. An
  undeclared key is omitted without value inspection. At a declared path, any wrong
  class, non-exact built-in type/subclass, non-member literal or invalid value
  aborts the complete reconstruction as fixed `invalid-executor-result`; no
  partial field or alternate declared-mismatch outcome is emitted.
- `literal_text` admits only exact equality to a source-reviewed public literal
  in a hard-coded frozen tuple bound to one operation and JSON path. Settings,
  descriptors, providers, executors and returned data cannot supply the tuple;
  no character, token, alias or endpoint classifier is used.
- The complete class catalog is finite: exact built-in `boolean`;
  signed-64 `int64`; signed-64 integer or finite exact built-in float
  `finite_number`; exact built-in `reference_count` from 0 through
  2,147,483,647; operation/path-local `literal_text`; and exact built-in
  canonical public HTTP(S) `documentation_url`.
- Each class has paired valid, wrong-type, subclass and invalid-domain cells.
  `boolean` marks subclass/domain cells not applicable because Python `bool`
  cannot be subclassed and both exact values are valid. Every applicable
  invalid cell yields the same complete `invalid-executor-result` without an
  input fragment.
- Artifact id, media type, SHA and sensitivity use exact field-local grammars;
  an admitted artifact charges five shared nodes, a rejected artifact zero,
  and executor path data never grants authority.
- Public reconstruction is bounded at depth 8, 64 items, 512 shared nodes and
  2,048 scalars per admitted schema string. Complete canonical UTF-8 JSON cells
  are 65,535/65,536/65,537 bytes; final overflow returns fixed
  `result-too-large`.
- Pure route admission precedes evidence and adapter invocation. One outer
  boundary contains snapshot, traversal, URL, receipt and encoding failures.

## Exact URL Matrix

URL authority/userinfo and path are decoded separately for at most four rounds.
Every intermediate is checked. Admission requires a fixed point and emits one
canonical encoding. Query/fragment are absent.

For each exact depth below, both real MCP and ScenarioRunner execute all cells:

| Depth | Credential-path hostile | Authority/userinfo hostile | Paired control | Oracle |
| ---: | --- | --- | --- | --- |
| 1 | assignment encoded once | `user@`, `user:pass@` encoded once | benign path encoded once; no-userinfo authority | hostile absent with no original/decoded fragment, control canonical |
| 2 | assignment encoded twice | both userinfo forms encoded twice | benign path encoded twice; no-userinfo authority | hostile absent with no original/decoded fragment, control canonical |
| 3 | assignment encoded three times | both userinfo forms encoded three times | benign path encoded three times; no-userinfo authority | hostile absent with no original/decoded fragment, control canonical |
| 4 | assignment encoded four times | both userinfo forms encoded four times | benign path encoded four times; no-userinfo authority | hostile absent with no original/decoded fragment, control canonical |
| 5 | assignment encoded five times | both userinfo forms encoded five times | benign path encoded five times | all reject non-fixed; no fragment |

Depth-5 benign rejection is a bound control, not credential classification.
Depths 1–4 must preserve the same canonical safe URL. A path `@` is path data;
literal or decoded authority `@`, username or password is always rejected.

## Positive Admission And Stable Rows

The successor evidence matrix has stable ids:

1. `isolation` — overlapping contexts and exceptional mapping;
2. `provenance` — path candidates plus controls for all six fields;
3. `structure` — depth/item/node/string/UTF-8/aggregate boundaries;
4. `URL` — the complete exact depth table above at core;
5. `artifact` — forged and current receipt cases;
6. `public-verdicts` — four verdicts through MCP and ScenarioRunner;
7. `public-URL-paths` — the complete depth table through both real paths.

Each row includes a hostile, paired control, public surface and exact oracle.
Runtime successors retain intended-oracle RED evidence before implementation.
The `public-URL-paths` row has exactly
`40 = 5 × (3 hostile + 1 control) × 2 paths` cells.

Direct value/error cells always use the same exact paths,
`value.referenceLabel` and `error.details.referenceLabel`, each bound to
`literal_text(("Reference label 7",))`. The exact built-in safe literal
preserves. Every alternative string, path/assignment/alias/local endpoint or
string subclass returns complete fixed `invalid-executor-result` without input
fragments. Unknown-key omission is verified separately.

Numeric/type cells are equally exact: `int64` tests minimum/zero/maximum plus
outside bounds; `finite_number` tests signed-64 integer boundaries, finite
floats, out-of-range integers, `NaN` and infinities; `reference_count` tests
0/2,147,483,647 plus −1/2,147,483,648. Wrong types and int/float/string
subclasses return the complete fixed result. Documentation URL controls include
canonical public values, wrong types/subclass and private/local/userinfo/query/
fragment/invalid-authority/depth-5 non-fixed invalid domains.

Artifact validation order and controls are exact:

| Field | Valid controls | Invalid controls/outcome |
| --- | --- | --- |
| `artifact_id` | declared lower-ASCII grammar, length 127/128 | length 129, undeclared, subclass → `invalid-executor-result` |
| `media_type` | declared lower-ASCII type/subtype, total 126/127 | 128, uppercase, parameter, undeclared → `invalid-executor-result` |
| `sha256` | empty or exact 71-character lowercase digest form | 70/72/uppercase/non-hex → `invalid-executor-result` |
| `sensitivity` | exact built-in `public`/`internal` | truncation/extension/private/case/subclass → `invalid-executor-result` |
| receipt path | same-scope canonical 2,047/2,048 | 2,049 → `invalid-evidence-receipt` |

## Ordered Handoff

1. A4 authorizes only R7's future exact `3.inprogress` path, ceiling 301.
2. R7 implements core ledger/normalizer at a stricter cap of 300 lines.
3. A5 authorizes only R8's future exact `3.inprogress` path, ceiling 301.
4. R8 integrates route/MCP/scenario at a stricter cap of 300 lines.

Both authorization sources set new authority/wire protocol to false. Exhausted
R5/R5-R1 and former A3/R6 stay blocked/superseded. R8 alone unblocks OSS-04E.
This design payload performs no Windows, TestClient, Docker, host-agent, live
1C, protocol or other external action.
