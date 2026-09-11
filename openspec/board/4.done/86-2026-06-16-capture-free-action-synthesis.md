# 86. ⭐ KEYSTONE — capture-free action synthesis for arbitrary forms

## Status
4.done

## Order Index
86

## Owner
unassigned

## OpenSpec Stage
epic

## Source
- 2026-06-16: roadmap card 82, stage 4 — THE central research→product gap. Today every read/click/write needs
  a genuine CAPTURE of that exact flow as a template (`run_scenario` takes capture_dir + manager_templates;
  actions go through an `action_resolver` fed by captures; `native_write` needs a per-field INPUT capture).
  Vanessa needs no per-flow capture — the platform `ТестируемоеПриложение` engine synthesizes the input/click
  from the form's live state/metadata.

## Summary
Generate the native protocol commands (activate / set-value+commit / click / navigate) for ANY form element,
addressed by NAME/path, WITHOUT a per-flow capture — the single biggest blocker to general real-config
testing. Either (a) decode the protocol's general addressing of form elements + command structure so commands
are built from the live form descriptor (read via the existing introspection), or (b) an auto-capture-once-
per-element-kind scheme that `derive_*` then parameterizes.

## Acceptance
- A scenario can input/click/write an element identified by NAME on a form for which NO bespoke capture was
  authored, and it commits/acts live (read-back verified), on a real config beyond the fixture.
- The command builder is driven by the live form descriptor (element id/path/type) + a small per-element-TYPE
  template set, not a per-FLOW capture.
- Documented protocol model: how a form element is addressed and how each command (activate/set/commit/click)
  is structured + which fields are session-derived (GUIDs/seq) vs static.

## Spike (step 0) — DONE 2026-06-16: element addressing decoded

The central unknown ("how does a command address its target element?") is **resolved from existing captures**
(no new genuine runs). Evidence: `docs/protocol-research/evidence/card86-element-addressing-spike-2026-06-16/`,
reproduce with `tools/protocol-research/element_addressing_spike.py`.

- In `genuine-commit-conn` the single-field command frames cover **41 distinct fields**; diffing two
  equal-length, same-type frames for different fields (`PF_EDIT_STRING` vs `PF_EDIT_NUMBER`) differs in **only
  3 ranges**: the offset-19 counter, the 16-byte nonce, and the **element name** — nothing else.
- **An element is addressed by a length-prefixed hierarchical path string** (latin1): `<0x9a><len:1>` then
  `SecondaryFrame[S].ManagedForm[F].Group[…].EditField[NAME]`. **No hidden per-element id/GUID.**
- Every component is already in hand: S/F GUIDs from the handshake (`GuidRebinder`), the group-path + name
  from `read_form_summary` introspection, the 1-byte length recomputed like `native_write` does for the value.
- Consequence: **strategy (b) (per-element-TYPE template + live address) is nearly a straight shot** and (a) is
  within reach. A command frame = [static per-type structure] + [length-prefixed element path] +
  [optional length-prefixed value] + [session header + GUIDs] — all four now understood.

## Refined decomposition (split into `2.todo` as 86a..86e)

- **86a `ElementRef` + path builder** (foundation) — ✅ **DONE (offline + live, 2026-06-16).**
  `src/qa_mcp/protocol/element_ref.py`: `ElementRef`/`build_element_path`/`extract_element_paths`/
  `retarget_element_path`/`retarget_element_leaf` (length-prefixed path retarget). 8 offline tests (incl. a
  real capture frame). Hook wired into `SessionHandle.read_form_value` (`frame_rewriter`, post-rebind).
  **Live proof** (`element_addressing_read_probe.py`): read PF_EDIT_NUMBER/DATE/READONLY by re-targeting the
  path leaf of one PF_EDIT_STRING value-read frame — each returned its OWN live value, value-mode flipped to
  the addressed field, no per-field capture. Caveat: making `read_form_value` itself run live needs the
  value-read frames sourced from the capture (218..221 aren't in the 8..106 template set) — small follow-up.
- **86b set-value+commit (`input_text`) capture-free** — ✅ **addressing DONE (offline + live, 2026-06-17);
  commit: same-type DONE, cross-type/cross-group deferred.** `build_write_frame` +
  `NativeWriteSession.write(value, field=…)` apply `retarget_element_leaf` to the write block; runner
  `run_write_scenario(base_field=…)` writes each step to its own `step.marker`; MCP `write_form_value`/
  `write_form_values`/`run_write_scenario_tool` gain `base_field`. Live (one session): write-ADDRESSING proven
  (each field's read-back returns its OWN value, no per-field capture); COMMIT proven for the template TYPE
  (string); read-only correctly not modified; session robust after a non-commit. Boundaries (→ other stories):
  cross-TYPE commit (number/date) needs per-element-TYPE SET templates (86c/88); the only other writable string
  field is on a tab page → needs navigation (86d). Evidence:
  `docs/protocol-research/evidence/card86b-capture-free-write-2026-06-17/`.
- **86c click (`click_button`) capture-free**: per-type button template + `ElementRef(button)`.
- **86d navigate** — ✅ **page-SWITCH DONE (decoded + synthesized + LIVE-verified, 2026-06-17); open_list
  pending a genuine list capture (card 90).** (a) nav-link length framing `<0xf7><char-count:1><utf-16le link>`
  → `navigation.retarget_nav_link` (variable-length) + 2 tests. (b) **page-SWITCH:** from
  `genuine-multiaction-clean-20260617`, switch→B vs switch→A differ in only counter/nonce/page-name → a switch
  = the genuine switch frame with its page-`Group` leaf re-targeted (`retarget_element_leaf(kind="Group")`).
  LIVE via screenshots (card 85): default→genuine-B→synth-A, md5 shows B changed the render and synth-A is
  BYTE-IDENTICAL to default-A (`page_switch_probe.py`). **PRODUCTIZED ✅:** `derive_page_switch` +
  `switch_page` (standalone) + `NativeWriteSession.switch_page` + MCP tool `switch_page` (11 tools) + Gherkin
  «я перехожу к закладке с именем 'X'» → `switch_page` step kind + runner routing in `run_write_scenario`;
  +2 tests (full suite 208). Live via MCP: `switch_page('PF_PAGE_A', base_page='PF_PAGE_B')` → accepted=true.
  open_list still needs a genuine `e1cib/list/…` capture (fixture is a processor → card 90). Evidence:
  `docs/protocol-research/evidence/card86d-{navigation,page-switch}-2026-06-17/`.
- **86e tables / row-select** (overlaps card 88): defer or thin.

## Change Set
- (spike) `tools/protocol-research/element_addressing_spike.py`,
  `docs/protocol-research/evidence/card86-element-addressing-spike-2026-06-16/findings.md`.
- (86a) `src/qa_mcp/protocol/element_ref.py` (NEW), `src/qa_mcp/protocol/session.py` (frame_rewriter hook +
  read_form_value addressing), `tests/test_element_ref.py` (NEW, 8),
  `tools/protocol-research/{element_addressing_read_probe.py,run_addressing_read_test.sh}` (NEW).
- (86b) `src/qa_mcp/protocol/native_write.py` (`build_write_frame`, `NativeWriteSession.write(field=…)`),
  `src/qa_mcp/scenario/runner.py` (`run_write_scenario(base_field=…)` + per-step marker), `mcp_server.py`
  (`base_field` on the write tools), `tests/test_native_write.py` (+3) & `tests/test_scenario_runner.py` (+1),
  `tools/protocol-research/{element_write_86b_probe.py,element_write_crossgroup_probe.py,run_86b_write_test.sh}`,
  `docs/protocol-research/evidence/card86b-capture-free-write-2026-06-17/findings.md`.
- (per-type SET investigation + number-commit BREAKTHROUGH) `tools/protocol-research/element_write_86c_diag.py`,
  `tools/protocol-research/element_write_number_probe.py`,
  `docs/protocol-research/evidence/card86c-per-type-set-investigation-2026-06-17/findings.md`.
- (86d) `src/qa_mcp/protocol/navigation.py` (`retarget_nav_link`), `tests/test_navigation.py` (+2),
  `docs/protocol-research/evidence/card86d-navigation-2026-06-17/findings.md`.

## The recurring wall (2026-06-17) — the decisive unblock for 86c/86d/86e + card 88

Element ADDRESSING (86a/86b) was fully derivable because the read sweep + one input covered every element.
But each per-ACTION command structure is its own wire shape and needs a genuine example: per-type SET (number/
date/checkbox), page-switch, open-list, table ops. **The single-flow lab capture (open processor → read all →
type into PF_EDIT_STRING) has been mined for everything it offers.** The decisive next step is ONE genuine
MULTI-ACTION capture: drive the genuine Vanessa TestManager THROUGH `protocol_proxy.py` (`capture_session.sh`)
to input a number/date/checkbox, switch a page, click a button, open a list, edit a table row — that single
session unblocks 86c, 86d, 86e and card 88 at once. Infra exists (`capture_session.sh`, `protocol_proxy.py`,
`vanessa_mcp_call.py`, memory `vanessa-mcp-linux-genuine-manager`).

### DONE (2026-06-17): genuine multi-action capture taken → `genuine-multiaction-20260617`

Actual method was Vanessa→**tcpdump** (not proxy: the manager launches its own client on its own TPort 48001),
driven by `tools/protocol-research/qa-multiaction-capture.feature` via the genuine manager's `run_scenario`.
Captured (107 mgr frames): **genuine DATE input** (PF_EDIT_DATE=`17.06.2026`, SET ×2) + **page-SWITCH to
`Group[PF_PAGE_B]`** (11 frames) + number/string re-confirm. The scenario failed at the page-field input
(`PF_PAGE_B_FIELD` is not a plain text control — control-type nuance), so checkbox/open_list/tables remain
uncaptured (no "флажок" step; fixture is a processor; table needs the table-cell step) → **tracked as card 90**
(extend the fixture or add a new focused one — the current one is overloaded). Recipe is reproducible
(boot manager → tcpdump → run feature → pcap_to_traffic). Evidence:
`docs/protocol-research/evidence/genuine-multiaction-capture-2026-06-17/`.

**DATE COMMIT ✅ proven (2026-06-17):** re-captured with a post-input `get_form_analysis` (adds read-back
frames) → `genuine-multiaction-clean-20260617` (pcap had MIXED connections; isolated with `pcap_to_traffic`'s
4th `manager_port` arg = dominant port 57312). LIVE via MCP: `write_form_value('25.12.2027',
field='PF_EDIT_DATE', base_field='PF_EDIT_DATE', capture='genuine-multiaction-clean-20260617',
captured_value='17.06.2026', …)` → readback `'25.12.2027 0:00:00'`, committed=true (commit check made
prefix-tolerant for date's time component). **Per-type commit now covers string + number + date.** Next:
decode the page-SWITCH command (the 11 `Group[PF_PAGE_B]` frames); checkbox/choice/list/tables → card 90.

## Per-type SET — investigation + BREAKTHROUGH (2026-06-17): number COMMITS from the existing capture

Investigated capture-free COMMIT for non-string types. First (wrong) read: reusing the **string** SET (16-wide
buffer) for a number never commits — concluded "needs new per-type captures." **That conclusion was an artifact**
(like card 80's "off-wire wall"). The genuine capture **already contains the genuine PF_EDIT_NUMBER input**
(card 80's two-input feature typed `777,77`, frames 353-356) — uncommitted only because no focus-change followed.

The SET structure is **type-IDENTICAL** (`88 82 81 e0 41 81 81 ba <varint-len> <value> 20 20 20`; variable-
length, not fixed-width). The commit trigger is **universal: "activate ANY other field."** So a number commits
with: setup → activate PF_EDIT_NUMBER + genuine number SET (value retargeted) → activate PF_EDIT_STRING
(synthesized focus-change) → read-back. **Proven LIVE** (`element_write_number_probe.py`): `777,77`→committed,
`555,55` (retargeted, fresh session)→committed. So number is NOT blocked — it works from the existing capture.

Corrected model: per-type commit needs the field's OWN genuine SET (correct buffer) + a synthesized
focus-change — NOT a type-descriptor, and NOT a new capture when the type is already present. number ✅.
date/checkbox/choice still need their genuine SETs (absent here → a genuine multi-action capture / richer
fixture, card 88). **PRODUCTIZED ✅ (2026-06-17):** `WriteTemplate.commit_block` +
`derive_write_template(commit_partner_field, commit_partner_value)` + `NativeWriteSession.write` (write-block →
commit-block → read). LIVE via MCP: `write_form_value('314,15', field='PF_EDIT_NUMBER', base_field=
'PF_EDIT_NUMBER', captured_value='777,77', commit_partner='PF_EDIT_STRING', commit_partner_value=
'QAGENUINE2026')` → committed=true, readback='314,15'. +1 derive unit test (full suite 206). number commit is
a product feature now; other types await their genuine SETs.

## Notes / risks
- Builds on the proven pieces: live read (card 79), value-write+commit (card 80), nav/click replay (card 74),
  GUID rebind + offset-19 counter handling. ~~The open question is GENERAL element addressing without a
  capture.~~ **RESOLVED by the spike** — addressing is the length-prefixed element path string.
- Remaining (smaller) unknowns: confirm the same path addressing on activate/SET/click/navigate families;
  per-element-TYPE structure templates (one genuine example each); element path shapes for non-EditField
  types (TableBox/Column, CommandBar, choice, pages); the cross-FORM axis (all current captures are the one
  fixture form — confirm with a real config under card 88).

## Related
- cards 71 (api coverage limitations), 72 (phase-3 readonly buildout), 76 (raw-API session-id synth), 77
  (agent_runtime parity), 80 (Fork-2 write), `src/qa_mcp/protocol/{navigation,native_mutation,native_write}.py`,
  `src/qa_mcp/scenario/actions.py`.

## Log
- 2026-06-16T00:00:00Z card created.
- 2026-06-16: step-0 addressing spike DONE (no new captures) — element address = length-prefixed path string
  `…EditField[NAME]`, no hidden id/GUID; the keystone unknown is resolved. Evidence doc + reproducible tool
  added. Refined into sub-stories 86a..86e; (a)/(b) decided toward (b) with (a) accreting.
- 2026-06-16: 86a DONE (offline + LIVE). element_ref.py (path builder + length-prefixed retarget) + 8 tests;
  read_form_value frame_rewriter hook. Live: read 3 fields capture-free by path-leaf substitution, each its
  own value, value-mode flipped — capture-free addressing proven live. Full suite 199 passed.
- 2026-06-17: 86b — write-ADDRESSING DONE (offline + LIVE), same-type COMMIT DONE. build_write_frame +
  NativeWriteSession.write(field=) + runner/MCP base_field; +4 tests (full suite 203). Live one-session proof:
  every field addressed (read-back = its own value), string commit works, readonly not modified, session
  robust. Cross-TYPE commit (number) → per-type SET templates (86c/88); tab-page string field → navigation
  (86d). Honest: a different-field *commit* needs those follow-ups; addressing now spans read+write.
- 2026-06-17: per-type SET investigated (for non-string commit). Decisive: SET tag is type-agnostic (number
  accepts the `ba` edit-text) but the value buffer is type-specific + baked into the captured frame — the
  string SET can't be reformatted for a number (no value format commits). ⇒ needs genuine per-type INPUT
  captures (card 88 scope); cheap path ruled out. Evidence card86c-…; diagnostic tool added.
- 2026-06-17: 86d — nav-link length framing decoded (`<0xf7><char-count:1><utf-16le link>`) →
  `retarget_nav_link` (variable-length) + 2 tests (full suite 205). open_list & page-switch live-BLOCKED: lab
  has no genuine list/page-switch capture. Surfaced the recurring wall: 86c/86d/86e + card 88 all need a
  genuine MULTI-ACTION capture (Vanessa-through-proxy) — the single decisive unblock. Evidence card86d-…
- 2026-06-17: 86c BREAKTHROUGH — number COMMITS from the EXISTING capture (corrects the earlier "blocked"
  read). The genuine PF_EDIT_NUMBER SET was already captured (card 80 two-input feature); SET structure is
  type-identical; commit = genuine per-type SET + synthesized focus-change (activate any other field). LIVE:
  777,77 & 555,55 (retargeted) both commit. number not blocked. Probe added; per-type SET productization
  (commit-partner in NativeWriteSession) is the next step; date/checkbox still need their genuine SETs.
