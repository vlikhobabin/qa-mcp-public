# TestedForm.Activate — result-contract acceptance (2026-06-14)

Accepted via the manager-fixture-v1 result-contract (same class as read_only), NOT zero-divergence
replay (raw-API session-GUID limitation tracked in board card 76).

- command_kind `form_activate`: `НайтиОбъект(ТестируемаяФорма,"QA MCP Protocol Fixture V1").Активизировать()`.
- Capture `fixture-form-activate-cap` (manager-fixture-v1-readonly, OpenFixtureViaCommandInterface
  bootstrap): case event `after/ok` → `result_preview = "form_activated=QA MCP Protocol Fixture V1"`.
  The TestedForm.Активизировать method executed live via the raw test-API and emitted protocol traffic
  (307 manager chunks captured) — confirming the protocol mapping.
- Also `active_form_activate` on the active window's form → `active_form_activated=Продажи`.

Acceptance basis: command executed + returned the expected result + command frames present in the
capture = accepted_protocol_mapping (result-contract). Zero-divergence replay deferred to card 76.
