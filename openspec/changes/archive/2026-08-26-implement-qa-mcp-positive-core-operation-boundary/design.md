## Context

`qa_mcp.core` currently exposes neutral DTOs and passes executor results through
unchanged. Published R5-R2 defines a replacement contract after multiple
denylist and ambient-authority implementations exhausted review; published A4
authorizes only this R7 card at machine ceiling 301 while R7 keeps a hard
300-added-production-line cap. Failed stashes are read-only evidence and are
not an implementation source to restore.

## Goals / Non-Goals

**Goals:**

- compose one immutable callback-free schema catalog per
  `ApplicationContext` from source-owned constants;
- admit sealed logical provenance and application-owned evidence receipts;
- reconstruct executor results through a closed positive schema with one
  complete failure for every declared mismatch;
- make URL, artifact, structure, node, receipt and final-byte behavior total
  and exact;
- retain test-first Linux evidence and exact-source Windows offline evidence.

**Non-Goals:**

- no MCP, ScenarioRunner, lifecycle or executor routing changes;
- no live 1C, protocol capture/replay, Docker, host-agent or external action;
- no new callback, provider setting, public authority or wire contract;
- no wholesale restoration of R5/R5-R1 or any other failed stash.

## Decisions

### 1. Application composition owns a sealed finite schema

The new boundary module defines deeply immutable tuple object/array nodes and leaf
rules for exactly six public classes: `boolean`, `int64`, `finite_number`,
`reference_count`, `literal_text` and `documentation_url`. A private composer
builds a read-only mapping for `ApplicationContext.operation_schemas`; the
field is `init=False`, assignment/deletion is blocked, and reconstruction checks
the exact source tuple and application-composed catalog identities. Settings, target
profiles, executors, result data and callers cannot supply a mapping, rule,
literal tuple or callback.

The direct `read_active_window` schema closes `value` and `error.details` over
the six scalar classes plus source-owned array/object structure used to prove
depth, item, node and byte bounds. Both
`value.referenceLabel` and `error.details.referenceLabel` bind exact
`literal_text(("Reference label 7",))`. Documentation URLs and numeric classes
have their own exact paths. An artifact slot is schema-declared, while each
artifact field still has its independent exact grammar.

Alternative rejected: accepting a schema argument or generic dynamic mapping
would let executor/provider data choose disclosure behavior and repeat the
failed authority model.

### 2. Reconstruction uses one ordered outcome partition

`normalize_operation_result(context, request, raw, provenance, ...)` snapshots
trusted fallback constants before touching the executor DTO and then applies:

1. validate the exact context catalog, request and sealed provenance;
2. require an exact `OperationResult`, exact verdict/error shape and a schema
   for the exact admitted operation;
3. rebuild only declared value/error-detail keys; unknown exact-string keys are
   omitted without reading their values;
4. abort the entire result as fixed `invalid-executor-result` on any declared
   wrong class, non-exact built-in type/subclass or invalid domain;
5. validate artifacts and any full-local receipts in the published order;
6. encode the complete reconstructed DTO and replace it with fixed
   `result-too-large` only when an aggregate structural/byte bound is exceeded.

There is no partial result. Executor request/provenance/path, arbitrary error
code/message and undeclared values are never emitted. Non-success verdicts use
source-owned fixed error code/message constants; only exact boolean
`retryable` and declared details are reconstructed. The rebuilt request comes
from admitted provenance and the original exact operation kind.

### 3. Leaf classes are exact

- `boolean`: exact built-in `bool` only;
- `int64`: exact built-in non-boolean integer in signed 64-bit range;
- `finite_number`: such an integer or exact finite built-in `float`;
- `reference_count`: exact built-in non-boolean integer from 0 through
  2,147,483,647;
- `literal_text`: exact built-in string equal to one frozen path-local member;
- `documentation_url`: exact built-in string accepted and canonicalized by the
  bounded public HTTP(S) fixed-point algorithm.

Frozen literal tuples contain 1–64 unique exact built-in strings of 1–2,048
Unicode scalars. Catalog composition accepts no dynamic schema input. Boolean's subclass
and invalid-domain cells are explicitly not applicable.

### 4. Documentation URLs have one fixed-point canonicalizer

Scheme and host canonicalize to lower case; default ports are removed; IDNA
host labels and path quoting become canonical. Query and fragment are absent.
Authority and path are decoded separately and checked after every round. Up to
four changing rounds are admitted only when the next round is a fixed point.
Literal or decoded authority userinfo, credential assignments in the path,
private/loopback/link-local/multicast/unspecified/reserved non-documentation
addresses, local hostnames, malformed authority/port/percent/UTF-8 and any
fifth changing round reject as `invalid-executor-result`. Exact-depth 1–4
benign encoded paths converge to one canonical URL; depth 5 rejects.

### 5. Evidence authority is context-local and exact-scope

Each context owns a frozen `EvidenceLedger` derived only from its immutable
runtime-target evidence root/policy (or sanitized/no-root defaults). The ledger
accepts only the platform's exact built-in `Path` class, resolves existing
paths strictly, rejects a symlink root or chain and requires a concrete path
strictly below the frozen root.

`ledger.operation()` creates an unforgeable active token. `scope.record(...)`
returns a frozen receipt, while the ledger retains the authoritative
token/id/path record. Full-local reconstruction accepts only a current receipt
from the exact ledger, scope and artifact id and rechecks containment. Sanitized
artifacts omit path unconditionally. Scopes close and erase only their own
records even when reconstruction or the caller raises.

### 6. Local and aggregate bounds are deterministic

- admitted container depth: 8 (value/error-details root is depth 1);
- raw items in each admitted container: 64;
- shared admitted executor-content nodes: 512; mapping keys count zero;
- application literal/URL scalar: 2,048 Unicode scalars;
- receipt canonical path: 2,048 Unicode scalars;
- complete compact sorted UTF-8 DTO: 65,536 bytes.

Each admitted scalar/container charges one shared node. A rejected artifact
charges zero; an admitted artifact charges exactly five after id, media, SHA
and sensitivity validation. Artifact id uses exact built-in ASCII
`[a-z][a-z0-9._-]{0,127}`; media uses lower-ASCII type/subtype segments
`[a-z0-9][a-z0-9.+-]{0,62}`; SHA is empty or `sha256:` plus 64 lower hex; and
sensitivity is exact `public` or `internal`. Receipt validation follows those
fields. The final byte gate runs last over `OperationResult.to_dict()`.
An overlong declared literal/URL is a field-domain mismatch and therefore uses
`invalid-executor-result`; `result-too-large` is reserved for aggregate
container/depth/node/final-byte overflow after individually valid fields.

### 7. The implementation remains a bounded core-only surface

Production additions across `src/qa_mcp/core/` MUST remain at most 300 lines
relative to published A4 `main`. R7 exports the schema/provenance/ledger and
normalizer primitives and documents them, but existing
`execute_operation`, MCP and ScenarioRunner aliases remain unchanged. R8 owns
public routing integration.

## Risks / Trade-offs

- **Finite schemas reject new executor fields by default** → omission is the
  intended safe default; a new public field requires a reviewed source rule.
- **Whole-result failure loses otherwise valid sibling data** → one complete
  outcome is more auditable and cannot leak partial hostile input.
- **Tight line cap encourages dense code** → keep helpers cohesive, require
  compile/static review and count only actual production additions.
- **Windows path semantics differ from Linux** → run the exact source artifact
  in an owned Windows staging directory and retain pre/post process/listener/
  staging inventory without live 1C.

## Migration Plan

1. Add intended-oracle tests and retain the failing RED result.
2. Implement the sealed schema, provenance, ledger and normalizer within the
   300-line production cap.
3. Pass direct/focused/full Linux verification and exact-source Windows
   offline proof with owned cleanup.
4. Sync this capability and archive the change; do not connect public routes.
5. After fresh review and publish, deliver A5 then R8 for integration.

Rollback is the scoped R7 commit; no persisted format, live runtime or external
resource is changed.

## Open Questions

None. R5-R2 and A4 close the contract and authorization.
