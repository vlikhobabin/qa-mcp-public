## Why

The public factory stores explicit Settings, but composed display selection,
host-agent availability checks and lifecycle construction still read process
environment. An application configured for remote execution can select local
X11, or two applications can use the same unintended host-agent address.
This remains relevant to both standalone qa-mcp and downstream shared-core use.

## What Changes

- Construct display and host-agent clients from the active application's
  explicit Settings, including mode, address, credentials, compatibility pins,
  timeout, window selector and native client port.
- Use that same source in availability guards and relevant error formatting;
  an intentionally empty application value cannot inherit process environment.
- Bind the current attachment per operation without sharing mutable target or
  handshake state across applications or sessions.
- Keep explicit legacy environment constructors outside composition and preserve
  current bound-attach rejection, owned launch and cleanup restrictions.
- Add focused offline regressions through real factories with fake HTTP/X11,
  plus legacy controls. This changes Python routing, not Windows wire/API behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-runtime-configuration`: application-owned display/host-agent settings
  take precedence over process environment throughout composed calls.

## Impact

Primary owners: `src/qa_mcp/protocol/display_backend.py` and
`src/qa_mcp/mcp_server.py`; `src/qa_mcp/core/application.py` only if an explicit
construction seam is needed. Existing immutable Settings fields suffice.
Tests: display backend, shared-core factory, target-bound lifecycle/cleanup;
focused new composition cases may live in a separate test file.
Consumer documentation: `docs/shared-core-extension.md`.

One native change replaces the draft's two uncreated change slugs; ordered
tasks retain the two implementation checkpoints. No ChangeRail work, protocol
relay changes (FIX-04B), storage ownership (FIX-04C), new attach observer,
Windows deployment or stable qualification is included. FIX-02 remains stopped
and is not adopted as a completed dependency. FIX-11/12 retain final-source
native qualification before release.
