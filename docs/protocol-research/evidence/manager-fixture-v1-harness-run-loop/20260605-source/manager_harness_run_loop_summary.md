# Manager Fixture V1 Harness Run Loop Source Evidence

Run id: `20260605-source`

Scope:

- Manager harness source:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\Forms\ManagerHarness\Module.bsl`
- Manager harness form:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\Forms\ManagerHarness\Form.form`

Implemented source contract:

- Added `TM_MANIFEST_PATH` as a form attribute and run-context field.
- Added `TM_RUN_MANIFEST_V1` as the explicit manifest-driven UI command.
- Added `ВыполнитьЗапускМанифестаV1()` to load
  `manager_harness_manifest.json`, validate all commands before execution,
  open one TestClient connection through the manifest proxy port, execute
  read-only commands in manifest order, emit before/after events and write a
  final run result.
- Kept V1 action and mutation command kinds rejected before execution through
  `ЗапрещенныеКомандыV1()` and `ПроверитьКомандуМанифестаV1()`.
- Fixed the manifest validation loop so it iterates the `commands` array.

Validation performed:

- XML parse of `Form.form`: passed.
- Form command/attribute assertions for `TM_RUN_MANIFEST_V1` and
  `TM_MANIFEST_PATH`: passed.
- BSL routine boundary count: 23 starts and 23 ends.
- EDT probe diagnostics: not available. The `lab.edt.bslprobe` plugin is
  missing and the interactive EDT shell timed out during readiness check.
- Metadata MCP structural lookup for `ProtocolFixtureTestManager`: no indexed
  evidence in the default `demo10413` snapshot; local source checks are the
  retained evidence for this change.

Runtime status:

- No live 1C invocation was performed for this change. Live capture and
  traffic proof are covered by the later capture-runner and smoke-evidence
  changes in the same OPSX card.
- Sample manifest, event and result files in this directory describe the
  expected contract for local dry-run review.
