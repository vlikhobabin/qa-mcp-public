## Context

`mcp_server.main()` currently calls `_enforce_startup_license_gate()` before it
starts the MCP transport. That helper reads three settings and can execute the
`ai1c-license` broker, then terminate the process on a denied or malformed
decision. The gate is off by default, but legacy environment values can still
activate it, which is incompatible with the operator's free-distribution
decision.

This change is confined to Python startup/config behavior. It introduces no
protocol claim: capture sources, frame ranges, dynamic fields, replay strategy,
live 1C cleanup, Vanessa MCP, and EDT/meta evidence are all not applicable.

## Goals / Non-Goals

**Goals:**

- Make product-license state incapable of affecting qa-mcp startup.
- Ensure legacy `QA_MCP_LICENSE_*` variables cannot launch any process.
- Remove dead broker/gate code and its settings surface.
- Retain a focused regression test that fails if broker execution is wired
  back into startup.

**Non-Goals:**

- Change or bypass the legal 1C platform license requirement.
- Change bundled-data encryption or runtime key delivery; that belongs to the
  second ordered change.
- Change the root suite license broker or other providers.

## Decisions

1. **Delete the gate rather than force its setting to false.** Removing the
   startup call, imports, settings, and helper module makes zero broker calls a
   structural invariant. Keeping a dormant decision engine would leave a
   future accidental re-enable path and unnecessary shipped attack surface.
2. **Treat legacy environment variables as unknown/inert.** `Settings.from_env`
   reads only declared qa-mcp settings, so removing these fields naturally
   ignores old values without logging their potentially sensitive contents.
3. **Test the public startup boundary.** A startup regression patches the MCP
   run boundary and makes subprocess execution fail the test, then calls
   `main()` with all legacy variables set. This observes the behavior source
   that previously invoked the gate and would fail if the regression returned.
4. **Remove the old decision-matrix tests.** They specify retired behavior and
   would preserve a false product contract if left in place.

## Risks / Trade-offs

- **[Risk] Existing deployments may still set legacy variables.** -> They are
  ignored without value disclosure or startup failure, so no migration step is
  required before update.
- **[Risk] Removing `qa_mcp.license_gate` breaks private imports.** -> The module
  was an internal startup implementation, not an MCP or documented Python API;
  release docs and tests are updated in the second change.
- **[Risk] A broker call survives elsewhere.** -> Repository scans and focused
  tests cover `ai1c-license`, the legacy env names, and subprocess invocation
  from startup-related surfaces.

## Migration Plan

1. Add the startup regression test and record its pre-fix failure.
2. Remove the startup gate call/imports, configuration fields, and helper
   module.
3. Run focused config/startup tests and scan the Python runtime for retired
   product-license identifiers.
4. Delivery/image cleanup follows in the second ordered change.

Rollback is a normal source revert; it would intentionally restore a retired
product-license path and therefore requires a new operator decision.

## Open Questions

- None. Free qa-mcp distribution and removal of the product gate are explicit
  operator decisions on the source card.
