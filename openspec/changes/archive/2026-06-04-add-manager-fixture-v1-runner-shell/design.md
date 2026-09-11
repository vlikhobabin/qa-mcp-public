## Context

The client fixture V1 exists in the `vanessa_client` EDT target and has live
open evidence. The manager side was not previously connected as an EDT project,
but the `manager` target now resolves to project `vanessa_manager` and file
infobase `C:\1C_BASES\vanessa_manager`.

The manager V1 runner shell is the first 1C-side tool that will generate a
controlled TestManager/TestedApplication command stream for protocol capture.
It is a harness shell, not a protocol analyzer.

## Goals / Non-Goals

**Goals:**

- Create a target-bound manager fixture processor/harness in
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager`.
- Accept a run context with `run_id`, proxy TestClient port, client fixture
  navigation target and output directory.
- Bootstrap the live client fixture form and record bootstrap status before
  corpus commands run.
- Verify through `edt-mcp` binding, EDT validation/apply evidence and a
  Vanessa/TestClient runtime smoke.

**Non-Goals:**

- No TCP parsing, frame normalization or socket handling inside 1C.
- No read-only command catalog beyond the shell-level bootstrap path.
- No clicks, text input, page switching, business commands or writes.
- No accepted protocol mapping publication.

## Decisions

1. Use a dedicated manager fixture processor instead of Vanessa feature steps
   as the primary corpus generator.
   Rationale: a processor can execute a documented command list and write
   stable side-channel records. Vanessa remains useful for smoke evidence and
   comparison, but feature steps are too broad for a reference corpus.

2. Bind all source/deploy operations through `target_id=manager`.
   Rationale: this mirrors the completed client fixture workflow and prevents
   accidental edits against the client project or an implicit EDT project.

3. Keep the shell input/output file based.
   Rationale: the capture runner can choose the runtime directory and pass it
   to 1C without introducing sockets or protocol parsing in the manager
   fixture.

4. Label bootstrap traffic separately.
   Rationale: opening the client fixture form is required setup, but bootstrap
   frames must not be confused with read-only command cases.

## Risks / Trade-offs

- Manager 1C process startup may be slow or blocked by an existing session.
  Mitigation: use bounded runner timeouts and retain startup failure evidence.
- EDT deploy can report project dirty or not equal after import.
  Mitigation: require `validate_project_infobase_binding(target_id="manager")`
  and deploy/apply evidence before runtime smoke.
- The exact TestManager API object names may differ by platform/help wording.
  Mitigation: keep implementation checked against platform help or semantic
  provider evidence before finalizing command calls.
- Client fixture navigation can fail if the client fixture was not applied.
  Mitigation: require the existing client live-open evidence or rerun it as a
  preflight during implementation.

## Migration Plan

1. Add the manager fixture processor/form/module source under the
   `vanessa_manager` EDT project.
2. Validate source and apply it only after manager binding validation passes.
3. Run a runtime smoke that opens the harness and performs bootstrap without
   executing read-only corpus cases.
4. Keep generated runtime output under ignored `.artifacts/` or `runtime/`
   paths and publish only compact evidence summaries when needed.

## Open Questions

- Whether the processor object name should mirror the client Cyrillic fixture
  name or use an ASCII metadata name such as `ProtocolFixtureTestManager`.
- Whether the implementation should launch the harness through a form command,
  `/Execute`, or a small command-line wrapper around the manager infobase.
