# Card 79 (Fork 1) — effect verification on a READ, live, no Vanessa (2026-06-15)

Fork 1 of card 79's acceptance decision: input actions assert "accepted"; the EFFECT is verified
by a subsequent READ of the field's live value. This is the Vanessa-free, ship-now bar (forks 2/3 —
de-novo / manager-side input-commit — are spun out to card 80).

## What runs

`effect_read.feature` (Russian Gherkin) → `transpile_feature` → `ScenarioRunner.run_single_session`
in ONE synthesized session against a live Linux TestClient, NO Vanessa process:

1. `я получаю сводку формы` → `read_form_summary` — opens the fixture form (frames 11-17).
2. `значение поля 'PF_EDIT_STRING' содержит 'PF_EDIT_STRING_VALUE'` → `read_form_value` — runs the
   value-read (frames 218-221), parses the field's LIVE value, asserts it contains the expected text.
3. `в поле с именем 'PF_EDIT_STRING' я ввожу текст 'PF_INPUT_PROOF'` → `input_text` — the action is
   sent and ACCEPTED by the client.

## Result — PASSED

`scenario_result.json`: status `passed`. Step 2 (`read_form_value`) assertion `True`; the value-read
response (990 B) carried `value_mode_on=True` and the extracted value `PF_EDIT_STRING_VALUE` (the 0x81
value mode, not the 0x88 stub). Step 3 (`input_text`) `accepted=True` (sent 268 B, recv 476 B).

So the native runner now performs **effect verification on reads** (read a field's live value and
assert) end-to-end from a `.feature`, Vanessa-free — the capability a real test manager needs.

## Reproduce

```bash
# 1) boot a live TestClient (Linux, headless) — see memory linux-native-testclient-xvfb
xvfb-run -a "$PLATFORM_ROOT/1cv8" ENTERPRISE /IBConnectionString "File=\"$INFOBASE_PATH\";" \
  "/N$TEST_CLIENT_USER" /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages &
# 2) regenerate the merged open+value-read template (gitignored runtime artifact)
PYTHONPATH=src python3 tools/protocol-research/build_tm_v1_open_template.py
# 3) drive the .feature through the native runner, no Vanessa
PYTHONPATH=src python3 tools/protocol-research/native_scenario_runner.py \
  --host 127.0.0.1 --port 15381 --single-session \
  --manager-templates runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json \
  --feature docs/protocol-research/evidence/native-effect-read-verification-2026-06-15/effect_read.feature \
  --action-capture fixture-input-capture --action-input-value PF_INPUT_PROOF
```

Requires the gitignored captures `tm-v1-ro-batchQ3` + `fixture-input-capture` under
`runtime/protocol-research/captures/` (sync separately).

## Implementation

- `qa_mcp.protocol.responses.extract_edit_field_value` / `value_mode_present` — value-read parser.
- `qa_mcp.protocol.session.SessionHandle.read_form_value` + `FormValueContext` — open form + value-read.
- `read_form_value` step kind (`qa_mcp.scenario.model`) + runner dispatch (`qa_mcp.scenario.runner`).
- Gherkin rules for `значение поля '…' содержит '…'` and `я читаю значение поля '…'`.
- `form-value-read` read-only operation descriptor (`qa_mcp.protocol.evidence`).
- Offline tests: `tests/test_form_value_parser.py`, runner + gherkin tests (160 pass).
</content>
