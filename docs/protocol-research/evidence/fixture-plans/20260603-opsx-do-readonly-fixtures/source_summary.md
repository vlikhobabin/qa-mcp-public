# Source Summary 20260603-opsx-do-readonly-fixtures

## Inputs

- Semantic source inventory:
  `docs/protocol-research/semantic-source-inventory.md`.
- Semantic map:
  `docs/protocol-research/evidence/semantic-mapping/20260603-opsx-do-semantic-mapping/semantic_map.md`.
- Current corpus evidence:
  `docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`.
- Planned case manifest:
  `fixture_case_manifest.json`.

## Summary

The current accepted read-only corpus maps active window, active form and
`EditField`/typed-input details. The missing `Button`, `Table`, `CommandBar`,
`Page`, `Label` and `CheckBox` families are visible as unsupported fixture gaps
because the current sales dashboard form does not provide compact accepted
wire evidence for those families.

`meta-mcp` readiness for the `demo10413` EDT source tree was used only as
semantic support for fixture planning. Raw metadata provider payloads, EDT
generated output and infobase exports are not committed. `help-mcp` labels are
used to choose expected testing API marker names, not to prove native protocol
behavior.

## Output Boundary

The reviewed git output for this change is limited to compact planning files:

- `fixture_plan.md`;
- `fixture_case_manifest.json`;
- `source_summary.md`.

Future live runs must keep raw capture and generated authoring output in
ignored runtime or artifact paths and link only compact evidence summaries from
reviewed docs.
