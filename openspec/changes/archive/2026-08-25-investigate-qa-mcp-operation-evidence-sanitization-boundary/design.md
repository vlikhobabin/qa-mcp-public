## Context

The published baseline is commit `bf66ce87425827739db5bcc20746d650a988138f`.
No operation-identity implementation has been published after OSS-04C. Two
unpublished lineages attempted it:

- OSS-04D final snapshot: tree `442179f51ecade55f129187f818a605c1705201d`,
  fingerprint `sha256:aa1e70f5bdd859958795f63c6c2c73fed2d2e36d8055ed8d03c557f51dfbf826`;
- OSS-04D-R1 final snapshot: tree `3e3e250b67801beeb6a908592dae433fe97523b1`,
  fingerprint `sha256:23e72e6121ec8a26e3b7ea33e0fd25635aa47ca3c53ae28e7463bdb1e2450181`.

Each lineage exhausted two rescues. The recurring failures are architectural:
executor-controlled data and core-trusted provenance share serializers;
field sensitivity is inferred by expanding token/substring rules; URL secrecy
is inferred by regex; malformed objects are introspected outside one total
exception boundary. Fixing individual spellings and address forms therefore
alternates between leakage and over-redaction.

This investigation uses the retained verdicts, histories, bounded RED evidence
and available checkpoint diffs as offline sources. Only the OSS-04D-R1 stash
reconstructs its exact final reviewed tree; the older OSS-04D stash is an
explicitly identified checkpoint and is not claimed as exact recovery. The
investigation makes no protocol claim, uses no frame range or dynamic
TestClient field, and needs no capture, replay, live 1C, Windows, Docker or
runtime cleanup.

## Goals / Non-Goals

**Goals:**

- define one owner for every public result field;
- make serialization total, bounded and secret-safe for hostile values;
- replace heuristic URL matching with structured parsing and address classes;
- preserve declared public metadata without broad token exceptions;
- keep route admission before either concrete executor;
- prepare exact authorization and implementation successors.

**Non-Goals:**

- implement or publish the operation-identity runtime in this card;
- reapply either failed stash as a new implementation baseline;
- add a new runtime authority, evidence policy or wire contract;
- start OSS-04E lifecycle admission or OSS-04F runtime evidence work;
- use Windows or live TestClient evidence for a design-only payload.

## Decisions

### 1. Reimplement from the published baseline

The successor SHALL use `bf66ce87425827739db5bcc20746d650a988138f` plus
this published design as its semantic baseline. Failed stashes are evidence and
test-source material only. Production code is not restored wholesale.

Alternative rejected: continue patching OSS-04D-R1. It is already `300/300`
production lines, has exhausted its review budget, and repeats the same defect
class.

### 2. Separate trusted provenance from untrusted content

The operation boundary SHALL construct a new public result from two channels:

1. core-trusted target, session, operation, binding generation and evidence
   policy, derived only after route/binding validation;
2. executor-controlled value, error and artifact content, admitted through a
   total public normalizer.

Executor-provided provenance is ignored, not sanitized in place. Every emitted
identifier is checked against a bounded scalar grammar and length. An invalid
trusted-field candidate produces a stable typed failure and no raw candidate.

Alternative rejected: `dataclasses.replace()` on executor result subclasses.
It retains hostile fields, descriptors and serializer behavior.

### 3. Use explicit public DTO serializers

The successor SHALL provide one public serializer module for
`OperationResult`, `OperationError`, `ArtifactReference`, `TargetIdentity` and
`SessionIdentity`. It SHALL reconstruct exact public dataclasses before
serialization and SHALL catch the whole snapshot/normalization operation.

Unknown objects are represented by a stable redacted sentinel. The normalizer
does not execute arbitrary `to_result` properties or callbacks. Mapping
iteration, key conversion, scalar access and sequence traversal are all inside
the exception boundary. Depth, collection size, string length and total output
size have explicit ceilings. No raw exception, attribute, traceback or input
fragment reaches the public result.

Alternative rejected: recursive best-effort introspection. It creates an
unbounded callback surface and repeatedly escaped through exceptional fields.

### 4. Classify fields by anchored semantic names

Field names SHALL be normalized deterministically across separators and case,
then matched against closed, anchored semantic names. Sensitive patterns may
include explicit domain prefixes such as `db_reference` or
`provider_reference`, and the exact `reference_name` alias. They SHALL NOT
classify a field merely because any token equals `reference`.

An explicit public-metadata registry precedes sensitive matching. It includes
the documented URL aliases and benign controls required by the verification
matrix, such as `reference_count`, `reference_label` and
`documentation_reference`. Unknown fields remain structurally visible, but
their values still pass through bounded scalar/inline-secret normalization.

Alternative rejected: growing an `any(token in sensitive)` set. It necessarily
over-redacts unrelated fields while still missing new compound spellings.

### 5. Parse and classify documentation URLs structurally

Public documentation URL fields SHALL use `urllib.parse.urlsplit` and
`ipaddress.ip_address`, not route regexes. Admission requires:

- scheme `http` or `https`;
- a hostname and no username, password or other userinfo, including encoded
  forms;
- an IP hostname with `is_global == true`; when strict IP parsing fails, a
  bounded legacy-numeric grammar classifies one to four dot-separated
  components, each either ASCII digits or `0x` plus ASCII hexadecimal digits,
  as numeric-host syntax and rejects them without value interpretation rather
  than admitting them as DNS;
- a remaining non-numeric canonical DNS name that is not localhost,
  single-label, `.local` or `.internal`;
- no credential-bearing query field; the sanitized representation omits query
  and fragment unless the successor explicitly implements their same bounded
  field policy.

RFC documentation-only hostnames may be admitted as inert test fixtures. All
loopback spellings, shortened/legacy numeric IPv4, RFC1918, carrier/private, link-local,
unspecified, multicast, reserved and private IPv6 forms are rejected.

Alternative rejected: enumerate private address regexes or let strict-IP parse
failures fall through to DNS. Alternate IPv4 text, IPv6, userinfo and encoding
make the former incomplete, while the latter admits compact numeric routes
such as `127.1`, `0177.0.0.1` and `0x7f.1`.

### 6. Make artifact and error policy closed

Under `sanitized`, every artifact scalar—including provenance—is reconstructed
and validated. Artifact paths are absent. Under `full_local`, a path is emitted
only when core code supplies the unforgeable seal and the resolved path remains
inside the approved evidence root at serialization time.

Errors are reconstructed with a boolean `retryable`, bounded public code and
message, and normalized mapping details. Any field access or conversion failure
returns the same typed `invalid-executor-result` class with no nested original
exception.

### 7. Keep route admission independent and first

A pure admission step SHALL validate target, session, attachment, binding
generation and current host/port/display before adapter invocation. Exactly
`session=None` plus `attachment=None` may use pre-session lifecycle admission.
Every asymmetric state blocks with zero Local and Windows adapter calls.

Serialization never grants route authority and route fallback never repairs an
inconsistent bound state.

### 8. Require separate authorization and implementation cards

This design does not authorize a large or repeated-defect implementation by
itself. It SHALL create:

1. `oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload`, an exact
   authorization source bound to this completed investigation and one
   successor, ceiling `500`, no new authority or wire protocol;
2. `oss-04d-r3-implement-typed-operation-evidence-boundary`, the only runtime
   successor, dependent on the published investigation and authorization.

OSS-04E remains blocked until OSS-04D-R3 publishes with a fresh GO.

## Adversarial Verification Matrix

The implementation successor SHALL test the cross-product needed to observe
the decisions, with bounded pairwise reduction where combinations are
equivalent:

| Surface | Hostile classes | Safe controls | Required outcome |
| --- | --- | --- | --- |
| Provenance | secret/path data in every target/session/operation/binding scalar | bounded logical ids and fingerprints | reconstructed or typed failure; no executor provenance |
| Artifact | direct/bound, malformed scalar, forged/full-local path, exceptional subclass | safe id/media/hash/sensitivity; sealed in-root path | all sanitized scalars safe; path only sealed and contained |
| Error | every scalar, details mapping, property/items/key/value exceptions, recursive data | typed boolean and bounded details | stable typed error; no escaping exception/input graph |
| Value | mappings, sequences, paths, unknown objects, cycles/depth/size | JSON scalars and benign nested data | bounded JSON-safe output or redacted sentinel |
| Field names | credential/route aliases across case/separators/prefixes | referenceCount, referenceLabel, documentationReference | exact anchored classification; controls preserved |
| URLs | compact/legacy numeric hosts (`127.1`, `0177.0.0.1`, `0x7f.1`), canonical loopback, all non-global IPv4 classes, private/link-local IPv6, encoded/user-only userinfo, internal DNS | canonical global IPv4/IPv6, public HTTP(S) docs and RFC documentation fixtures | numeric strict-parse failures never reach DNS; private/credential routes absent; admitted docs canonicalized |
| Routing | foreign target/session/generation/endpoint, both asymmetric states | current attachment; true pre-session lifecycle; unbound legacy | block before Local/Windows or preserve declared compatibility |
| Verdicts | success/blocked/ambiguous/failure through MCP and scenario | same trusted request | identical bounded provenance and taxonomy |

The successor needs exact test-first evidence, focused MCP/scenario/runtime
tests, the full non-live suite, strict OpenSpec, Python compilation, diff and
manifest checks, plus exact-source Windows offline executor proof. Live 1C is
not required unless successor scope changes beyond this design.

## Risks / Trade-offs

- [Risk] Explicit public schemas may omit a legitimate future field. → Add it
  through a reviewed registry entry and positive/negative controls, not a broad
  token exception.
- [Risk] Reconstructing DTOs may break callers relying on subclass behavior. →
  Keep legacy behavior only for unbound execution and document the project-bound
  public contract; unknown bound subclasses fail closed.
- [Risk] A 500-line authorization can invite scope growth. → Bind it to one
  successor, one capability, no new authority/wire protocol and mandatory
  source breakdown in preflight.
- [Risk] Stashed tests can bias the new design toward old implementation. → Use
  them only as RED fixtures after requirements and matrix are independently
  materialized from the reviewed findings.

## Migration Plan

1. Publish this investigation/design card without production code.
2. Publish the exact authorization source bound to the named successor.
3. Implement OSS-04D-R3 from the safe baseline, selectively porting only
   evidence-backed tests from the failed stashes.
4. Obtain a fresh independent review and publish OSS-04D-R3 on GO.
5. Mark the original OSS-04D lineage superseded and unblock OSS-04E.

Rollback for this card is documentation-only: revert its scoped commit. The
failed runtime payloads remain unpublished. The R1 final tree and the older
OSS-04D checkpoint remain recoverable in named stashes; exact recovery of the
final OSS-04D tree is not claimed or required by the successor.

## Open Questions

- None for the investigation. Any request to preserve documentation URL query
  or fragment data is a successor scope change and needs an explicit field
  policy before implementation.
