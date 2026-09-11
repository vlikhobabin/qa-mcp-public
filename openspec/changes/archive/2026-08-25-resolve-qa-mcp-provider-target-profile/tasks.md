## 1. Profile Resolution

- [x] 1.1 Replay the closed profile loader and frozen handoff activation rules from the preserved payload.
- [x] 1.2 Reconcile target/kind/fingerprint, principal, receipt, binding reference and positive generation into one immutable resolution.
- [x] 1.3 Enforce regular local profile/env paths, evidence-root allowlisting and approved `sanitized`/`full_local` policy without serializing secrets.
- [x] 1.4 Confirm added production LOC is at most `300` and no provider package dependency is added.

## 2. Negative And Cross-Platform Verification

- [x] 2.1 Cover file/client-server, absent/partial handoff, mismatch/stale generation, unsafe paths and both evidence policies.
- [x] 2.2 Prove failures create no process, listener, filesystem target or alternate infobase.
- [x] 2.3 Run a Windows-native read-only resolver smoke against synthetic ignored profiles and retain only sanitized outcomes.

## 3. Delivery Gate

- [x] 3.1 Run focused adapter tests, compilation, exact non-live CI/coverage, diff check and strict OpenSpec validation.
- [x] 3.2 Sync the capability spec and prepare the completed change for archive; preflight and review remain card gates.
