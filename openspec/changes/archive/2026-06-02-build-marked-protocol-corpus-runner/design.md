## Context

The current `run_protocol_capture.ps1` path can start a TestClient, TCP proxy
and Vanessa TestManager, then clean the PIDs it owns. The proxy captures raw
chunks but does not know which 1C testing API call caused a frame range. The
existing analyzers can classify request series after the fact, and
`python_manager_probe.py` can confirm a narrow read-only schedule directly
against TestClient.

This change connects those pieces into a marked corpus loop without promoting
runtime code into `src/qa_mcp`.

## Goals / Non-Goals

**Goals:**

- Execute short, labeled read-only cases through the verified Vanessa
  attach-running path.
- Preserve case markers next to captured traffic so frame ranges can be derived
  without manual slicing.
- Generate normalized evidence rows using the corpus contract.
- Confirm accepted mappings with replay or direct Python-manager probes where
  feasible.
- Keep runtime cleanup bounded to owned PIDs.

**Non-Goals:**

- Do not build a full independent 1C TestManager replacement.
- Do not include write/action commands in the first matrix.
- Do not make raw capture depend on EDT/meta providers.
- Do not commit raw capture streams.

## Decisions

### Extend The Existing Capture Path First

The runner should reuse `run_protocol_capture.ps1`, `protocol_proxy.py` and the
current Vanessa attach-running workflow before introducing a minimal custom 1C
runner.

Alternative considered: start by writing a standalone 1C reference manager.
That can reduce Vanessa noise later, but it adds a second runtime path before
the case/evidence model is proven.

### Record Case Markers As Events

Each case should write explicit `case_start`, `case_step`, `case_result` and
`case_end` events that can be correlated with proxy chunk timestamps and MCP
tool responses. The analyzer then derives frame ranges from those events.

Alternative considered: embed markers into the TCP stream. That risks changing
the protocol being studied and is inappropriate until write/action semantics
are understood.

### Keep The First Matrix Read-Only

The first matrix should cover active-window, active-form and form-element
queries around `TestedApplication`, `TestedClientApplicationWindow`,
`TestedForm` and basic form-element properties.

Alternative considered: include `ExecuteCommand`, click and input operations.
Those need recovery semantics and fixture cleanup, so they belong in a later
corpus phase.

### Replay Confirmation Is Best-Effort But Explicit

The runner should invoke an existing replay/probe path when the case shape is
supported. Unsupported cases are still useful captures, but their rows must
show `replay_status` as pending, unsupported, rejected or timeout rather than
accepted.

## Risks / Trade-offs

- Vanessa may emit background traffic around a case - mitigate with short cases,
  case markers and repeated captures.
- Timestamp correlation may be ambiguous under fast responses - mitigate by
  recording ordered tool-call results and chunk counters in addition to time.
- Replay support may lag behind corpus capture breadth - mitigate by separating
  captured status from accepted mapping status.
- Live 1C windows may remain open if cleanup regresses - mitigate by retaining
  PID ownership manifests and static/lab cleanup checks.

## Migration Plan

No existing capture format is removed. The runner adds new manifest/events and
new compact corpus evidence while preserving current raw capture outputs.
Existing analyzers should continue to work against old captures.

## Open Questions

- Whether the first implementation should expose one `corpus_runner.py` entry
  point or keep PowerShell orchestration as the primary entry point.
- Whether case definitions should be JSON first or a small Python data module
  until the schema stabilizes.
