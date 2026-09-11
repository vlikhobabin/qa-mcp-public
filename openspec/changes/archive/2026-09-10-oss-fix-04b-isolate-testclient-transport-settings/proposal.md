## Why

Native TestClient transport still resolves relay settings from process environment,
even inside a server factory built with explicit Settings. A hermetic real-factory
probe on 2026-09-10 reproduced this for two different relay configurations and
explicitly absent, partial and malformed configurations: all selected the third,
process-configured relay. FIX-04A's display changes do not fix this separate seam.

## What Changes

- Bind a minimal configuration scope to existing application activation and reset
  it on nested, concurrent and exceptional exits.
- Make shared relay resolution consume the active application's immutable relay
  fields, including intentional absence, without process fallback.
- Preserve exact endpoint-bound authentication, direct TCP behavior, refusal
  cleanup and non-consuming relay-listener readiness.
- Reject malformed/partial configuration before socket creation and keep public
  failures bounded and free of configured tokens or untrusted relay reply prose.
- Retain explicit low-level environment adapters outside composition and prove
  actual session/native-helper/lifecycle consumers with fake protocol boundaries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-runtime-configuration`: application-owned relay resolution and its
  isolation, validation, readiness and explicit legacy compatibility contract.

## Impact

Production owners are `config.py`, `core/application.py` and
`protocol/transport.py`. Existing session, replay, foreground, native write,
mutation/XTEST and lifecycle callers share that transport and require focused
consumer proof. Consumer documentation describes scope and legacy behavior.
No protocol-frame, relay-server, display/HTTP, artifact-root, target-admission or
ChangeRail implementation change is planned. No dependency is added.

One native change replaces the two unaccepted draft checkpoint slugs; no existing
active or archived artifacts were found for them. FIX-04A is now completed and
published with retained independent GO and history; this transport defect still
reproduces on clean `bd64e5a`. Its new delivery uses the ordinary native review
allowance. This is offline Python scope; final Linux/Windows qualification remains
with FIX-11/FIX-12.
