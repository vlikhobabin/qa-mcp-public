## 1. Public Contract

- [x] 1.1 Replay only immutable fingerprint/binding/observation/profile/evidence-policy values from the preserved OSS-04 payload and keep `TargetIdentity` canonical.
- [x] 1.2 Add the closed runtime-target profile JSON schema, public exports and package/archive asset declarations.
- [x] 1.3 Keep resolver, application, lifecycle, executor and runtime behavior out of this payload and confirm added production LOC is at most `300`.

## 2. Contract Verification

- [x] 2.1 Add tests for immutability, fingerprint normalization, evidence-policy values and closed-schema required/unknown fields.
- [x] 2.2 Add wheel/sdist/open-image inventory tests proving the schema asset is present and no private artifact is introduced.
- [x] 2.3 Run a Windows-native read-only import/schema parse smoke; no TestClient or lab mutation is authorized for this change.

## 3. Delivery Gate

- [x] 3.1 Run focused core/package tests, Python compilation, the exact non-live CI suite with coverage, `git diff --check` and strict OpenSpec validation.
- [x] 3.2 Sync the capability spec and prepare the completed change for archive;
  deterministic preflight and fresh independent review remain card-level gates.
- [x] 3.3 Include the apply-ready OSS-04B–F board/OpenSpec planning artifacts in the scoped publish and leave their implementation tasks unchecked.
