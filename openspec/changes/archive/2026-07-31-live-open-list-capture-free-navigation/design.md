## Context

`open_list` currently derives a complete replay from the public `capture`
argument. Its default names an ignored development capture, while an empty
string can be interpreted as the repository/work directory. Both fail in the
released thin runtime before a list navigation can be sent.

The engine already has a released, live-proven navigation path used by form
introspection and scenario OPEN steps. It bootstraps a manager connection from
the version-selected bundled bootstrap corpus, renders a live header from the
bundled value-read templates, enumerates the live desktop `MainFrame`, and
splices the target `e1cib/list/...` link into the two-frame navigation command.
The decoded navigation body originates from the genuine open-list command at
manager frame 14; dynamic ACK GUID, sequence, nonce, desktop `MainFrame` GUID,
and variable-length link data are rebound for the live session. This change
reuses that established claim and does not introduce a new frame family or raw
capture.

The affected surface is a read-only/safe UI navigation command. It does not
write business data, modify an infobase, or own the attached TestClient
process. The per-call manager socket must close on success and failure; any
live proof that launches a TestClient must use the provider-owned lifecycle and
stop only the exact launched process.

## Goals / Non-Goals

**Goals:**

- Make omitted or blank `capture` use the released, versioned navigation
  template path.
- Keep explicit capture replay as a compatibility path, including a neutral
  bundled capture selector.
- Load and validate every required bootstrap/template asset before opening the
  TestClient socket, and return a typed capability diagnostic on asset failure.
- Preserve attached-endpoint routing and bounded, sanitized evidence.

**Non-Goals:**

- Decode a new protocol frame family or add/re-record a capture.
- Change list search, row selection, write actions, persisted data, platform
  configuration, host-agent lifecycle semantics, or display automation.
- Treat arbitrary external captures as a supported default.

## Decisions

### Default to template-backed live navigation

Change the public `capture` default to `None`. `None` and blank strings select
the template-backed live navigation path; a non-blank value continues through
the legacy explicit-capture derivation. This preserves caller compatibility
without exposing a historical development name in the MCP schema.

The default path resolves the version-selected bundled bootstrap and value-read
template assets, renders the live session, and invokes the existing
`_open_form_by_link`/`splice_navigate` implementation. The result identifies
the requested nav-link and whether a form resolved, without returning local
asset paths.

Alternative considered: rename the old default to `listform-read` and replay
the whole captured list-read flow. That would fix packaging but would retain an
unnecessary complete replay dependency and would not use the existing
capture-free navigation mechanism.

### Make the template selector explicit but optional

Add an optional `navigation_templates` argument. Omission selects the active
version's bundled `value_read_templates.json`; an explicit path supports
controlled testing and compatible packaged overrides. The selector is loaded
before any `TestClientSession` is opened. The public endpoint wrapper also
completes this preflight before it probes a remembered attachment for liveness,
so even the routing layer cannot open a TestClient socket first.

Alternative considered: overload `capture` with template paths. That keeps a
smaller signature but conflates JSON navigation templates with JSONL capture
directories and recreates the empty-path ambiguity.

### Fail closed at the asset boundary

The default path performs bootstrap resolution, capture/template parsing, and
synthesized-bootstrap preparation as one preflight stage. Missing, unreadable,
or structurally incomplete assets return `ok: false`, error
`open-list-navigation-unavailable`, capability
`template-backed-open-list`, and `protocol_write_attempted: false`. The result
records only an asset class and reason code, not an absolute path or raw
payload.

Runtime connection/handshake failures after preflight continue through the
existing endpoint wrapper contract and are not mislabeled as asset failures.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | `open_list` safe navigation command and attached endpoint | Omitted-capture, blank-capture, explicit bundled-template, and missing-template cases with an assertion that no session/socket opens on preflight failure | Focused offline endpoint tests plus a live `e1cib/list` open result | `.runtime/changerail/evidence/live-open-list-capture-free-navigation/` | required |  | Live target availability can block runtime proof; if so, retain a provider-gap with resume condition | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Delivery or runtime apply | Released Python MCP runtime using bundled assets | Run focused and full Python suites, strict OpenSpec validation, and a bounded remote/live attach-open-stop proof | Command outcomes, sanitized live result fields, exact-process cleanup summary | `.runtime/changerail/evidence/live-open-list-capture-free-navigation/verification-summary.json` | required |  | Offline tests cannot alone prove the Windows remote-client contour | `/opt/ai-dev-suite-for-1c/qa-mcp` |

BSL, metadata-object, role-rights, posting/register, report/DCS, and migration
surfaces are not applicable because no 1C source, infobase schema, role,
business command, persisted data, or report is changed. Residual risk for those
surfaces is none.

## Risks / Trade-offs

- [Risk] The live navigation helper resolves a form, so it sends bounded
  window-list and resolve queries in addition to the two navigation frames. ->
  Mitigation: reuse the already tested helper and assert the result shape rather
  than adding a second partially decoded route.
- [Risk] A malformed explicit template could otherwise fail after connection.
  -> Mitigation: load and render the required no-form splice frame during
  preflight, before constructing the live session.
- [Risk] Changing `capture` from a string default to optional affects schema
  consumers that introspect defaults. -> Mitigation: preserve non-blank
  explicit capture behavior and cover the registered MCP schema/endpoint tests.
- [Risk] Live remote evidence may depend on host availability. -> Mitigation:
  retain a typed runtime gap and cleanup audit if the authorized contour is not
  reachable; do not substitute unbounded logs or another user's session.
