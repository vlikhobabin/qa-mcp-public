## Context

The package can query form-element details directly from a running TestClient,
but current accepted mappings deliberately exclude those rows because the
reviewed expanded-readonly comparison lacks request hashes. Earlier readonly
smoke corpus artifacts contain element-detail rows with `101..106` request
frames, while later expanded rows and probe-attached comparisons still expose
the current target rows as `incomplete_hash`.

## Goals / Non-Goals

**Goals:**

- Use the audit output to decide whether existing reviewed captures can be
  extracted or a fresh read-only capture is required.
- Produce compact reviewed request-hash evidence for
  `form-element-details` and `typed-input-field-readonly`, or a precise
  unavailable proof.
- Preserve frame ranges, normalized hashes, dynamic fields, operation tokens
  and response markers needed for later classification.
- Keep fresh runtime output under ignored `runtime/protocol-research/`.

**Non-Goals:**

- Do not promote rows to accepted descriptors in this change.
- Do not broaden to safe UI actions, clicks, text input, command execution or
  writes.
- Do not depend on EDT/meta services for byte-level acceptance.
- Do not terminate unrelated 1C sessions during cleanup.

## Decisions

### Prefer Existing Reviewed Capture Extraction

If the audit identifies a committed compact row with enough source capture and
frame data, delivery should first extract the reviewed request evidence from
that source rather than starting fresh 1C processes. Fresh capture is used only
when existing evidence cannot prove the current row.

### Capture Uses Read-Only Direct Probe Schedules

The first live path is the direct Python-manager probe:

```text
python tools\protocol-research\python_manager_probe.py --query form-element-details --frame-schedule short ...
```

The short schedule sends frames `1..17,101..106` and targets the known
element-detail operation family. The full schedule `1..106` is a fallback when
bootstrap or context frames are needed to make the request slice reviewable.
Expected request frames are manager-to-client `101..106`; expected response
frames are client-to-manager frames adjacent to that schedule.

### Normalize Only Known Dynamic Fields

Reviewed hashes should name dynamic fields rather than hide them:

- `ack_guid_uuid_le`
- `sequence_uint16_le`
- `nonce`
- `operation_token`
- `ascii_guid`
- any preserved semantic token that remains intentionally unnormalized

If frames exist but stable hashes cannot be produced because a field is not
covered by the normalizer, the output remains unresolved as
`incomplete_normalizer_coverage`.

### Runtime Safety Is Read-Only And Owned-Process Only

Runtime scripts may start a TestClient or manager process only when the
operator chooses a live capture path. Cleanup must close only PIDs created by
the current script/run. Raw captures, PID files, platform logs and generated
probe output remain ignored under `runtime/protocol-research/`.

## Risks / Trade-offs

- Live 1C capture may be unavailable or timing-sensitive; mitigate by allowing
  an explicit unavailable proof with command output summary and planned
  evidence path.
- Element-detail and typed-input may share the same direct probe path; mitigate
  by recording operation markers and semantic target labels separately for
  both row ids.
- Normalizing a semantic operation token too aggressively could create a false
  stable hash; mitigate by preserving operation-token evidence unless repeated
  captures prove it safe to replace.

## Migration Plan

This change produces evidence only. Later classification consumes the compact
evidence and decides whether rows are accepted or remain non-accepted with
precise reasons. No deployed runtime or package API migration is required.
