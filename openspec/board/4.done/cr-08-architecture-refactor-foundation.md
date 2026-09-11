# CR-08 — Architecture refactor foundation (roadmap-111 item 5)

## Status
4.done

## Order Index
8

## Owner
codex

## OpenSpec Stage
archived

## Source
- Multi-agent architecture review 2026-07-02, findings A1, A2, A5, A6 + dead-code
  / dedup cleanups. This is the deferred **card-111 item 5** ("wire-constants +
  split god-files"). Full report: `docs/code-review-2026-07-02.md`.

## Summary
Structural debt concentrated in two god-files: `mcp_server.py` (4405 lines,
~1800 of them wire-level protocol code) and `native_write.py` (2558 lines, 14
near-identical replay functions). This card extracts the seams the package
structure already promises, behind the safety net that CR-01..CR-07 provide
(honest verdicts, hardened transport, the tool decorator, and CI). **Do this
last** — it is pure refactor and should not change behavior, so it must land on
top of a green, CI-gated suite. Sequence the sub-steps; each is independently
shippable.

## Already delivered by CR-03/CR-04 (2026-07-02) — do NOT redo, MUST preserve
Verified against `main` after cr-03/cr-04 archived:
- **Single receive point already exists:** `src/qa_mcp/protocol/transport.py::read_protocol_available`
  (frame-aware: waits for tail marker `66 53 b2 a6`, `time.monotonic()` deadline).
  `session.read_available` and `native_mutation._read_available` are now **thin
  delegators** to it. The `ReplaySession` in sub-step 1 MUST call this helper and
  MUST NOT reintroduce an idle-gap loop; it may collapse the two delegators.
  Preserve its semantics: stop at the **first** tail marker; tail-less buffers
  block to the hard deadline (higher latency, never truncates).
- **New symbols the split will relocate (leave the behavior intact):**
  `WriteRetargetError`, `_retarget_failed_result`, `_write_value_matches_readback`,
  the `ProtocolSendTimeout`/`send_timeout` send-hygiene path (native_write.py);
  `retarget_element_leaf_reencode` (element_ref.py); `read_protocol_available`
  (transport.py). Any `mcp_server.py` split (sub-step 2) must keep
  `_values_equivalent` (now `allow_prefix` gated on `date`/`reference`) and the
  `activation_retry`/`_should_retry_label_locate` path.
- **Dead-code list is now smaller:** `create_splice` string and its guard were
  **already removed** by cr-03, and `_splice_window_activate_command` is now
  **LIVE** (used by the cr-03 label-locate retry at `mcp_server.py:3298`) — do
  **NOT** delete it. `_CreateForegroundHold` (`mcp_server.py:3290`) is now
  genuinely dead (defined, never referenced) → safe to delete. Still-dead:
  `_RESOLVE_SF_RE` (`:3246`, only defined), `_OPEN_LINK_LABEL_ALIASES` (`:264`,
  empty dict via `_resolve_open_link_label` `:296`). `mutation.py::render_write_frame`
  is still imported by `native_mutation.py:26` (used at `:369`) — verify whether
  `native_mutation` itself is on a live path before deleting `mutation.py`.

## Problems (verified against code)

### A2 — `native_write.py`: 14 near-identical replay functions
The same ~40-line loop is pasted per operation: 20× `socket.create_connection`,
20× `GuidRebinder.from_client_chunks`, 27× `rebinder.observe_response(...)`, 7×
the setup-replay. `switch_page`, `toggle_checkbox`, `set_choice`, `open_list`,
`click_command`, `choose_from_list`, `answer_dialog`, `set_reference_field`,
`search_list`, `advanced_search`, `read_spreadsheet_cell`, `open_card`,
`close_window`, `activate_window`, `read_user_messages` differ only in (a)
template dataclass, (b) per-frame retarget fn, (c) accept/commit verdict.

### A1 — `mcp_server.py` contains a second protocol layer
~1800 lines are wire code, not tool plumbing: `_foreground_form_by_link` (`:2197`,
raw socket + GuidRebinder + per-frame version substitution), splice helpers
(`_splice_window_activate_command` `:3259`, `_splice_header_no_form` `:2964`),
sweeps (`_read_field_value` `:3030`, `_read_form_descriptor` `:3659`,
`_read_table_cell` `:3855`, `_read_testclient_windows` `:4282`), duplicate regexes
(`_DESCRIPTOR_FORM_PATH_RE` `:3194`, `_RESOLVE_SF_RE` `:3233` [unused]).

### A5 — version policy lives in the wrong package (protocol → regression up-dep)
`active_version_key()` (selects `_bundled/<8.3|8.5>/`) is defined in
`regression/versioning.py` and consumed by `protocol/` via deliberately lazy
imports (`bootstrap.py:35`, `evidence.py:33`, `mcp_server.py:31`) to dodge the
import cycle (`regression.versioning` imports `protocol.lifecycle`).

### A6 — 26 `QA_MCP_*` vars read at ~37 scattered sites
Some frozen at import time (`mcp_server`), some re-read per call
(`display_backend`) → changing env mid-process affects one and not the other; the
`QA_MCP_REMOTE_CLIENT` truthy parse is duplicated verbatim; ODATA defaults
duplicated across `data/odata.py` and `regression/__main__.py`.

### Dead code / dedup (low-risk cleanups)
`_CreateForegroundHold` + the `create_splice` branch (dead — see CR-03 S2),
`_RESOLVE_SF_RE` (unused), `_OPEN_LINK_LABEL_ALIASES`, `mutation.py` (docstring:
"kept only for offline round-trip"); dups: `_normalize_form_date` ≡
`runner.normalize_form_date`, `substitute_guid_all_encodings` ≡
`_sub_guid_all_encodings`, `_read_chunks` ≡ `CaptureBootstrap.load`, inline
LEB128-decode ×2.

## Recommended remediation (ordered sub-steps)
1. **`ReplaySession` (A2):** one engine — connect → drain initial →
   `replay_setup(retargets)` → `replay_block(lo, hi, frame_fn) -> responses` —
   plus a small `ReplayOp` spec (template, retarget fn, verdict fn). Each
   operation becomes ~10 lines. **Reuse the single receive point
   `transport.py::read_protocol_available` delivered by CR-04** — do not
   reintroduce an idle-gap loop; collapse `session.read_available` /
   `native_mutation._read_available` (now thin delegators) into it. Split the
   file into `write_templates.py` (derive/*Template), `replay.py` (engine),
   `splices.py`, `list_reads.py`.
2. **Extract protocol from `mcp_server.py` (A1):** `protocol/introspection.py`
   (splice header, descriptor/window-list/value-read sweeps, `_open_form_by_link`,
   `_read_field_value`) and `protocol/foreground.py` (`_foreground_form_by_link`,
   bare-create open). Tool functions shrink to arg plumbing + result shaping; keep
   the agent-facing docstrings on the tool wrappers.
3. **Versioning module (A5):** move `active_version_key` /
   `detect_live_platform_version` into a leaf `qa_mcp/versioning.py` (or `_bundled`);
   `regression.versioning` re-exports. Lazy imports become normal top-level imports.
4. **`Settings` (A6):** one `qa_mcp/config.py` `Settings.from_env()` documenting
   every `QA_MCP_*` var; modules take a `Settings` / call one accessor. De-dup the
   remote-client parse and ODATA defaults. Also unifies the version-injection
   helper used by both `bootstrap_synth` and `_foreground_form_by_link`.
5. **Dead-code / dedup sweep:** delete the unused/dead items above and collapse
   the duplicated helpers.

## Acceptance
- **No behavior change:** the full `uv run pytest -q` suite (and, where a client
  is available, the live-regression) passes **unchanged** after each sub-step;
  MCP tool count stays 63 and `verify_protected_image.py` still passes.
- `native_write.py` no longer contains 14 copies of the replay loop — the replay
  operations are expressed via one `ReplaySession`/`ReplayOp`; measured line
  reduction recorded in `## Result`.
- `mcp_server.py` no longer opens raw sockets or builds wire frames; that code
  lives under `protocol/` (`introspection.py`, `foreground.py`); `rg 'create_connection|GuidRebinder' src/qa_mcp/mcp_server.py` returns nothing.
- `active_version_key` is imported top-level (no lazy import comments referencing
  the cycle) from a leaf module; `regression.versioning` re-exports for
  compatibility.
- Every `QA_MCP_*` var is read through `Settings`/one accessor and documented in
  one place; `QA_MCP_REMOTE_CLIENT` parsing and ODATA defaults exist once.
- Dead code removed: `rg '_RESOLVE_SF_RE|_CreateForegroundHold|_OPEN_LINK_LABEL_ALIASES'`
  returns nothing (`create_splice` was already removed by cr-03). **Keep
  `_splice_window_activate_command`** — it is now LIVE (cr-03 retry). `mutation.py`
  is removed or renamed only after confirming `native_mutation` is not on a live
  path (it still imports `render_write_frame`).
- Each sub-step is its own commit/change so it can be reviewed and reverted
  independently.

## Change Set

1. `native-write-replay-session` - shared replay engine for native write/list/dialog/window operations.
2. `mcp-server-protocol-extraction` - move protocol wire helpers out of `mcp_server.py`.
3. `qa-mcp-versioning-leaf` - move platform version policy to a cycle-free leaf module.
4. `qa-mcp-settings-accessor` - centralize `QA_MCP_*` parsing and duplicated defaults.
5. `protocol-dead-code-dedup` - remove verified-dead helpers and exact duplicate utilities.

## Change 1: `native-write-replay-session`

### Why

The native replay operations repeat socket/setup/rebind/observe loops, so fixes
to send, receive and verdict behavior can drift across operations.

### Goal

Introduce one `ReplaySession`/`ReplayOp` engine that preserves existing native
operation results while reusing `read_protocol_available`.

### Scope

- Add shared replay orchestration under `src/qa_mcp/protocol/`.
- Convert native write/list/dialog/window operations to the shared engine.
- Preserve CR-03/CR-04 retarget, read-back, send-timeout and receive semantics.

### Acceptance

- `uv run pytest -q` passes.
- Converted replay paths use `read_protocol_available`; no new idle-gap receive
  loop is introduced.
- Existing structured `retarget_failed`, `committed`, `send_timeout` and
  divergence result shapes are preserved.

### Depends On

- CR-03 and CR-04 archived.

### Related

- `openspec/changes/native-write-replay-session/`

### Notes For `$openspec-ff-change`

- Use the existing proposal/design/spec/tasks artifacts; do not re-plan this
  change unless implementation discovers a contradiction.

## Change 2: `mcp-server-protocol-extraction`

### Why

`mcp_server.py` still owns raw socket and frame-rebinder protocol code that
belongs under `protocol/`, making the MCP boundary too broad.

### Goal

Extract foregrounding, introspection and read-sweep wire helpers to protocol
modules while preserving tool wrappers and endpoint behavior.

### Scope

- Add `protocol/introspection.py` and `protocol/foreground.py`.
- Move protocol helpers out of `mcp_server.py`.
- Keep MCP docstrings, `@testclient_tool`, `_values_equivalent`,
  activation retry and structured result behavior intact.

### Acceptance

- `uv run pytest -q` passes.
- `rg 'create_connection|GuidRebinder' src/qa_mcp/mcp_server.py` returns no matches.
- Tool count remains 63 and protected-image/tool-surface checks still pass.

### Depends On

- Change 1.

### Related

- `openspec/changes/mcp-server-protocol-extraction/`

### Notes For `$openspec-ff-change`

- The artifacts are apply-ready; implementation should move behavior without
  broad tool-surface rewrites.

## Change 3: `qa-mcp-versioning-leaf`

### Why

Protocol code imports version policy lazily from `regression.versioning` to
avoid an import cycle, leaving a protocol dependency in the wrong package.

### Goal

Move version-family selection into `qa_mcp.versioning` and keep
`regression.versioning` as a compatibility re-export.

### Scope

- Add the leaf module.
- Update protocol imports to top-level `qa_mcp.versioning` imports.
- Preserve existing `_bundled/<family>/` selection behavior.

### Acceptance

- `uv run pytest -q` passes.
- Protocol modules no longer need lazy imports from `regression.versioning`.
- Existing callers of `regression.versioning.active_version_key` still work.

### Depends On

- none

### Related

- `openspec/changes/qa-mcp-versioning-leaf/`

### Notes For `$openspec-ff-change`

- Keep the change compatibility-focused; do not introduce a new platform family.

## Change 4: `qa-mcp-settings-accessor`

### Why

`QA_MCP_*` values are parsed at scattered call sites, causing duplicated truth
parsing and duplicated OData defaults.

### Goal

Add `qa_mcp.config.Settings.from_env()` and migrate environment parsing through
one documented accessor without changing defaults.

### Scope

- Add settings module/tests.
- Centralize `QA_MCP_REMOTE_CLIENT` truth parsing.
- Centralize OData defaults used by `data/odata.py` and regression CLI code.
- Migrate remaining scattered `QA_MCP_*` reads where appropriate.

### Acceptance

- `uv run pytest -q` passes.
- `rg 'QA_MCP_' src/qa_mcp` shows remaining direct reads are centralized or
  explicitly justified.
- Remote-client local-only behavior and OData defaults are unchanged.

### Depends On

- none

### Related

- `openspec/changes/qa-mcp-settings-accessor/`

### Notes For `$openspec-ff-change`

- The new `qa-mcp-runtime-configuration` capability is intentional because this
  change adds an observable configuration contract.

## Change 5: `protocol-dead-code-dedup`

### Why

After the structural slices land, the remaining dead helpers and exact
duplicates can be removed with lower risk and clearer source-search evidence.

### Goal

Remove only verified-dead helpers and collapse duplicate utilities when tests
prove behavior-equivalence.

### Scope

- Delete `_CreateForegroundHold`, `_RESOLVE_SF_RE` and `_OPEN_LINK_LABEL_ALIASES`
  if current source searches still prove them dead.
- Keep `_splice_window_activate_command`; it is live through the CR-03 retry.
- Leave `mutation.py` unless `native_mutation` is proven no longer live.
- Collapse exact duplicate helpers with tests.

### Acceptance

- `uv run pytest -q` passes.
- `rg '_RESOLVE_SF_RE|_CreateForegroundHold|_OPEN_LINK_LABEL_ALIASES'` returns
  no matches.
- Live helper and `mutation.py` decisions are recorded in result notes.

### Depends On

- Changes 1-4.

### Related

- `openspec/changes/protocol-dead-code-dedup/`

### Notes For `$openspec-ff-change`

- Do not treat the original dead-code list as authoritative; verify against the
  current post-CR-03/CR-04 code.

## Suggested change decomposition (for `$opsx-ff`)
Map one change per sub-step above (Change 1 = ReplaySession, … Change 5 =
dead-code sweep). Land in order; each keeps the suite green. This is a large card
— `$opsx-ff` may split it into multiple cards if a single session per sub-step is
preferred.

## Verify
- `uv run pytest -q` after each sub-step; final run passed (`671 passed`).
- `openspec validate --all --strict` passed after spec sync/archive.
- `git diff --check` passed.
- Live regression was not run; all CR-08 changes are offline Python refactors
  with no new protocol claims or 1C metadata changes.

## Related
- `docs/code-review-2026-07-02.md` (A1, A2, A5, A6)
- Memory: surpass-vanessa goal (card 111 item 5, "gated on real need").
- **Depends on:** CR-03 (S2 dead branch), CR-04 (frame-aware receive to preserve),
  CR-05 (the `@testclient_tool` decorator), CR-07 (CI as the safety net).
- Publish commit: this CR-08 publish commit (`Refactor QA MCP protocol architecture`).

## Result
OpenSpec artifacts prepared for five ordered architecture-refactor changes:
`native-write-replay-session`, `mcp-server-protocol-extraction`,
`qa-mcp-versioning-leaf`, `qa-mcp-settings-accessor` and
`protocol-dead-code-dedup`. Change 1 archived as
`openspec/changes/archive/2026-07-02-native-write-replay-session/`.
Change 2 archived as
`openspec/changes/archive/2026-07-02-mcp-server-protocol-extraction/`.
Change 3 archived as
`openspec/changes/archive/2026-07-02-qa-mcp-versioning-leaf/`.
Change 4 archived as
`openspec/changes/archive/2026-07-02-qa-mcp-settings-accessor/`.
Change 5 archived as
`openspec/changes/archive/2026-07-02-protocol-dead-code-dedup/`.
Measured CR-08 replay-engine result: the publish diff reduced
`src/qa_mcp/protocol/native_write.py` from 2729 lines at pre-CR-08 commit
`e9d60ad` to 2701 lines in CR-08 commit `bff3267` while adding the shared
`src/qa_mcp/protocol/replay.py` engine. Later post-delivery read-back scanner
tail cleanup intentionally adds native-write coverage and lines outside the
CR-08 reduction metric.

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (A1, A2, A5, A6; roadmap-111 item 5).
- 2026-07-02 `$opsx-ff`: decomposed into five ordered OpenSpec changes and
  prepared proposal/design/spec/tasks artifacts with 1C verification matrix rows.
- 2026-07-02 `$opsx-do`: moved card to `3.inprogress` and started Change 1.
- 2026-07-02 `$opsx-do`: implemented and archived
  `native-write-replay-session`; full offline pytest passed (`662 passed`).
- 2026-07-02 `$opsx-do`: implemented and archived
  `mcp-server-protocol-extraction`; full offline pytest passed (`663 passed`),
  tool-surface check passed, and
  `rg "create_connection|GuidRebinder" src/qa_mcp/mcp_server.py` returned no
  matches.
- 2026-07-02 `$opsx-do`: implemented and archived
  `qa-mcp-versioning-leaf`; focused versioning/bootstrap tests passed (`44
  passed`) and full offline pytest passed (`665 passed`).
- 2026-07-02 `$opsx-do`: implemented and archived
  `qa-mcp-settings-accessor`; focused settings/guard tests passed (`42
  passed`) and full offline pytest passed (`670 passed`).
- 2026-07-02 `$opsx-do`: implemented and archived
  `protocol-dead-code-dedup`; focused cleanup tests passed (`54 passed`), the
  dead-symbol `rg` check returned no matches, and full offline pytest passed
  (`671 passed`).
- 2026-07-02 `$opsx-pub`: no separate durable docs update was needed beyond
  synced OpenSpec specs and this board result; proceeding with scoped publish.
- 2026-07-02 `$opsx-pub`: committed in this CR-08 publish commit (`Refactor QA
  MCP protocol architecture`).
- 2026-07-02 tail cleanup: added direct offline coverage for extracted
  `protocol.foreground` and `protocol.introspection` helper contracts
  (`tests/test_protocol_extracted_helpers.py`) and re-ran the related
  native/introspection slice (`120 passed`).
