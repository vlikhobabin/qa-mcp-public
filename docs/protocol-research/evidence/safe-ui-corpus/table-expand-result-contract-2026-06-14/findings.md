# TestedFormTable.Expand — result-contract (2026-06-14)

User added a dynamic-list-as-tree to ФикстураПротоколаTestClient, table name "ДенамическийСписокИерархия" (sic). command_kind table_expand: НайтиОбъект(ТестируемаяТаблицаФормы,,"ДенамическийСписокИерархия") -> Активизировать() -> Развернуть() -> Развернут()=Да. result_preview = "table_expanded=Да". TestedFormTable.Развернуть executed live via raw test-API and the table became expanded. accepted_protocol_mapping (result-contract). Zero-divergence deferred to card 76.

Note: the earlier Товары-list limitation (Развернуть throws "Неподходящее состояние" on a collapsed dynamic-list group row) did NOT bite on this fixture tree — Развернуть succeeded (expanded=Да). So the limit is row/state-specific, not blanket for dynamic lists.
