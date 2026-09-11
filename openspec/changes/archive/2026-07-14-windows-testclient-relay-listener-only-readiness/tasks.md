## 1. Listener-only lifecycle probe

- [x] 1.1 Add a RED lifecycle regression proving the current relay liveness
      path invokes the authenticated connector.
- [x] 1.2 Route the exact configured relay endpoint through listener-only
      reachability while preserving direct endpoint behavior.

## 2. Public tool regression

- [x] 2.1 Prove status, info and state tools inherit the listener-only path and
      never invoke the authenticated connector for liveness.
- [x] 2.2 Keep real protocol connector tests green for authenticated sessions.

## 3. Verification and lifecycle

- [x] 3.1 Run focused/full Python tests, strict OpenSpec and `git diff --check`.
- [x] 3.2 Sync the endpoint contract and archive the change.
