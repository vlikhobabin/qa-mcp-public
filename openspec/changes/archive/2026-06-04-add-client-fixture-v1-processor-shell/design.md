## Context

The current accepted protocol evidence is tied to a sales dashboard form that
exposes too few stable elements. The client fixture roadmap calls for a
dedicated processor in `vanessa_client` that can evolve through V1..V4 without
depending on demo business data.

This first change intentionally creates only the shell: metadata object,
default form, top-level markers and local state/reset hook. Full control-family
coverage is handled by the next ordered change.

## Goals / Non-Goals

Goals:

- Establish a target-bound processor/form that TestClient can open.
- Make the fixture version and form identity visible through read-only UI
  inspection.
- Provide local state attributes that later controls and scenarios can reuse.
- Keep the shell independent from catalogs, documents, registers and external
  services.

Non-goals:

- Do not add the full V1 control catalog in this change.
- Do not accept clicks, text input, page switching or reset command execution
  as protocol mappings.
- Do not implement TCP parsing, protocol decoding or socket communication in
  1C.
- Do not update the manager harness or Python manager package.

## Decisions

- Create a dedicated data processor instead of reusing an existing business
  object. This keeps fixture behavior isolated from demo application logic and
  makes `PF_*` target paths stable.
- Use explicit ASCII `PF_*` markers in names, captions and values where the
  platform allows it. ASCII markers simplify response-marker review across
  Russian UI captions and encoded EDT source.
- Keep reset as a named command hook but do not rely on executing it in V1
  shell verification. The command is needed for later versions, while V1 shell
  acceptance remains read-only.
- Validate the `client` binding before retrieve/update/hot-deploy work. The
  prior investigation showed cold EDT validation may need a 90 second timeout.

## Capture And Replay Strategy

This change does not assert frame ranges, normalized hashes, dynamic fields or
operation tokens. It prepares a stable active-form target for later capture
runs. Any form-open capture or Vanessa UI proof is supporting evidence only
and must not be promoted to accepted protocol dictionary entries.

## Safety Constraints

- No business data is created, edited, posted or deleted.
- Runtime scripts may start 1C only through owned PID tracking.
- Generated EDT validation output, screenshots and raw logs stay under
  `.artifacts/openspec/add-client-fixture-v1-processor-shell/<run-id>/`.

## Risks / Trade-offs

- EDT source authoring may require exact metadata XML shape. Mitigation:
  follow existing DataProcessor/Form patterns in `vanessa_client` and validate
  with EDT before runtime apply.
- TestClient may not open the form if command interface exposure is incomplete.
  Mitigation: include explicit form-open verification and record the path used
  to open the processor.
- Reset hook may look executable before its behavior is accepted. Mitigation:
  document it as future hook and keep V1 shell verification read-only.
