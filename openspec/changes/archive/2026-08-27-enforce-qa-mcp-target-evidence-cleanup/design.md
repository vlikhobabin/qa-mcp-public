## Context

Published OSS-04E-R1 at
`83d88eba4cd608e6141f2ac3def269cb813b502c` admits one target-bound session.
The remaining authority surfaces are
project tool schemas, representative operation routing, artifact retention and
cleanup. Older oversized and exhausted-payload evidence is retained only as
lineage; the final source must receive fresh Linux/Windows proof.

## Goals / Non-Goals

**Goals:**
- Remove model retargeting/retention authority in project tool schemas.
- Route safe read/display with target/session provenance.
- Clean only exact-owned local/Windows resources and certify the full chain.

**Non-Goals:**
- Add new TestClient protocol mappings or capture claims.
- Implement OSS-05 bridge extraction or OSS-06 external-processor flow.
- Provision, copy, restore, register or switch an infobase.

## Decisions

1. Compose bound wrappers with hidden provider-owned arguments; documentation-
   only restrictions were rejected because schemas are the model boundary.
2. Route representative protocol/window reads and screenshots through the
   existing common executor; retain only artifact id/hash/provenance under
   `sanitized`.
3. Require current target/session/generation plus exact lifecycle handle for
   owned cleanup. Non-owned attach only detaches; mismatch never signals.
4. Audit preserved source hashes first to classify lineage. Always run native
   proof against the exact final source/wheel because the published bounded
   sequence intentionally differs from the older oversized payload.
5. Audit the complete project registry recursively against an explicit
   authority taxonomy. Provider-bind endpoint and output roots, omit the
   credential-bearing role matrix from project mode, and preserve the original
   unbound schemas. A representative-tool allowlist is not sufficient proof.

## Risks / Trade-offs

- [Windows relay port differs from native lifecycle port] → Cleanup derives the
  stop port from the authenticated lifecycle handle and tests the regression.
- [Retained screenshot leaks UI data] → Raw image is removed; reviewed evidence
  retains only bounded SHA/provenance.
- [Live run affects unrelated resources] → Pre/post inventories and exact task,
  PID, listener, stage and tunnel ownership are mandatory.

## Migration Plan

Enable bound schemas only for applications with an admitted resolution. Rollback
uses explicit unbound mode. Cleanup must complete before rollback or evidence
finalization.

## Verification Strategy

- RED first for every model-visible override and stale/foreign/recycled cleanup
  handle, including relay/native-port disagreement and zero downstream signals.
- Recursively audit all `63` project tools and use the same exhaustive oracle in
  unit plus Linux/Windows native certification.
- Run focused and exact non-live gates before any live admission.
- Bind Linux and Windows evidence to the exact source/wheel hashes, retain
  secret-safe commands and exit codes, then repeat post-cleanup inventories.
- Run deterministic critical preflight and one fresh independent review before
  publish.

## 1C Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason | Residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Exact Linux source and Windows wheel executing lifecycle, `get_window_list`, `capture_screenshot`, hostile refusal and exact-owned cleanup | Read-only/screenshot scenario against the declared `vanessa_client` contours with bounded pre/post inventory | `qa_testclient_scenario`, `active_window`, sanitized `screenshot` hash and `cleanup_evidence` | `.runtime/changerail/evidence/oss-04f-enforce-target-evidence-cleanup/` | provided | — | Raw UI and credentials are intentionally excluded; sanitized hashes and verdicts are the review boundary. | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| BSL / common server logic | N/A | N/A | N/A | N/A | N/A | No BSL module or server business logic changed. | None beyond the tested Python/runtime boundary. | `/opt/ai-dev-suite-for-1c/bsl-mcp` |
| Metadata / managed form / form command | N/A | N/A | N/A | N/A | N/A | No configuration metadata, managed-form layout, form module or command changed. | Existing TestClient UI is used only as a read/display fixture. | `/opt/ai-dev-suite-for-1c/config-mcp` |
| Role rights / posting / report / migration | N/A | N/A | N/A | N/A | N/A | No roles, document posting, registers, DCS reports or data migration changed. | No business-data mutation is authorized by this card. | `/opt/ai-dev-suite-for-1c/qa-mcp` |

## Open Questions

- None. Capture sources, frame ranges, dynamic fields and replay templates are
  unchanged; existing read mappings are reused.
