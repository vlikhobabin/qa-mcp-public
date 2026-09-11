## Context

R5 failed runtime review after repeated sanitizer bypasses. R5-R1 correctly
replaced open token classification with immutable positive schemas, exact
artifact contracts and A4 → R7 → A5 → R8, but its final normative spec still
assigned omission and typed-failure outcomes to the same declared mismatch.
The exact failed R5-R1 tree is
`66533b545db9acd4b7f922633ac773e8810c5190`, fingerprint
`sha256:607a1d1bbaa2b090ca7f5701fc7fcfeca0882a863c9095e5e6ea1ec262554044`,
retained in evidence-only stash commit
`d0adbd7f05cb52a690d1313ddc9e74aec6393025`.

## Goals / Non-Goals

**Goals:**

- preserve accepted R5/R5-R1 decisions from clean published `main`;
- make every public reconstruction outcome unique and testable;
- keep string admission finite, application-owned and independent of aliases;
- define exact artifact, receipt, structural and encoded-output boundaries;
- recreate a bounded independently reviewed runtime/integration handoff.

**Non-Goals:**

- no runtime implementation or failed-stash restoration;
- no lifecycle, live 1C, Windows, Docker, TestClient or external action;
- no new authority, provider setting, callback or wire protocol.

## Decisions

### 1. Use one outcome partition

The immutable schema is selected by exact admitted operation identity and binds
closed JSON paths to finite field classes. It is hard-coded application state,
contains no callbacks and cannot be supplied by settings, descriptors,
providers, executors or returned data.

The result partition is exhaustive and ordered:

1. an undeclared key is omitted without inspecting its value;
2. at a declared path, any wrong class, non-exact built-in type (including a
   subclass), non-member literal or otherwise invalid value aborts the complete
   reconstruction as fixed `invalid-executor-result`;
3. an exact valid declared value preserves or canonicalizes per its class;
4. only after reconstruction do aggregate bounds apply, with fixed
   `result-too-large` on final overflow.

There is no field-local redaction, partial result or alternate typed failure for
a declared mismatch. The fallback is built only from pre-snapshotted trusted
constants and contains no input fragment.

The finite class catalog is complete:

| Class | Exact valid domain | Public valid outcome |
| --- | --- | --- |
| `boolean` | exact built-in `bool`; `False` or `True` | preserve |
| `int64` | exact built-in `int`, excluding `bool`, from `-9,223,372,036,854,775,808` through `9,223,372,036,854,775,807` | preserve |
| `finite_number` | exact built-in `int` in the `int64` range or exact built-in finite `float`, excluding `bool` | preserve the numeric DTO value |
| `reference_count` | exact built-in `int`, excluding `bool`, from `0` through `2,147,483,647` | preserve |
| `literal_text` | exact built-in `str` equal to one path-local tuple member | preserve exact member |
| `documentation_url` | exact built-in `str` admitted by the published canonical public HTTP(S) fixed-point rules | preserve canonical URL |

The required direct matrix is unique:

| Class | Exact valid cells | Wrong-type cells | Subclass cell | Invalid-domain cells |
| --- | --- | --- | --- | --- |
| `boolean` | `False`, `True` | `0`, `1`, `"true"`, `None` | not applicable: built-in `bool` is not subclassable | not applicable: both exact values are valid |
| `int64` | minimum, `0`, maximum | string, float, `bool`, `None` | `int` subclass | minimum−1, maximum+1 |
| `finite_number` | int64 minimum/maximum, `-0.0`, `0.0`, `1.5` | string, decimal, `bool`, `None` | `int` and `float` subclasses | integer outside int64, `NaN`, positive/negative infinity |
| `reference_count` | `0`, `2,147,483,647` | string, float, `bool`, `None` | `int` subclass | `-1`, `2,147,483,648` |
| `literal_text` | exact tuple member | integer, mapping, `None` | `str` subclass | any exact built-in non-member string |
| `documentation_url` | canonical public HTTP(S) controls and admitted depth-1–4 control | integer, mapping, `None` | `str` subclass | private/local/userinfo/query/fragment/invalid authority and depth-5 non-fixed forms |

Every wrong-type, subclass and invalid-domain cell returns the identical
complete `invalid-executor-result` and no input fragment. The two explicitly
non-applicable boolean cells do not invent a synthetic Python type or domain.

### 2. Admit text only as application literals or canonical URLs

`literal_text` accepts an exact built-in string equal to a member of a frozen
tuple bound to one exact operation identity and JSON path. Each member is a
source-reviewed public product literal and is not runtime secret, connection,
path or endpoint data. Executor text is compared only by exact type/equality;
characters, tokens and endpoint shapes are never classified.
Each tuple is an exact built-in tuple of 1–64 unique exact built-in strings;
each member contains 1–2,048 Unicode scalars. Invalid application schema fails
composition and never becomes executor-controlled public-result behavior.

The direct matrix binds both `value.referenceLabel` and
`error.details.referenceLabel` to
`literal_text(("Reference label 7",))`. That exact string preserves. Every path,
assignment, `User Id`, `Data Source`, `accessKey`, `hostname`, IPv4/IPv6 local
endpoint, alternative string and string subclass returns the same complete
`invalid-executor-result`. Unknown-key omission is a separate cell and cannot
satisfy the declared-path oracle. `documentation_url` alone uses the published
fixed-point canonical public HTTP(S) URL rules.

### 3. Keep artifacts and full-local authority separate

| Field | Exact admission | Boundary controls | Invalid outcome |
| --- | --- | --- | --- |
| `artifact_id` | schema-declared exact built-in ASCII `[a-z][a-z0-9._-]{0,127}` | length 127/128 valid; 129, undeclared or subclass invalid | `invalid-executor-result` |
| `media_type` | schema-declared lower-ASCII type/subtype; each segment `[a-z0-9][a-z0-9.+-]{0,62}` | total 126/127 valid; 128, uppercase, parameter or undeclared invalid | `invalid-executor-result` |
| `sha256` | empty or `sha256:` plus 64 lowercase hex | empty/71 valid; 70/72/uppercase/non-hex invalid | `invalid-executor-result` |
| `sensitivity` | exact built-in `public` or `internal` | exact values valid; truncation/extension/private/case/subclass invalid | `invalid-executor-result` |
| executor `path` | never admitted | every executor value ignored | no authority |
| ledger receipt path | same-operation, canonical concrete path strictly below frozen root | 2,047/2,048 eligible; 2,049 invalid | `invalid-evidence-receipt` |

Validation order is schema/tuple shape, declared id/media type, hash and
sensitivity, then full-local receipt/path. A rejected artifact charges zero
shared nodes; an admitted artifact charges exactly five. Sanitized output never
emits a path. Full-local uses only the application ledger receipt.

### 4. Retain one total envelope and matrix

Depth 8, 64 items/container, 512 shared executor-content nodes, 2,048 scalars
per admitted schema string and 65,536 canonical UTF-8 bytes remain fixed.
Required aggregate controls include 511/512/513 nodes, receipt paths
2,047/2,048/2,049 and complete DTO bytes 65,535/65,536/65,537. The final byte
gate runs last and returns one bounded `result-too-large` fallback.

The direct R7 matrix covers path, credential/connection aliases and local
IPv4/IPv6 forms at the same exact declared value/error paths and artifact
fields, with exact controls preserved. The later R8 public URL matrix remains
`40 = 5 × (3 hostile + 1 control) × 2 paths`: exact encoding depths 1–4 reject
all credential/userinfo hostiles without fragments and preserve the canonical
control; depth 5 rejects every non-fixed input without fragments.

### 5. Replace the handoff

A4 authorizes only R7's future exact `3.inprogress` path at machine ceiling
301; R7 retains a hard 300 production-line cap. A5 then authorizes only R8's
future exact path at ceiling 301; R8 retains cap 300. Both authorizations forbid
new authority and wire protocol. R5/A3/R6 and R5-R1 remain blocked/superseded.
Only published R8 can unblock OSS-04E.

## Risks / Trade-offs

- Exact literal tuples intentionally cannot relay arbitrary executor prose;
  a new public phrase requires a reviewed schema change.
- Whole-result failure for declared mismatch loses partial executor content but
  yields one auditable secret-safe contract.
- The split adds sequential cards, but keeps each runtime payload independently
  bounded and reviewed.

## Migration Plan

1. Publish this design-only replacement after fresh GO.
2. Deliver A4, then R7 from clean published `main` with exact RED/green proof.
3. Deliver A5, then R8 with real MCP/ScenarioRunner integration proof.
4. Start OSS-04E only after reviewed R8 publishes.

## Open Questions

None. The mismatch outcome and successor authority are closed by this design.
