# Card 86d — capture-free page-switch (findings)

Date: 2026-06-17. Decode + synthesize + LIVE-verify a page (tab) switch — a navigation action — from the
genuine multi-action capture `genuine-multiaction-clean-20260617`. Reproduce:
`tools/protocol-research/page_switch_probe.py`.

## Decode (decisive)

The genuine capture has two switch commands: → `Group[PF_PAGE_B]` (frames 30-31) and → `Group[PF_PAGE_A]`
(33-34), both length 259. Diffing switch→B vs switch→A differs in **only 3 ranges**:

| offset | →B | →A | meaning |
|---|---|---|---|
| `[19]` | `ce` | `d1` | offset-19 counter (session) |
| `[70..85]` | 16 bytes | 16 bytes | nonce (session) |
| `[247]` | `42` (`B`) | `41` (`A`) | the page NAME in the element path |

So a page-switch command = **address the target page** (`…Group[PF_PAGES_MAIN].Group[PF_PAGE_X]`) + a fixed
activate structure — the SAME element-path addressing decoded in 86a, on a `Group` leaf. Synthesizing a switch
to any page = the genuine switch frame with its page-`Group` leaf re-targeted:
`retarget_element_leaf(frame, "PF_PAGE_B", "PF_PAGE_X", kind="Group")` (the existing 86a helper, `kind="Group"`).

## Live verification (screenshot, card 85)

Boot the client on an owned display (card 84/85), open the fixture form via the genuine setup replay, then:
default → GENUINE switch-to-B → SYNTHESIZED switch-to-A (retargeted). Screenshot each (md5):

```
0-default      7b3f8507…   (page A, default)
1-pageB        80f34867…   (genuine switch -> B: rendering CHANGED)
2-pageA-synth  7b3f8507…   (synthesized switch -> A: BYTE-IDENTICAL to default A)
```

Decisive: the genuine switch to B changed the render; the **synthesized** switch back to A reproduced the
default page-A render **pixel-for-pixel** (same md5). So the synthesized page-switch correctly activates the
addressed page. (The screenshot also shows the genuine inputs committed — `PF_EDIT_STRING=MULTICAP`,
`PF_EDIT_NUMBER=654,32`, `PF_EDIT_DATE=17.06.2026 0:00:00` — confirming the capture replays faithfully.)

## Result

Page-switch is a **capture-free navigation action**: decoded, synthesizable via `retarget_element_leaf
(kind="Group")`, verified live (A→B→A, B differs, synth-A == default A). This is the 86d navigation primitive.

## Not covered / next

- **open_list** — the fixture is a data processor (no `e1cib/list/…`); nav-link length framing is decoded
  (card 86d `retarget_nav_link`) but a genuine list-open capture is still needed → card 90.
- **Productize:** wire a `switch_page` / navigate action (genuine switch frame + `retarget_element_leaf
  kind="Group"`) into the runner/MCP, like the write path.
- Interacting with a page's FIELDS after switching is still blocked by control type (PF_PAGE_*_FIELD not a
  plain text input) → card 90 (richer fixture).
