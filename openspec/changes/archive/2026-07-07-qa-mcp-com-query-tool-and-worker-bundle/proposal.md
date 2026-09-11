## Why

Local file infobases without OData cannot answer simple read-only data questions
through qa-mcp today, even though the Windows host can execute the same 1C query
through `V83.COMConnector`. The host-agent already has the `/com/execute`
transport, but qa-mcp does not expose a read-only MCP tool for it, standard
release handoff can omit the required `ai-com-worker.exe`, and broken
COMConnector TypeLib registration is hard to diagnose.

## What Changes

- Add a qa-mcp MCP read-only COM query tool and count assertion helper that call
  the Windows host-agent instead of OData.
- Add obvious write-operation rejection before a caller can send a query to the
  COM worker unless a future explicit mutation mode is implemented.
- Make standard self-hosted release wiring discover and bundle a supplied
  `ai-com-worker.exe`, while preserving the existing non-COM release path.
- Add COM worker health impact fields so a missing worker is reported as a
  feature-impact warning for COM flows.
- Add a host-side COMConnector doctor that checks 64-bit registration evidence,
  TypeLib presence, COM creation, file infobase connection, and an optional
  read-query smoke, with exact elevated `System32\regsvr32.exe` remediation.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: adds host-side read-only COM query and count
  tool behavior to the MCP contract.
- `qa-mcp-self-hosted-release`: tightens the standard COM worker bundling and
  health-impact release handoff contract.
- `qa-mcp-windows-host-agent-security`: adds the authenticated COMConnector
  doctor and COM worker health-impact diagnostics to the host-agent boundary.

## Impact

- Python manager/MCP provider setup: new MCP tool functions, host-agent client
  helpers, structured COM results, and offline tests.
- Windows host-agent code: new authenticated COMConnector doctor endpoint and
  clearer health metadata; existing `/com/execute` remains the query transport.
- Release tooling and docs: standard self-hosted publish/install path can bundle
  the ready worker executable without manual copying.
- Runtime evidence: Linux tests can verify contracts with fake host-agent
  responses; real `V83.COMConnector` registration and the BIT.FINANCE query smoke
  remain Windows-host evidence because COM is unavailable in the Linux contour.
