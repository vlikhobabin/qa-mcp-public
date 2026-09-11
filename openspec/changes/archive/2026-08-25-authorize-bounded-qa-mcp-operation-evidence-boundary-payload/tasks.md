## 1. Materialize The Exact Authorization Chain

- [x] 1.1 Normalize the A1 review and authorization fields to the canonical ChangeRail machine-readable form with exactly six closed authorization fields.
- [x] 1.2 Add reciprocal R2 `Blocks`, A1 `Depends On`, and R3 `Depends On` metadata while keeping R3's published authorization unset until A1 finalization.

## 2. Prove Fail-Closed Consumption

- [x] 2.1 Retain a secret-free authorization evidence index with exact card ids, canonical paths, ceiling, authority flag, source hashes and verification classification.
- [x] 2.2 Verify an isolated finalized candidate accepts the exact R3 chain and a bounded mismatched successor control fails closed.

## 3. Verify And Finalize

- [x] 3.1 Record Windows-native, live 1C and test-first runtime verification as not applicable because the payload changes metadata only and performs no external action.
- [x] 3.2 Run strict change/capability/all OpenSpec validation, JSON/relation checks, manifest scope and diff checks; sync the authorization capability, archive the change and prepare fresh independent review.
