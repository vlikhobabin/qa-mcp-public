# Operation Evidence Sanitization Boundary

## Decision Status

This document is the OSS-04D-R2 investigation decision. It defines the only
approved design input for the next operation-identity implementation. It does
not publish runtime behavior and does not authorize a large implementation by
itself.

Published runtime baseline: `bf66ce87425827739db5bcc20746d650a988138f`.

## Exhausted Lineage

| Lineage | Final tree | Diff fingerprint | Final review | Rescue budget |
| --- | --- | --- | --- | --- |
| OSS-04D | `442179f51ecade55f129187f818a605c1705201d` | `sha256:aa1e70f5bdd859958795f63c6c2c73fed2d2e36d8055ed8d03c557f51dfbf826` | cycle 3 `NO-GO` | `2/2`, exhausted |
| OSS-04D-R1 | `3e3e250b67801beeb6a908592dae433fe97523b1` | `sha256:23e72e6121ec8a26e3b7ea33e0fd25635aa47ca3c53ae28e7463bdb1e2450181` | cycle 3 `NO-GO` | `2/2`, exhausted |

Canonical ignored evidence remains at:

- `.runtime/changerail/reviews/oss-04d-propagate-target-session-operation-identity.json`
  and matching `.history.json`;
- `.runtime/changerail/reviews/oss-04d-r1-replace-operation-identity-after-exhausted-review.json`
  and matching `.history.json`;
- `.runtime/changerail/evidence/oss-04d-propagate-target-session-operation-identity/`;
- `.runtime/changerail/evidence/oss-04d-r1-replace-operation-identity-after-exhausted-review/`.

Recovery status is deliberately narrower than review lineage. The
`oss04d-r1-exhausted-review-payload-20260825` stash reconstructs the exact
OSS-04D-R1 final tree. The older
`oss04-oversized-review-payload-20260825` stash reconstructs checkpoint tree
`48256182c050da7315caa01c71b94f4ecd34725f`, not the final reviewed OSS-04D
tree. The latter is therefore retained exactly as verdict/history,
fingerprint and finding evidence, but its final source tree is not claimed as
durably recoverable. Neither failed source payload is an implementation input;
the successor starts from the published baseline and this reviewed design.

## Root-Cause Traceability

| Final finding class | Root cause | Required invariant | Decision |
| --- | --- | --- | --- |
| Credential/connection aliases alternately leak or over-redact | sensitivity is inferred from any matching token | field classification is closed and anchored, with explicit safe controls | canonical whole-name registry; no generic token membership |
| Private/userinfo documentation URLs leak while valid aliases disappear | route secrecy and public field identity are mixed in regex exceptions | field admission and URL-value admission are separate structured steps | explicit documentation-field registry plus `urlsplit`/`ipaddress` |
| Direct/bound artifact scalars and provenance leak | executor artifact and core provenance share the same mutable object | executor provenance is ignored; every emitted scalar is reconstructed | exact public DTO construction from trusted and untrusted channels |
| Exceptional error/mapping/object paths escape | attribute access and arbitrary callbacks occur outside a total boundary | public serialization is total and never runs arbitrary object callbacks | bounded JSON normalizer and stable typed failure |
| Live session without attachment reaches adapters | lifecycle fallback repairs inconsistent bound state | route admission completes before execution; only both-absent is pre-session | pure admission step with zero-call asymmetric-state block |

## Ownership Model

Public results are built from two channels:

1. Core-trusted provenance: target, session, operation, binding generation and
   evidence policy after binding and route validation.
2. Executor-controlled content: value, error and artifact content admitted by
   total bounded serializers.

Executor-provided provenance is never copied or repaired. The core constructs
new exact `OperationResult`, `OperationError`, `ArtifactReference`,
`TargetIdentity` and `SessionIdentity` DTOs. All trusted identifiers still pass
a bounded grammar and length check before emission.

## Total Public Serialization

The successor uses one dedicated public serializer module with these rules:

- the complete snapshot and normalization operation is inside one exception
  boundary;
- unknown objects become a constant redacted sentinel;
- arbitrary `to_result` properties or callbacks are not executed;
- mapping iteration, key conversion, sequence traversal and scalar access are
  contained;
- recursion depth, collection items, string length and total output size are
  bounded;
- failures return one stable typed `invalid-executor-result` class without
  original exception graphs, attributes or input fragments.

Unbound legacy execution remains unchanged. The closed serializer applies to
project-bound public results where the runtime-target contract is active.

## Field Classification

Names are canonicalized across supported case and separators, then matched as
whole anchored semantic names. Sensitive forms include explicit domain-prefix
patterns such as `db_reference`, `provider_reference` and exact
`reference_name`; they do not include every name containing a `reference`
token.

The public metadata registry is evaluated first. Its controls include:

- `referenceCount`, `referenceLabel`, `documentationReference`;
- `documentationURL`, `documentationUri`, `docsUrl`, `helpURL`,
  `apiDocumentationURL`.

Unregistered keys may remain structurally visible, but their values still pass
bounded scalar and inline-secret normalization. Adding a new sensitive alias or
public metadata field requires both hostile and safe-control tests.

## Documentation URL Admission

URL fields use `urllib.parse.urlsplit` and `ipaddress.ip_address`.

Admission requires HTTP(S), a hostname and no username/password/userinfo,
including encoded forms. A host accepted by strict `ipaddress.ip_address`
must be globally routable. If strict IP parsing fails, a bounded legacy-numeric
grammar is evaluated before DNS: one to four dot-separated components, where
every component is ASCII digits or `0x` plus ASCII hexadecimal digits, are
numeric-host syntax and are rejected without interpreting their value, never
passed to DNS admission. This closed grammar includes decimal, leading-zero
octal-like and hexadecimal legacy forms. Thus compact or alternate spellings such as `127.1`,
`0177.0.0.1` and `0x7f.1` cannot become hostnames. Only non-numeric DNS names
then enter canonical DNS admission, which rejects localhost, single-label,
`.local` and `.internal`. RFC documentation-only hosts are allowed as inert
fixtures.

Compact and canonical loopback, RFC1918, shared/private, link-local,
unspecified, multicast, reserved and private IPv6 hosts are rejected. The
sanitized representation omits query and fragment unless a later reviewed
scope defines their own field admission.

## Artifact And Error Policy

Under `sanitized`, every direct or bound artifact scalar is reconstructed and
validated; no path is emitted. Under `full_local`, path emission additionally
requires an unforgeable core seal and resolved containment inside the approved
evidence root at serialization time.

Errors are reconstructed with bounded code/message, a real boolean
`retryable`, and normalized mapping details. Any access or conversion failure
becomes the same typed public failure without retaining the malformed source.

## Route Admission

Target, session, attachment, binding generation and current host/port/display
are admitted before Local or Windows execution. Only
`session=None` and `attachment=None` together may enter pre-session lifecycle.
Either asymmetric state blocks with zero adapter calls. Serialization does not
grant route authority and settings fallback does not repair bound state.

## Successor Chain

1. Publish this investigation.
2. Publish
   `oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload`, bound to
   this investigation and one implementation successor, at most 500 production
   lines, with no new authority or wire protocol.
3. Deliver `oss-04d-r3-implement-typed-operation-evidence-boundary` from the
   published baseline and this design. Failed-stash production code is not
   restored wholesale; evidence-backed tests may be selectively recovered.
4. Obtain fresh independent GO, publish OSS-04D-R3, then unblock OSS-04E.

## Required Verification Matrix

| Surface | Required hostile coverage | Safe controls |
| --- | --- | --- |
| Provenance | every target/session/operation/binding scalar with secret/path/malformed values | bounded core identifiers and fingerprints |
| Artifact | direct/bound scalars, exceptional subclass, forged seal, escaped/out-of-root path | safe id/media/hash/sensitivity and sealed in-root path |
| Error | every scalar, details, attribute/items/key/value exceptions, recursive data | boolean retryability and bounded details |
| Value | mappings, sequences, paths, cycles, depth/size, unknown objects | JSON scalars and benign nested mappings |
| Field names | case/separator/prefix credential and route aliases | referenceCount/referenceLabel/documentationReference |
| URLs | compact/legacy numeric hosts (`127.1`, `0177.0.0.1`, `0x7f.1`), all non-global IPv4 classes, private/link-local IPv6, encoded/user-only userinfo, internal DNS | canonical global IPv4/IPv6, public HTTP(S) documentation aliases and inert documentation hosts |
| Routing | foreign identity/route and both asymmetric states through Local and Windows | current attachment, true pre-session lifecycle and unbound legacy |
| Verdicts | success/blocked/ambiguous/failure through MCP and scenario | identical trusted request and bounded provenance |

The implementation successor must retain exact RED evidence, focused
MCP/scenario/runtime results, the full non-live suite, compilation, strict
OpenSpec, diff/manifest checks and exact-source Windows offline executor proof.
Live 1C is not required unless later scope changes the runtime surface.

## Design-Only Verification Classification

This investigation changes documentation, OpenSpec and board state only.
Windows-native verification is not applicable: it changes no executable,
adapter, protocol, host-agent, Docker, TestClient or cleanup behavior. No SSH or
live runtime action is authorized or performed by this card.
