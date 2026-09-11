# Card 98 #2 — get_window_list_testclient: genuine-manager capture → decode → splice replay → SHIPPED

**Date:** 2026-06-20. **Result:** the protocol-level 1C window list is **built, tested and live-verified** — the
vanessa-mcp `get_window_list_testclient` equivalent, capture-free, no Vanessa. **45 MCP tools, 315 tests.** This
completes the change-2 window-enumeration item (the OS-level `get_window_list` shipped earlier lists OS windows;
this lists the 1C-internal windows/tabs — distinct capability, see card98-window-enumeration-2026-06-20).

## Capture (genuine Vanessa manager)

Followed the manager-capture recipe ([[vanessa-mcp-linux-genuine-manager]], [[genuine-action-capture-recipe]]):
booted the genuine Vanessa TestManager (Xvfb :77, MCP :9874, auto-allow the security modals → full 27 tools),
connected a TestClient and opened several tabs (`run_scenario` on `qa-card98-windowlist-capture.feature` →
fixture form + Товары list), found the manager↔client ports (client 48001, manager 48176 via `ss`), `tcpdump`'d
the `get_window_list_testclient` call, `pcap_to_traffic.py … 48001 … 48176`. Vanessa returned **4 windows**
(Товары / QA MCP Protocol Fixture V1 / Демонстрационное приложение / Начальная страница). Capture:
`runtime/protocol-research/captures/genuine-card98-windowlist-20260620` (gitignored).

## Decode — the response

The query is a **2-frame request** (manager→client: a 4-byte control + two ~100 B command frames); the **2nd
frame's response enumerates every open window**. The response is a sequence of **window records**, each:

```
<Kind>[<guid>]            Kind ∈ SecondaryFrame | MainFrame | HomePage   (ASCII path)
82 <marker> <len> <caption>   window title — marker fa = ASCII (byte len, latin1), f7 = UTF-16LE (char count)
fa <len> <KindStr>            the window kind as a string ("SecondaryFrame" / "MainFrame" / "HomePage")
81 <e1|e2> …                  the nav-ref (e1cib/list/…, e1cib/app/…, e1cib/navigationpoint/…) or empty
```

The caption markers are the **same value-encoding family** as field values (fa/f7 ↔ the fa/97 string envelopes).
NB the window list is keyed by **caption + frame path**, NOT purely by SecondaryFrame (4 windows but only 2
distinct SecondaryFrame GUIDs in the response — the earlier `_all_secondary_frames` guess was wrong). Parser:
`responses.extract_testclient_windows(blob)` → `[{kind, guid, caption}]`, deduped by (kind, guid); decodes the
genuine capture to the exact 4-window Vanessa oracle.

## Replay — the splice (the key)

A **raw replay** of the genuine query frames is **rejected**: the client returns «Сеанс работы завершен
администратором» — it validates the session GUID, and the genuine query carries the genuine-manager session's
GUID. These are binary frame-type ≥ 8 command frames (like the value-read 218-221), so the rebind lives in the
template render path — templatizing them is involved.

**The shortcut that worked:** the value-read frame (218) and the window-list query share the identical header
`… cb 53 81 a3 cb 23 95` then a command body. So **render a value-read frame live** (the engine rebinds the
session GUIDs), keep its header up to + including `cb 23 95`, and **graft the window-list command body** after it
→ a frame with the LIVE session + the window-list command (`native_write.splice_window_list_queries`). The
command body is **session-independent** (its leading 16-byte field is a query-id nonce the client echoes, not
session-validated — proven across a fresh session), so the genuine body is reused verbatim (embedded as
`WINDOW_LIST_QUERY_BODIES`, no capture dependency at runtime). Live-proven: q1 → 1 window, q2 → the full list.

## Productized + live-verified

`get_window_list_testclient` MCP tool (`_read_testclient_windows`): open the fixture form (so windows exist) →
render a live value-read header → send both spliced query bodies → decode with `extract_testclient_windows`.
Live (fresh /TESTCLIENT, `get_window_list_testclient_verify.py`): **3 windows** — SecondaryFrame "QA MCP
Protocol Fixture V1", MainFrame "Демонстрационное приложение", HomePage "Начальная страница" → PASS. (3 not 4 —
no Товары list opened in the one-shot session; the genuine 4-window capture had the list open.)

SCOPE (honest): like `read_form_descriptor`, each MCP call is a FRESH session, so it lists the windows of the
session it opens (fixture form + desktop + home); windows opened by SEPARATE MCP calls are in closed sessions.

## Artifacts

- Code: `src/qa_mcp/protocol/responses.py` (`extract_testclient_windows`, `_window_caption_after`),
  `src/qa_mcp/protocol/native_write.py` (`WINDOW_LIST_QUERY_BODIES`, `splice_window_list_queries`),
  `src/qa_mcp/mcp_server.py` (`_read_testclient_windows`, `get_window_list_testclient` MCP tool #45).
- Tests: `tests/test_window_list.py` (+6: parser synthetic/dedup/empty/genuine-capture, splice). **315 tests.**
- Probes: `windowlist_replay_probe.py` (raw — rejected), `windowlist_splice_probe.py` (the splice — works),
  `get_window_list_testclient_verify.py` (the productized tool — PASS). Capture feature:
  `qa-card98-windowlist-capture.feature`. Parity doc updated.
