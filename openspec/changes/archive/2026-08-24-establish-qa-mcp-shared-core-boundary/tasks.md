## 1. Freeze current behavior and contracts

- [x] 1.1 Capture deterministic tool name/schema snapshots for the current default surface and classify standalone versus research tools.
- [x] 1.2 Add public target/session, operation verdict/error, artifact and executor protocol models with fake implementations.
- [x] 1.3 Add import-boundary tests that reject dependencies on Runtime Relay, RPW, live-mcp, Team or private AI for 1C packages.

## 2. Add explicit application composition

- [x] 2.1 Implement an application/runtime context that owns settings, attachment/session state and the selected executor.
- [x] 2.2 Implement `create_mcp_server` and make the existing CLI entrypoint delegate to the standalone composition.
- [x] 2.3 Replace unconditional tool decoration with deterministic standalone and research profile registration.
- [x] 2.4 Prove two application instances keep attachment and lifecycle state isolated.

## 3. Share operation semantics

- [x] 3.1 Extract an initial representative read, write, lifecycle and display operation behind the public executor/result contracts.
- [x] 3.2 Route both MCP wrappers and scenario actions through those shared operations and compare verdict classes.
- [x] 3.3 Adapt the current local Linux and Windows-host paths without changing protocol templates, replay algorithms or cleanup ownership.

## 4. Verify and document the extension boundary

- [x] 4.1 Run focused factory/profile/contract tests, the full non-live Python suite and strict tool-schema comparison.
- [x] 4.2 Run Linux local lifecycle/read regression and retain owned cleanup evidence, or record the preflight runtime gap before execution.
- [x] 4.3 Run Windows-native standalone executor lifecycle/read/display smoke against the authorized target and retain exact cleanup evidence.
- [x] 4.4 Document public extension rules, compatibility policy and upstream-first downstream consumption without private implementation details.
- [x] 4.5 Record the runtime-target binding card as the next public-core consumer of the generic target/session seam and prove no project-descriptor dependency entered this change.
