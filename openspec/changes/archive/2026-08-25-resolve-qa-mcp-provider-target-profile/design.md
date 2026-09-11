## Context

OSS-04A defines provider-neutral values. This payload consumes the frozen
environment handoff and one ignored profile but remains below application and
lifecycle layers.

## Goals / Non-Goals

**Goals:**
- Parse a closed local profile and reconcile every frozen identity field.
- Enforce evidence policy/root and emit typed secret-safe failures.

**Non-Goals:**
- Import private provider packages or interpret their project descriptor.
- Compose a server, doctor or TestClient lifecycle.
- Add protocol capture/replay behavior.

## Decisions

1. Treat any partial handoff as an error and no handoff as unbound mode.
   Guessing defaults was rejected because it can select another infobase.
2. Require a regular profile and physical env file under explicit local policy;
   reject symlink/path escape rather than canonicalizing silently.
3. Reconcile target, principal, receipt, binding reference and positive
   generation before returning a resolution. Physical connection values remain
   opaque and are never serialized.
4. Permit `full_local` only with explicit non-production approval and an
   allowlisted evidence root; model input never controls this policy.

## Risks / Trade-offs

- [Strict profiles reject legacy configuration] → Unbound standalone remains
  supported; project mode fails with a typed field/code.
- [Error detail leaks secrets] → Public exceptions expose only bounded field and
  code values.

## Migration Plan

Add the resolver after OSS-04A. Roll back to an unbound application; never
rewrite a bound target. No runtime cleanup is applicable.

## Open Questions

- None. Frozen wire values are consumed unchanged and no protocol evidence is
  introduced.
