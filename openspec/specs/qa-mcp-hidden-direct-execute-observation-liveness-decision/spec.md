# qa-mcp-hidden-direct-execute-observation-liveness-decision Specification

## Purpose

Define the offline evidence boundary, exclusive liveness states and sole
bounded correction authorization required after repeated hidden direct-execute
inventory refusal.

## Requirements

### Requirement: Offline evidence preserves unresolved liveness
The decision MUST use only retained privacy-safe evidence and offline tracked
source, MUST classify the retained first-inventory refusal as an inventory
error, and MUST leave child and listener liveness unknown when no
contemporaneous liveness predicates were retained.

#### Scenario: Historical listener PID is present
- **WHEN** a retained response contains a non-zero listener PID but no current
  synchronize, job and exact-TPort checks at the failed inventory call
- **THEN** the decision records listener liveness as unknown
- **AND** historical readiness cannot satisfy current listener liveness.

#### Scenario: Retained enumeration failed
- **WHEN** retained evidence reports `EnumDesktopWindows` failure or normalized
  `ERROR_INVALID_DATA`
- **THEN** the decision records `inventory_error` with unknown window presence
- **AND** it does not relabel that state as an empty inventory or absent main.

### Requirement: Observation liveness states are exclusive and fail closed
A bounded observation sample SHALL determine exact child liveness, exact
listener liveness, inventory outcome and main-window presence in order, and
MUST stop on dead, unknown, errored or changing state before passive UIA.

#### Scenario: Child or listener is not currently live
- **WHEN** the exact process handle is signaled or absent, job membership is
  lost, exact listener TPort ownership is lost, or a liveness query is unknown
- **THEN** the sample returns the corresponding typed child/listener refusal
- **AND** does not enumerate or admit a window.

#### Scenario: Enumeration succeeds with zero windows
- **WHEN** the single bounded desktop enumeration call completes successfully
  with zero retained top-level rows
- **THEN** the sample records `inventory_empty` and `main_absent`
- **AND** the empty result remains fail closed and distinct from an API error.

#### Scenario: Enumeration succeeds with windows
- **WHEN** the single call succeeds with bounded non-empty rows
- **THEN** the sample records `main_present` only for one exact job-owned
  desktop/class/root-owner identity
- **AND** any missing, duplicate, foreign or changed identity records
  `main_absent` or `lifecycle_changed` and cannot reach passive UIA.

### Requirement: One correction is the continuation ceiling
The decision SHALL authorize exactly one later S4-R1 correction: replace each
existing untyped inventory boundary with one pre/post child-and-listener
liveness fence around one enumeration call. It MUST authorize no retry,
sentinel, extra job assignment, desktop-handle fallback, public caller or
second correction.

#### Scenario: Later correction is verified offline
- **WHEN** a separately resumed S4-R1 session implements the fenced sample
- **THEN** hostile tests prove every child, listener, empty, error, non-empty,
  main and post-fence state is exclusive
- **AND** only a live/live/non-empty/exact-main/unchanged sample can reach
  passive UIA.

#### Scenario: Correction fails its target
- **WHEN** the correction cannot pass its hostile offline target or a later
  separately authorized real-contour run still returns an inventory error
- **THEN** delivery stops with the typed evidence
- **AND** this decision supplies no authority for another correction or retry.

### Requirement: Decision grants no runtime or public authority
This change MUST modify only its board card, OpenSpec artifacts, synced spec
and protocol-research decision document, MUST preserve blocked S4-R1 and
foreign S7/OSS-07/OSS-08 bytes, and MUST NOT run 1C, access real configuration
or perform a new real-contour admission.

#### Scenario: Decision is published
- **WHEN** strict offline validation, protected-path comparison and independent
  review pass
- **THEN** only explicit card-owned documentation and OpenSpec paths are
  published
- **AND** any later real-contour confirmation still requires a new explicit
  operator resume and the source card's complete gates.
