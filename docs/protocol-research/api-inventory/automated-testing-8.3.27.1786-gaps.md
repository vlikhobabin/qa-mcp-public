# Automated Testing API Inventory Gaps

Inventory:
`docs/protocol-research/api-inventory/automated-testing-8.3.27.1786.json`

Open gaps:

- `help_snapshot_version`: the available help snapshot is `8.3.27.1786`, while
  the local protocol lab baseline is `8.3.27.2130`.
- `client_agent_api_objects`: `help-mcp` did not resolve a
  TestClientAgent/client-agent entity in the first pass; broad semantic search
  was degraded because `EMBEDDING_API_URL` is not set.
- `member_parameter_signatures`: `list_type_members` gave object/member names,
  aliases and return summaries, but not stable parameter signatures.
- `constructor_signatures`: constructor overloads for
  `ТестируемоеПриложение` still need manual help expansion before generated
  BSL depends on them.
- `command_bar_object_identity`: exact lookup for
  `ТестируемаяКоманднаяПанельФормы` returned no object; current rows expose
  command bars as `ТестируемаяГруппаФормы`.
- `tested_form_table_exhaustiveness`: `ТестируемаяТаблицаФормы` reported
  40 members; 39 retained rows are enough for first safety planning, not final
  exhaustive publication.

Required follow-up before corpus scale-out:

- Re-run or diff this inventory against help `8.3.27.2130` when that snapshot
  is available.
- Expand parameter signatures for selected read-only and safe-action members.
- Resolve client-agent/runtime API identity or keep it explicitly out of the
  first corpus manifest.
- Treat table and command-bar coverage as partial until a second extraction
  pass confirms the missing rows.
