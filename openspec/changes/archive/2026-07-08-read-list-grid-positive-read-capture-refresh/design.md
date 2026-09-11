## Context

The previous fail-loud card proved that `read_list_grid` no longer returns a
normal-looking `row_count: 0` when the list table cannot be resolved. The
remaining [redacted third-party configuration] blocker is earlier in the protocol path: the selected
capture's session-manager bootstrap reaches manager frame 3, then the live
client response does not contain the expected ACK/GUID shape and the socket is
reset. That failure is currently surfaced as a generic descriptor/list-table
failure, even though the actionable diagnosis is "selected capture does not
match this live manager handshake."

The user has stated that the real Windows .205 / [redacted third-party configuration] host is unavailable
in this session. This delivery therefore implements only the offline-testable
scope and records the runtime positive-read proof as a provider gap.

## Goals / Non-Goals

**Goals:**

- Stamp capture metadata with platform build and configuration identity.
- Select a capture by platform/configuration metadata before falling back to the
  existing version-family bundled data.
- Provide a repeatable refresh-capture procedure/tool that records metadata and
  avoids committing raw captures.
- Add a manager-handshake preflight with a structured `manager-handshake-moved`
  diagnostic when frame 3 live ACK/GUID extraction fails for the selected
  capture.
- Add offline tests for metadata matching and handshake drift classification.
- Retain a provider-gap artifact for the unavailable [redacted third-party configuration] positive read.

**Non-Goals:**

- Do not fabricate [redacted third-party configuration] positive-read evidence.
- Do not run live Windows UI automation or data-changing 1C actions from this
  Linux workspace.
- Do not change business data, role rights, metadata objects, reports, posting,
  COM writes, OData writes, or raw capture storage policy.
- Do not claim that demo10413 or [redacted third-party configuration] protocol compatibility is proven by
  offline tests alone.

## Decisions

### Capture metadata is a small sidecar contract

Each curated capture or template set can carry a small JSON sidecar with schema,
capture id, platform build, configuration name/vendor/version when known, source
paths, template paths, and notes. This sidecar is safe to commit because it
contains labels and hashes, not raw TCP payloads or customer data.

### Config-matched selection is explicit and fallback is observable

The selector first matches requested platform build/configuration tags against
metadata sidecars. If no exact config match exists, it returns a structured
selection result explaining the fallback to the existing active bundled capture.
Callers can include that selection result in diagnostics before a live replay is
trusted.

### Manager-handshake drift is a preflight, not a hidden exception

The preflight sends only the bounded bootstrap frames needed to observe the
client ACK/GUID after manager frame 3. If the response cannot be decoded or the
ACK/GUID marker is absent, it returns `ok:false`,
`error:"manager-handshake-moved"`, the selected capture metadata, frame index,
and an action hint to refresh the capture for the target platform/configuration.

### Refresh tooling documents operator work without retaining raw capture

The procedure/tool records a sanitized capture metadata sidecar and a checklist
for re-recording the session bootstrap plus list-open/read templates. Raw pcap,
traffic logs and platform output remain under ignored runtime directories.

## Risks / Trade-offs

- Offline tests can prove matching and diagnostic classification, not live
  [redacted third-party configuration] data visibility. Mitigation: retain an explicit provider-gap
  artifact and leave the positive-read acceptance unclaimed.
- Configuration names can vary across deployments. Mitigation: normalize simple
  labels but retain raw labels in metadata for auditability.
- A config mismatch may still use a compatible capture. Mitigation: fallback is
  observable; the live preflight is the authoritative signal before the read.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Real Windows .205 [redacted third-party configuration] `read_list_grid` positive read for `Справочник.Валюты` | Operator-owned run with config-matched capture, visible rows returned, and retained sanitized MCP transcript | `qa_testclient_bundle` or provider-gap report | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows .205 / [redacted third-party configuration] host is unavailable; positive-read proof remains unproven. |
| Native protocol claim | Capture metadata sidecars and config-matched capture selection | Offline unit tests for platform/config tag parsing, exact match, fallback selection, and safe serialization | Focused pytest output and retained summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/capture-metadata-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline metadata tests do not prove live replay compatibility. |
| QA/TestClient UI automation | Manager-handshake drift preflight before descriptor/list read | Offline unit tests using fake socket/session responses for ACK success and frame-3 ACK/GUID absence | Focused pytest output and retained summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/handshake-drift-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live preflight still requires an available TestClient endpoint. |
| Protocol research tooling | Refresh-capture procedure/tooling | Runbook review plus CLI/help or dry-run output proving metadata path and raw-capture boundary | Documentation/tooling check summary | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/refresh-procedure-check.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The procedure is not a substitute for the unavailable Windows capture run. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No mutation is part of this protocol-lab change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change is read-only protocol metadata/preflight/tooling. | None beyond unproven live positive-read acceptance. |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence | sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | qa_testclient_bundle | Blocks proof that `read_list_grid` on [redacted third-party configuration] / 8.3.27.2130 / Бухгалтерия 3.0 returns visible `Справочник.Валюты` rows using a config-matched capture. | Operator can run the documented refresh procedure and positive-read smoke later on the real Windows .205 host, then replace this provider-gap artifact with a sanitized proof bundle. | `openspec/board/1.backlog/read-list-grid-positive-read-capture-refresh.md` | `.artifacts/openspec/read-list-grid-positive-read-capture-refresh/20260708T072524Z/third-party-config-positive-read-provider-gap.md` | no credentials, screenshots or live data copied |

## Open Questions

- Which exact Бухгалтерия 3.0 configuration version string should be stamped by
  the Windows refresh run? The offline sidecar supports it, but the real host
  must provide the authoritative label.
