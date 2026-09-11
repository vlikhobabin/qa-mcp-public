# TestedFormButton.Activate — result-contract acceptance (2026-06-14)

command_kind `button_activate`: НайтиОбъект(ТестируемаяКнопкаФормы) on the fixture form, .Активизировать().
Capture `safeui-tm-v1-button-activate-cap` (manager-fixture-v1, fixture-open bootstrap): case event
`after/ok` → `result_preview = "button_activated=PF_SHOW_CHOICE_LIST"`. TestedFormButton.Активизировать
executed live via the raw test-API and emitted protocol traffic. accepted_protocol_mapping (result-contract).
Zero-divergence replay deferred to card 76.
