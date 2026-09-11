## 1. State Model

- [x] 1.1 Add a fixture-local mutation state record and marker update helpers
  for baseline, editable values, inert action markers and local counters.
- [x] 1.2 Wire form initialization and reset so the V1 baseline is restored
  from one shared routine after each mutation.

## 2. Verification

- [x] 2.1 Retain Windows-native open/reset evidence that proves the mutation
  baseline markers return to the V1 baseline.
- [x] 2.2 Run `bin\openspec.cmd validate mutation-state-model --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/mutation-state-model
  openspec/board`.

Evidence retained under
`.artifacts/openspec/mutation-state-model/20260608-v3-surface/`. Runtime
open/reset proof shows V3 markers at baseline after live open and after reset.
The paired `mutation-form-handlers` proof completed later in the same surface
delivery with normal Vanessa/TestClient number/date input and reset evidence
before archive.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V3 mutation state markers and reset hook | Observable local marker set and baseline restore | Read-only form inspection before and after reset | `.artifacts/openspec/mutation-state-model/<run-id>/state-model/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: marker names may drift until the form module is updated |
| Form module or command | Mutation state helpers, baseline initialization and reset routines | Deterministic marker update and reset model | BSL diagnostics; focused runtime open/reset proof | `.artifacts/openspec/mutation-state-model/<run-id>/bsl-reset-proof/` | required | `project:qa-mcp`, `/opt/edt-lab` | N/A | Medium: helper drift can bypass the shared reset path |
| Runtime apply | BSL and managed form update | Spec-driven fixture state change | Windows-native open/reset evidence and OpenSpec strict validation | `openspec/changes/mutation-state-model/` | required | `project:qa-mcp` | N/A | Low: change is local to the fixture surface |
