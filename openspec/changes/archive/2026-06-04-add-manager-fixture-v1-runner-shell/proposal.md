## Why

The protocol corpus needs a controlled 1C TestManager-side harness instead of
using broad Vanessa Automation feature steps as the primary case generator.
The `manager` EDT target is now importable and binding-valid, so the first
implementation step is a target-bound runner shell in `vanessa_manager`.

## What Changes

- Add a dedicated manager-side fixture processor/harness shell in the
  `target_id=manager` EDT project.
- Keep the shell responsible for TestManager/TestedApplication orchestration
  only; it must not parse TCP or normalize protocol frames inside 1C.
- Add explicit run context fields for `run_id`, client fixture navigation
  target, proxy TestClient port and output directory.
- Add a bootstrap command path that opens the client fixture form and records
  that bootstrap traffic separately from corpus cases.
- Require manager target binding validation and retained deployment/runtime
  evidence before the shell is used for corpus runs.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require a target-bound manager harness shell for
  controlled TestManager API execution against the client fixture.

## Impact

- Touches 1C EDT source in
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager`.
- Uses local `edt-mcp` for manager binding, source validation and deploy/apply
  evidence.
- Requires live 1C runtime and Vanessa/TestClient evidence during
  implementation verification.
- Does not change Python protocol parsing or accepted protocol mappings.
