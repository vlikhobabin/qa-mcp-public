> **✅ UNBLOCKED (2026-06-25) — the earlier "license" failure was a `HOME`-override bug, not a real limit.**
> The 1C software license is per-user under `$HOME/.1cv8/1C/1cv8/conf/*.lic`. The first attempts launched
> `/TestManager` with `HOME` overridden to a scratch dir → the platform looked for the license in the wrong
> place → «Не найдена лицензия» (looked mode-gated, wasn't). Re-run as `lihv` with the real `HOME`: the Vanessa
> TestManager boots on 8.5 — **MCP port up in ~3 s, `Server startup` + `Component connect: success`, no license
> error**. So the genuine 8.5 capture path (Vanessa TestManager + `tcpdump`) is available — capture is the next
> step, not blocked.

## 1. Determine the 8.5 capture path

- [x] 1.1 Probed the Vanessa TestManager on 8.5 (manager-on-Xvfb recipe, 8.5 binary + converted manager
  base). **Result: it RUNS on 8.5** once launched as the licensed user (real `HOME`) — MCP `:9874` up in ~3 s,
  full 27-tool set registered after the auto-allow cleared the security modals. The Vanessa-on-8.5 driver is
  the path (reuse the `genuine-action-capture-recipe`).
- [x] 1.2 Launch the manager DIRECTLY (not via `start-vanessa-manager.sh`, which overrides `HOME` *and*
  hardcodes 8.3 in `config/vanessa-manager.env`): `8.5/1cv8 /TestManager /IBConnectionString File=… /Execute
  <vanessa-automation-single.epf> /C"runMcp;mcpPort=9874;…"` on Xvfb, real `HOME`, with the auto-allow clicker.
  Capture path = native `tcpdump -i lo 'tcp portrange 47000-49000'` (client TPort observed `:48001`).

## 2. Drive one genuine action

- [x] 2.1 Captured the **8.5 equivalent of the bundled `genuine-card98-listform-read`** (a proven corpus
  capture): a connect-with-params `.feature` had the 8.5 manager launch an 8.5 client against
  `/opt/1c-dev/vanessa_client_85`, open the «Товары» list, position the first row and read «Наименование».
  `run_scenario` → **Success**. (Used the real-config list-form, like card-98, rather than the fixture's
  unnamed-column dynlist — same call shape, lower risk.)
- [x] 2.2 One genuine 8.5 manager↔client session captured to a single clean pcap (client `:48001` ⇄ manager
  `:60618`).

## 3. Convert + verify

- [x] 3.1 Converted via `pcap_to_traffic.py <pcap> 48001 <out> 60618` → `traffic.jsonl` (45 records: 24
  manager + 21 client chunks). **Parses with the production `CaptureBootstrap.load`** (24 manager + 21 client
  frames) — same format as the 8.3 corpus.
- [x] 3.2 Retained the sample 8.5 `traffic.jsonl` + pcap + `.feature` as evidence
  (`docs/protocol-research/evidence/card115-8-5-genuine-capture-2026-06-25/`, gitignored). Capture path
  recorded for P2.

## 4. Hand-off to P2

- [x] 4.1 Pipeline PROVEN on 8.5 end-to-end (manager → action → pcap → parseable `traffic.jsonl`). The FULL
  re-capture (handshake + frame templates 8-106 + value-read 218-221 + the 13 action/foreground captures +
  `accepted_mappings`) is P2/card 115, scaling THIS exact path; it drops into `_bundled/8.5/` via the P0
  version-aware resolvers.
