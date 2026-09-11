# qa-mcp — operator / consumer reference (63 stable standalone tools)

This is the **consumer-facing** reference: how to drive qa-mcp as a QA tool and
the 63-tool stable standalone support matrix, grouped by purpose. The source
inventory currently contains 68 tools: four explicit `research`-profile tools
and dormant `open_external_processor` are listed separately and are not stable
standalone support. This reference is deliberately separate from the
protocol-research narrative under `docs/protocol-research/` (which documents
*how* the native TestClient protocol was decoded — internals, not usage).

- New to the project? Read this + [`vanessa-mcp-parity.md`](vanessa-mcp-parity.md) (the Gherkin step library and the
  Vanessa→qa-mcp authoring guide). You do **not** need the research trail to use qa-mcp.
- Continuing development? Start at [`program-102-native-superset-handoff.md`](program-102-native-superset-handoff.md)
  and the active roadmap `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`.

State: **63 stable standalone tools; 68 source/research inventory tools; real
Vanessa corpus transpile 11.9% → 100%.** The current code-level `standalone`
catalog is a 64-tool pre-stable runtime inventory, not a stable-support claim.
The declared stable profile omits dormant `open_external_processor`; the
remaining four non-stable tools are explicit research inventory.

## What qa-mcp is

qa-mcp drives real 1C:Enterprise managed forms over the **native TestClient protocol, capture-free, with NO Vanessa
Automation runtime in the loop**. It launches a native `/TESTCLIENT` (headless under Xvfb), replays the irreducible
7-frame handshake once (below the configuration layer, so one capture works for any config at a given platform
protocol version), and synthesizes every other frame from per-element templates. On top it exposes two authoring
surfaces:

- **Gherkin / BDD** — the high-level surface. Author a `.feature` from the canonical step library and run it with
  `run_scenario`; existing Vanessa feature suites transpile (corpus 100%). See `vanessa-mcp-parity.md`.
- **The 63 stable standalone MCP tools** — the supported programmatic surface
  for finer control (below).

## Quickstart — author and run a test

```python
from qa_mcp import mcp_server

# 1) discover the supported Gherkin vocabulary
mcp_server.search_for_steps(keywords="")          # → canonical phrasings + kinds

# 2) check a feature transpiles (never silently drops a step — unmapped lines are reported)
mcp_server.transpile(feature_text=open("smoke.feature").read())

# 3) run it (boots/uses a TestClient; reads/asserts/data/open actions execute live)
mcp_server.run_scenario(feature_text=open("smoke.feature").read(), host="127.0.0.1", port=15381)

# 4) emit a CI report
mcp_server.write_test_report(path="out/", junit=True, allure=True)
```

For the live lab boot recipe (Xvfb + Apache/OData + teardown discipline) see
`program-102-native-superset-handoff.md` § "Proven lab recipes". Live writes (`*_xtest`, calendar, by-label) need a
real X display + matchbox; reads / asserts / data-layer / open-actions do not.

## Stable standalone support matrix

Before chasing individual failures in a model-B setup, run `qa_mcp_doctor` from
the MCP surface or `qa-mcp-doctor` from the shell. It returns one secret-safe
pass/fail/skipped chain covering bearer-token env presence, host-agent HTTP
reachability, container-to-host route, platform discovery, TestClient TPort,
an open-link-free TestClient smoke, login/access-dialog evidence, effective-user
evidence when available, and the COMConnector doctor when configured.
The doctor uses light-weight health, TestClient and optional COM routes only; it
does not run Designer metadata dumps such as `DESIGNER /DumpConfigToFiles`.

### Lifecycle / session (5)
| tool | purpose |
| --- | --- |
| `qa_mcp_doctor` | one secret-safe setup diagnostic chain; bearer verification defaults on for HTTP transports and off for stdio; use it to distinguish missing bearer env, host-agent HTTP/route failures, TestClient TPort failures, open-link-free smoke, login-dialog state, effective-user evidence, and COM doctor status |
| `launch_test_client` | boot a native `/TESTCLIENT` (headless under Xvfb or through the Windows host-agent); local launch refuses an already-occupied TPort, records process ownership before waiting, and requires a non-consuming TPort check plus a 20-second process-stability window; applies the Linux libgcc preload when needed, optionally manages Apache + clears the infobase lock, and reports bounded launch diagnostics; a remote owned launch records a lifecycle-bound `client_target` |
| `attach_test_client` | attach to an already-listening TestClient TPort without claiming process ownership; records the active attached endpoint and, when the Windows host-agent resolves it, a non-owning `client_target` for this MCP process |
| `test_client_status` | is a client up; connection/listen state |
| `stop_test_client` | tear the client down (restart Apache in your `finally`) |

Composed servers keep runtime output under their active `QA_MCP_HOME` (or the
documented static fallback for an explicitly empty setting). Ownership markers
use the active `QA_MCP_TESTCLIENT_OWNERSHIP_ROOT` when set, otherwise that
server's lifecycle subdirectory; local composed launches put marker and
lifecycle output together so later cleanup remains scoped after environment
drift. Direct low-level callers retain the environment-backed compatibility
adapter. This does not alter ownership identity checks or project-bound evidence
root/retention policy.

After `attach_test_client` succeeds, endpoint-touching protocol tools called with the default host/port use that
attached endpoint for this MCP server process. Pass a non-default `host` or `port` to target a different client
explicitly. This route covers descriptor/value reads, waits/asserts, write helpers, scenario execution, replay-backed
actions, dialogs, list/report/window helpers and `get_window_list_testclient`; stale attached descriptor reads fail
closed with an attached-endpoint diagnostic instead of returning a silent empty form.

For a project-bound server, every native-session tool requires the current exact
target/session/attachment/generation route before it evaluates hidden arguments,
checks an endpoint, uses the display, or sends a native command. Missing, stale,
foreign or malformed route state returns `runtime-target-route-blocked`. This is
independent of result-schema membership (including `click_command`); unknown
bound operations fail closed. Lifecycle, provider-data, and pure/readiness tools
retain their separately documented policies, and an explicitly unbound server
retains its compatibility behavior.

### Composed relay configuration

When constructing a server with `create_mcp_server(settings=...)`, native
session, replay, foreground, write/mutation/XTEST, and lifecycle/attachment
paths use that server's relay endpoint and token only.  Separate server
factories remain isolated from each other and from a conflicting process relay;
an explicitly unconfigured factory stays a direct connection.  Relay
authentication is limited to the exact configured endpoint.  Listener-only
readiness never authenticates, sends TestClient protocol bytes, or acquires a
manager session.

Invalid scoped relay settings are refused before a socket opens and public
diagnostics omit tokens and untrusted relay reply text.  Direct callers of the
low-level transport helpers may still supply their explicit environment mapping
outside server composition, but that mapping cannot override an active server's
settings.  These boundaries have hermetic fake-socket coverage; live relay and
native TestClient qualification requires its separately authorized runtime
verification.

In a project-bound server, general non-owned `attach_test_client` is deliberately unavailable: TCP reachability,
PID/TPort status, the declared profile, and a prior owned handle do not prove the infobase of a newly attached
process. It returns `runtime-target-observation-missing` before admitting a session or sending TestClient/UI commands.
This limitation remains until a separately reviewed observer can provide current process-to-target and binding-generation
proof. Explicit standalone attach and validated owned launch retain their existing contracts.

In model-B remote mode, an active launch/attach target is inherited by implicit
`capture_screenshot`, `send_keys`, text, click, and visible-list-cell routes.
An explicit non-empty, non-`*` window selector always wins. Implicit inheritance
requires the host-agent `testclient-window-target` capability; missing,
mismatched, or stale identity fails closed and never falls back to the OS
foreground application. Locked, disconnected, and non-interactive Windows
desktops retain the typed host-agent diagnostics
`desktop-session-locked`, `desktop-session-disconnected`, and
`desktop-session-noninteractive` in the MCP error result.
If a form-level read returns `open-link-required`, use `qa_mcp_doctor` first to prove the raw
MCP-to-TestClient connection, then pass an explicit `open_link` such as
`e1cib/list/Справочник.Валюты` or `e1cib/list/<metadata>` to the form-level tool.
For catalog-name troubleshooting, prefer descriptor/open-link input,
metadata-provider input, or the optional COM read-smoke route; Designer
metadata dump is not a routine connection diagnostic.

### Scenario / BDD authoring & execution (5)
| tool | purpose |
| --- | --- |
| `transpile` | Gherkin `.feature` → native scenario JSON; reports `unmapped` steps (never drops silently) |
| `search_for_steps` | list the supported Gherkin step library (canonical phrasing + kind + example), derived from `STEP_PATTERNS` |
| `run_scenario` | run a `.feature` / scenario JSON natively (reads, asserts, data-layer, open actions, nested scenarios) |
| `run_step` | execute a single step (Vanessa `execute_step_from_text` equivalent) |
| `run_write_scenario_tool` | run a write-oriented scenario (input + commit) against a captured action template |

### Reporting / state / results (4)
| tool | purpose |
| --- | --- |
| `get_test_results` | aggregate the scenarios run this server session (pass/fail/step counts) |
| `write_test_report` | emit JUnit XML + Allure results (per-step timing + screenshot attachments) for CI |
| `get_state` | capture-free `get_state` equivalent — connection + run-session + infobase identity |
| `infobase_info` | infobase/connection metadata from the `.ai1c` profile (password-redacted) + live listening |

### Read / introspection (11)
| tool | purpose |
| --- | --- |
| `read_form_descriptor` | full element name→value descriptor + Gherkin state; `open_link=` opens ANY form by nav-link; `enumerate_live=` enumerates fields live (ASCII **and** Cyrillic names) |
| `read_active_window` | bound reads expose only the finite `window_state` (`observed`/`missing`/`ambiguous`) and bounded `marker_count`; requested window assertions return `assertion_passed` without exposing raw UI references or expected text |
| `read_record` | read a navigated record's fields |
| `read_table_cell` | read a form-table cell |
| `read_list_column` | read one dynamic-list cell |
| `read_list_row` | read a row's columns (or a row BY VALUE via `where={col: value}`) |
| `read_list_grid` | read the whole dynamic-list grid (next-row command; `flat=True` for a hierarchical catalog in flat view) |
| `read_spreadsheet_cell` | read a spreadsheet-document cell |
| `read_user_messages` | read the client's user-message area (`Сообщить`) |
| `get_window_list` | OS top-level windows on the client display (xdotool: id/title/geometry); bound backend failures are returned as operation failures, while successful inventories preserve their exact `count` (including zero) |
| `get_window_list_testclient` | the 1C-internal window/tab list (caption + frame kind); for raw connection smoke without `open_link`, use `qa_mcp_doctor` |
| `capture_screenshot` | OS screenshot of the client display; trusted bound producers allocate and verify a fresh destination and actual digest before sanitized cleanup or full_local retention. Standalone calls retain the returned image; remote implicit calls inherit the active lifecycle/client target and refuse weak foreground fallback |

### Assertions / waits (5)
| tool | purpose |
| --- | --- |
| `assert_form_value` | assert a form field equals/contains a value |
| `wait_for_form_value` | poll a form field until it reaches a value (or timeout) |
| `assert_data` | **beyond Vanessa** — assert a UI action persisted to the DB via a read-only OData client (`entity_set/field/expected`, `match=equals\|contains\|regex`) |
| `assert_data_count` | **beyond Vanessa** — assert the NUMBER of records matching a filter (`op=eq\|ne\|gt\|lt\|ge\|le`); e.g. "posting created exactly N register rows", "no orphan remains" |
| `role_data_matrix` | **beyond Vanessa** — run the same data-layer read under several credentials/roles → per-role access (`read`/`denied`) + count (data-layer security verification) |

### Host-side COM read / diagnostics (3)
| tool | purpose |
| --- | --- |
| `query_com` | execute a bounded read-only 1C query through the configured Windows host-agent COM worker |
| `assert_com_count` | compare the first numeric result of a bounded COM read query with an expected count |
| `com_connector_doctor` | diagnose COMConnector availability, bitness, registration and actionable host repair guidance |

### Write / input (6)
| tool | purpose |
| --- | --- |
| `write_form_value` | string/number/date input + commit via the protocol template (captured action) |
| `write_form_date` | validate and write a form date by field name/label, with optional open-link routing |
| `write_form_value_xtest` | input + commit via the protocol+XTEST hybrid (real OS keystrokes; needs a display) |
| `write_form_values` | write several fields in one session |
| `write_form_fields_by_label` | **config-agnostic** arbitrary-field write by visible label «X:» (foreground → locate → xtest type), no per-field capture |
| `send_keys` | raw OS keyboard keys (Enter/Esc/Tab/arrows/shortcuts) via XTEST/local display or the Windows host-agent; model-B implicit calls inherit the exact active lifecycle/client target, `F5`/`Escape` avoid foreground steal, and foreground/session refusals remain typed |

This lifecycle-window binding changes no native TestManager/TestClient wire
frames and makes no protocol-corpus claim, so the protocol evidence index is
not updated. Windows screenshots, identities, binaries, request payloads, and
logs used for verification remain under ignored `.runtime/` paths; reviewed
evidence contains only sanitized booleans, typed reason codes, and test
outcomes.

### Form field actions (12)
| tool | purpose |
| --- | --- |
| `switch_page` | switch a form tab/page |
| `toggle_checkbox` | toggle a checkbox |
| `set_choice` | set a choice/enum field |
| `set_reference_field` | set a reference (lookup) field |
| `set_table_cell` | write a form-table cell |
| `set_table_date_cell` | set a date in a table date cell (config-agnostic; auto-localized; calendar driven by mouse) |
| `select_table_row` | select / go to a table row |
| `add_table_row` · `delete_table_row` · `move_table_row` · `copy_table_row` · `select_all_table_rows` | table-row CRUD / ordering / bulk-select |

### Navigation / windows (5)
| tool | purpose |
| --- | --- |
| `open_list` | open a list form by nav-link; omitted/blank `capture` uses the released versioned navigation templates, while a non-blank capture keeps explicit replay compatibility; missing navigation assets fail closed before protocol I/O |
| `open_card` | open an object card (e.g. by a button) |
| `close_window` | close the current/named window |
| `activate_window` | bring a window to the foreground |
| `click_command` | click a form command/button |

### Lists / search / reports / dialogs (7)
| tool | purpose |
| --- | --- |
| `search_list` | search/filter a dynamic list |
| `set_list_view` | switch a dynamic list's view mode |
| `advanced_search` | dynamic-list advanced filter |
| `choose_from_list` · `choose_from_menu` | pick from a selection list / menu |
| `answer_dialog` | answer a modal dialog (Да/Нет/ОК) |
| `run_report` | run a report |

## Non-stable source/runtime inventory (5)

These entries are intentionally outside the stable support matrix. The four
research tools require `QA_MCP_TOOL_PROFILE=research`. The dormant external-
processor tool remains in the unchanged pre-stable runtime catalog only to
preserve implementation and qualification foundations; it is not stable
support.

| tool | inventory status |
| --- | --- |
| `open_external_processor` | **dormant** — omitted from stable standalone support until a separately reviewed target-bound qualification publishes |
| `echo_jsonrpc_arguments` | **research-only** — inspect parsed JSON-RPC arguments and likely encoding damage |
| `generate_smoke_suite` | **research-only** — metadata-driven smoke generation |
| `autofill_required_fields` | **research-only** — metadata-driven required-field values |
| `measure_scenario` | **research-only** — debug-protocol coverage and performance measurement |

## Beyond Vanessa (what Vanessa Automation cannot do)

`assert_data` (UI→DB cross-verification), `generate_smoke_suite` / `autofill_required_fields` (metadata-driven test
generation), dormant `open_external_processor` (Vanessa-component-free external `.epf` open, omitted from stable
standalone support pending separate qualification), and `measure_scenario` (code coverage + perf/APDEX during a UI
run). These are retained non-stable inventory, not entries in the stable support matrix. See
`vanessa-mcp-parity.md` § "Beyond Vanessa" for the rationale.

## Regression

To re-verify that these capabilities still work against a real 1C TestClient (not just that frames encode
correctly), run the **live-regression harness** — one gated command that boots a TestClient, exercises the
LIVE-verified capabilities, and exits non-zero on a regression: `python -m qa_mcp.regression`. See
[`live-regression.md`](live-regression.md).

## CI quality gates (beyond Vanessa)

Built on `measure_scenario` (code coverage + perf/APDEX via the debug protocol) — enforceable in CI:

- **Per-step perf budget** — the Gherkin step «`Каждый шаг выполняется быстрее N мс`» (kind `assert_step_perf`)
  fails a scenario when any step's wall-clock exceeds N ms.
- **Coverage gate** — `python -m qa_mcp.debug.gates --report <measure.json> --min-lines N [--min-modules N]
  [--required "Object :: Module"]` exits non-zero below an agreed coverage bar (works on a saved report or
  measures live via `--feature`).

## See also

- `vanessa-mcp-parity.md` — the Gherkin step library, the Vanessa→qa-mcp tool coverage map, and the authoring guide.
- `live-regression.md` — the live-regression harness (CI/cron-gateable capability checks).
- `program-102-native-superset-handoff.md` — development handoff + the live lab boot recipe.
- `protocol-research/` — how the native protocol was decoded (internals; not needed to *use* qa-mcp).
