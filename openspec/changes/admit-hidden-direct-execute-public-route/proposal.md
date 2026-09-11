## Why

The published S1-S6 sequence proves each dormant hidden direct-execute and
exact-cleanup boundary independently, but the standalone bridge and project-
bound MCP route still do not compose or advertise them. S7 is the single
published and LOC-bounded authorization point that may turn those foundations
into a stable `open_external_processor` capability.

## What Changes

- Add a backward-compatible standalone bridge capability for hidden native
  `/Execute` through the existing authenticated TestClient launch/stop surface.
- Compose published S1-S6 into one closed typed receipt without changing their
  certified source or admitting chooser/global-input fallbacks.
- Route project-bound Windows `open_external_processor` through capability
  negotiation, exact receipt validation and the single-use cleanup lease.
- **BREAKING (pre-stable tool schema):** replace the legacy model-visible
  display/coordinate/timing controls with only the logical EPF/ERF path and
  optional expected caption. The tool name and bounded result taxonomy remain
  stable; callers cannot retain physical targeting authority.
- Admit the tool in the stable standalone profile only after exact final-source
  Windows proof and critical review; preserve the existing Linux route and
  bounded public result taxonomy.
- Retain privacy-safe exact-source prompt-off, fresh prompt-on, recovery,
  hostile refusal and cleanup evidence. No protocol capture, Vanessa MCP,
  EDT/meta snapshot or runtime-lab configuration change is required; final
  delivery does require the authorized live Windows 1C contour.

## Capabilities

### New Capabilities
- `qa-mcp-hidden-direct-execute-public-route`: Conditional public MCP/profile
  admission, exact typed-result validation, bounded stages and single-use
  cleanup for the project-bound Windows external-processor route.

### Modified Capabilities
- `qa-mcp-standalone-host-bridge`: Add the versioned bounded direct-execute
  capability, request admission, closed receipt and exact lifecycle-stop
  behavior to the existing authenticated bridge contract.

## Impact

- Windows bridge capability declaration and existing TestClient launch/stop
  integration paths.
- Python external-processor operation core, remote bridge client and MCP
  profile/schema registration.
- Go/Python hostile, contract, profile and exact-cleanup tests plus retained
  Windows-native certification evidence.
- OpenSpec roadmap/card/spec workflow. Runtime Proxy/RPW, Relay, Team,
  live-mcp and private AI for 1C downstream repositories remain unchanged.
