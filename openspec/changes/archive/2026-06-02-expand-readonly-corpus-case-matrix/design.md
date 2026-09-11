## Context

The published corpus runner currently covers `active-window-context`,
`active-form-context` and `form-element-details`. The next read-only protocol
phase needs breadth across form element families, while preserving the same
source-of-truth boundary: captured TCP bytes and direct replay/probe evidence
prove a mapping; help/meta/EDT evidence only labels it.

## Goals / Non-Goals

**Goals:**

- Add an expanded read-only matrix for common form element families.
- Keep each case short enough to map one 1C testing API surface to a frame
  range and result markers.
- Preserve the reviewed row contract from
  `docs/protocol-research/corpus-evidence-contract.md`.
- Confirm accepted mappings with replay or direct Python-manager probing where
  the frame family is supported.

**Non-Goals:**

- Do not include focus, tab switching, command execution, clicks or writes.
- Do not promote protocol code into `src/qa_mcp`.
- Do not make raw capture depend on EDT/meta providers.
- Do not commit raw traffic or platform logs.

## Decisions

### Keep The Matrix Manifest-First

Add or extend a JSON-compatible case manifest before adding runner behavior.
Each case should record `case_id`, `api_call`, `ui_target`, expected state,
safety class, replay expectation and frame-range strategy.

Alternative considered: hard-code every new family in Python first. That would
make repeated capture comparison harder to audit and would mix matrix policy
with analyzer logic.

### Use Existing Vanessa Attach-Running Capture Path

The first implementation should continue using `run_protocol_capture.ps1` and
the current TestClient infobase. If a target element family is not available on
the current active form, the case should be marked `unsupported` or moved to a
fixture follow-up rather than inventing write setup.

Alternative considered: build a new reference 1C fixture first. That may be
needed later, but the current card should extract all value from the existing
read-only lab before adding fixture complexity.

### Keep Element Family Evidence Separate

Each element family should produce distinct corpus rows and compact report
sections. A single wide row for all form elements would hide which family owns
which frame range and response markers.

## Risks / Trade-offs

- The current demo form may not expose every target element family - mitigate
  by marking missing families explicitly and linking a fixture card when
  needed.
- Vanessa background refresh can add traffic noise - mitigate with short
  cases, side-channel case events and repeated captures.
- Direct Python-manager support may lag new read-only families - mitigate with
  non-accepted `pending` or `unsupported` statuses until probe support exists.

## Migration Plan

No migration is required. Existing corpus evidence remains valid. New cases
extend the corpus matrix and add new compact evidence folders.
