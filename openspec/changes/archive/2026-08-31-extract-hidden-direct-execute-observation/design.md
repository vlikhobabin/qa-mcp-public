## Context

Published S1-S3 provide exact hidden desktop/process creation, worker/job/TPort
ownership and read-only top-level window isolation. The dirty combined
investigation candidate also contains marker/UIA observation mixed with later
prompt actions and public integration. S4 must extract only the passive slice
into separate files, remain below `300` production lines and leave every
published predecessor byte-identical.

No TestClient protocol frame or capture is changed. The proof source is direct
Win32/UIA observation of exact platform `8.3.27.2214` on the declared Windows
`vanessa_client`; frame ranges, protocol dynamic fields and replay strategy are
therefore not applicable. Dynamic HWND/PID/desktop values remain in memory and
curated evidence retains only hashes, counts, booleans and typed outcomes.

## Goals / Non-Goals

**Goals:**

- bind one current S3-admitted main HWND to exact PID/job/desktop/class/owner;
- compare exactly one UIA name only through a precomputed lowercase SHA-256;
- inventory a bounded set of structural UIA hashes/pattern flags;
- reject missing, duplicate, foreign, changed, malformed, oversized or
  ambiguous observations with action count zero;
- retain sanitized evidence and exact-owned Windows cleanup.

**Non-Goals:**

- prompt admission, focus or confirmation;
- UIA Invoke/Value/Focus, addressed messages or any global input;
- chooser, screenshot/capture, raw title/text/credential retention;
- Go-to-Python receipt integration, public route/profile or stable admission.

## Decisions

### Re-admit the exact S3 window before interpreting UIA

The portable policy receives the original S3 main identity and a fresh hidden
inventory. It calls the published exact selector, then also requires the same
HWND/PID/class/owner/desktop tuple. A replacement HWND or second matching
window is a typed refusal even if the marker is present. This avoids treating
UIA content as ownership proof.

### Keep raw UI values inside the Windows observer only long enough to hash

The Windows adapter obtains a UIA root from the exact HWND, walks at most `512`
elements and emits only SHA-256 values for control type, class, automation id,
name, runtime/path identity and a fixed supported-pattern set. Raw values never
cross the adapter boundary or enter JSON/evidence. The caller supplies only an
already computed lowercase marker SHA-256; a raw marker is not an API input.

An embedded read-only Windows UIA query is used because the current host module
has no UIA library dependency and the proven hidden-desktop candidate already
uses the platform UIAutomation assemblies. It performs property reads and
`TryGetCurrentPattern` capability checks only; it never retrieves a pattern
object for invocation, sets focus/value or sends a window message. A native Go
COM implementation was rejected for S4 because it would materially expand the
bounded security-sensitive surface.

### Make ambiguity and stability portable

Every row must be exact-PID, fully hashed and uniquely identified. Duplicate
row identity, foreign PID, malformed hash or overflow fails before receipt
admission. Two passive snapshots of the same exact main identity must have the
same marker cardinality and topology hash; changed topology is a typed refusal.
The receipt contains schema/status, exact identity hash, expected marker hash,
marker/control counts, topology hash, `action_count: 0` and explicit no-raw-UI
booleans.

### Prove behavior from published HEAD plus exact S4 paths

RED tests first define missing/duplicate marker, foreign identity/job/desktop,
changed HWND, ambiguous topology, leakage and action-count failures. Clean
composition starts from published `46287c...` and overlays only S4 files and
artifacts. The native candidate launches direct `/Execute <target.epf>` on the
unique hidden desktop, passively obtains two stable observations and performs
no prompt action. If a real prompt blocks the marker, the native result is a
typed non-pass rather than confirmation.

## Risks / Trade-offs

- [Platform UIA topology changes] -> fail closed and require new exact native
  evidence; do not infer identity from text or loosen cardinality.
- [UIA worker serializes raw values] -> schema tests reject any non-hash string
  and retained-output scans reject marker text, credential-like fields and raw
  UI values.
- [HWND is reused between snapshots] -> fresh S3 inventory plus full exact
  tuple equality precedes each observation.
- [A prompt is present] -> S4 inventories/returns a typed passive outcome only;
  S5 alone may admit and address it.
- [Cleanup could touch unrelated state] -> bind task/stage/PIDs/job/desktop/port
  to the current run before removal; preserve listener `18081`, Docker and
  unrelated processes, and never reboot.

## Migration Plan

No runtime migration exists because S4 remains dormant. Add RED tests, extract
the two passive sources, run clean/native verification, sync the new capability
and archive. Publish only after fresh independent ordinary/high `GO`. Rollback
removes only S4 source/tests/spec lineage; S1-S3 remain unchanged.

## Open Questions

- None for S4. Prompt topology/action, typed bridge receipt and public
  integration remain deliberately deferred to S5, S6 and S7.
