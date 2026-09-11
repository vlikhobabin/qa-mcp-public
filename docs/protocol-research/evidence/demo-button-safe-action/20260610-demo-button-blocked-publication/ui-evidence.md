# Demo Button UI Evidence Summary

Run id: `20260610-demo-button-blocked-publication`

## Runtime UI Status

No live UI evidence was captured for this publication because the classification
gate failed before runtime execution. This is intentional for the blocked path.

Retained upstream provider facts:

- Vanessa `get_form_analysis` failed before form analysis because the
  TestClient was not connected.
- Dry-run `project_ui_evidence_preflight` reported no active TestClient.
- No screenshot is claimed for the selected real demo button.

## Source UI Status

The selected target is a static source candidate:

- external source boundary:
  `C:\1C_BASES\EDT\demo10413\demo10413`;
- source object alias:
  `Document.OperatsiyaPoUchetuTovarov.Form.FormaDokumenta`;
- element path alias:
  `TovarnyeZapasyKomandnayaPanel/PereklyuchitAktivnost`;
- source state: visible and enabled.

Source evidence is sufficient for a conservative rejection because the target
is tied to register-record activity state. It is not sufficient to prove a V2
safe UI action.

## Provider Gap

| Provider | Owner route | Missing evidence | Impact |
| --- | --- | --- | --- |
| `vanessa` | `/opt/vanessa-mcp-stack` | live active-window/form tree and screenshot for selected target | non-blocking because the target was rejected before execution |
| `meta-mcp` / `edt-mcp` | `/opt/finshtab-1c`, `/opt/edt-lab` | typed command semantic inspection for `commandName=0` | non-blocking because source evidence is enough to fail closed |

No UI action was performed.
