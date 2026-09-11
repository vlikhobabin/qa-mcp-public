# Genuine multi-action capture (2026-06-17)

The decisive unblock for the capture-coverage wall (cards 86c/86d/86e/88): a genuine capture of NEW action
families, recorded with the proven Vanessa-through-tcpdump recipe (NOT a proxy — the genuine manager launches
its own client on its own TPort).

## Recipe (reproducible)

1. Boot the genuine Vanessa TestManager (Xvfb :77, MCP :9874): `vanessa-mcp/bin/start-vanessa-manager.sh`
   + `tools/protocol-research/vanessa_auto_allow_dialogs.sh :77 80 &` (clears the 3 security modals → 27 tools).
2. Stop apache2 (vanessa_client version contention), keep `vanessa_auto_allow_dialogs.sh :77` running (the
   launched client raises its own dialogs).
3. `sudo tcpdump -i lo -U -w capture.pcap 'tcp portrange 48000-48400'` BEFORE connecting (Vanessa picks a port
   in that range — observed 48001).
4. Drive `tools/protocol-research/qa-multiaction-capture.feature` via the manager MCP:
   `vanessa_mcp_call.py run_scenario '{"filePath":"…/qa-multiaction-capture.feature","mode":"all"}'`
   (connect-with-params table step + open the fixture processor + a chain of UI actions; each input is
   followed by another action so the prior input COMMITS — its genuine SET/command is captured).
5. Discover the client port (`ss -tn | grep :480`), stop tcpdump, restart apache2.
6. `pcap_to_traffic.py capture.pcap <client_port> runtime/protocol-research/captures/<name>`.

## Result — `genuine-multiaction-20260617` (107 mgr frames)

The scenario reached the page actions and FAILED at `в поле с именем 'PF_PAGE_B_FIELD' я ввожу текст …` with
*«Неподходящий тип элемента управления для вызванного действия»* — PF_PAGE_B_FIELD is not a plain text input
(a control-type nuance, not a capture failure). Everything BEFORE it executed and was captured:

| captured | frames | unblocks |
|---|---|---|
| `PF_EDIT_DATE` input (value `17.06.2026`, "ввожу текущую дату") | 4 (incl. SET ×2) | **date commit (86c)** — derive a date template + commit-partner, like the number |
| `PF_EDIT_NUMBER` input (`654,32`) | 2 | re-confirms number |
| `PF_EDIT_STRING` input (`MULTICAP`) | 2 | re-confirms string |
| page-SWITCH to `Group[PF_PAGE_B]` | 11 | **page activation (86d)** — decode the switch command; then the page's fields become editable |

So we now hold genuine command frames for the DATE type and the PAGE-SWITCH action — both previously
unavailable. The page-target kinds in commands are `EditField` and `Group` (a page is `Group[PF_PAGE_x]`).

## Next (decode, each its own step — same pattern as the number)

- **date commit:** `write_form_value(field='PF_EDIT_DATE', base_field='PF_EDIT_DATE', captured_value='17.06.2026',
  capture='genuine-multiaction-20260617', commit_partner='PF_EDIT_NUMBER', commit_partner_value='654,32')`
  (the date input is followed by the number input in the capture → a genuine focus-change may already exist).
- **page-switch:** decode the `Group[PF_PAGE_B]` switch command structure (the 11 PF_PAGE_B frames) → synthesize
  a page-activate; then re-test the cross-group write to a now-active page field (86b/86d).
- **checkbox / open_list / tables:** still not captured — no "флажок" step phrasing surfaced; the fixture is a
  processor (no list); table input needs the table-cell step. A richer fixture or more step research needed.

## UPDATE — re-capture with read sweep + DATE COMMIT proven

The first capture lacked read-back frames (no post-input read sweep), so a commit could be performed but not
verified. Re-captured with the same recipe + a `get_form_analysis` MCP call AFTER the feature (it drives a
read sweep over the wire → read-back frames). Two fixes were needed:
1. The feature dropped the failing tab-page FIELD inputs (kept the page-SWITCHes); it then ran fully green.
2. **pcap mixing:** the manager opened SEVERAL connections to the client (probe + real); `pcap_to_traffic`
   merged them by client_port → the replay desynced (two handshakes → ConnectionReset). Fixed by passing the
   4th arg `manager_port` = the DOMINANT manager-side ephemeral port (found via
   `tcpdump -r cap.pcap -nn 'port 48001' | grep -oE '127.0.0.1\.[0-9]+' | sort | uniq -c`). Here 57312 (957
   packets) vs noise (57304/57298/57284). → clean single-connection capture `genuine-multiaction-clean-20260617`
   (361 frames, single handshake).

**DATE COMMIT proven LIVE via the MCP tool** (clean capture; the date input is followed by the number activate
= a genuine focus-change, so `derive_write_template` needs no commit-partner):
`write_form_value('25.12.2027', field='PF_EDIT_DATE', base_field='PF_EDIT_DATE',
capture='genuine-multiaction-clean-20260617', captured_value='17.06.2026',
default_value='15.01.2026 10:30:00')` → readback `'25.12.2027 0:00:00'`, **committed=true**. (The commit check
in `NativeWriteSession.write` was made prefix-tolerant: a date field reads back WITH a time component, so
`readback.startswith(value)` — a non-commit reads back the old value and fails the prefix.)

So card-86c per-type commit now covers **string + number + date**. checkbox/choice/open_list/tables still need
their genuine SETs → card 90 (richer fixture). Recommended canonical capture: `genuine-multiaction-clean-…`
(remember the manager_port filter when converting).

## Cleanup

Manager (1cv8 /TestManager), client (1cv8c), and Xvfb :77 are stopped after the capture; apache2 restarted
(OData 200). The capture bytes live under gitignored `runtime/`; this doc + the `.feature` are the tracked,
reproducible recipe.
