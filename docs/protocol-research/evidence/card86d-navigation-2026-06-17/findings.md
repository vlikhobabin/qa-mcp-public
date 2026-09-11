# Card 86d — navigation (findings)

Date: 2026-06-17. Goal: capture-free navigation — open_list for an arbitrary catalog, and page activation
(which would unblock the 86b cross-group write to the tab-page string field PF_PAGE_A_FIELD).

## What the available captures contain

All lab captures are the SAME flow on ONE form (`Обработка.ФикстураПротоколаTestClient`): open the processor,
read every element, type into PF_EDIT_STRING. Concretely (genuine-commit-conn):

- **Nav links:** only `e1cib/app/Обработка.ФикстураПротоколаTestClient` — opening the processor. **No
  `e1cib/list/…`** (the fixture is a data processor, not a list), so there is no genuine open-list command.
- **Pages:** `Group[PF_PAGES_MAIN].Group[PF_PAGE_A]` etc. appear only as value-mode READS (tags `88 81 81 e0/e1`,
  like the field read sweep). The genuine flow **never switched pages** — value-mode reads work on inactive
  pages, so Vanessa read both pages' fields without activating them. **No page-switch command was captured.**
- Button (68×) and Table (40×) also appear, but as single-target reads in the sweep (not action commands).

## Decoded (offline)

The nav-link length framing: `<tag 0xf7><char-count:1 byte><utf-16le link>`. The byte before the 47-char
`e1cib/app/…` link is exactly 47. So a nav link is a length-prefixed (CHARACTER count) UTF-16LE string —
recomputing the count lifts the same-length restriction. Implemented as `navigation.retarget_nav_link`
(variable-length) + 2 offline tests.

## Blocked (needs genuine captures)

- **open_list for an arbitrary catalog** — needs a genuine `e1cib/list/…` open capture to verify live (and to
  confirm the full command structure around the nav link). Not present.
- **page activation** — needs a genuine page-switch command capture. Not present (the flow never switched).

## The recurring wall (strategic)

Element ADDRESSING (86a/86b) was fully derivable because the read sweep + one input covered every element.
But each per-ACTION command structure is its own wire shape and needs a genuine example: per-type SET (86c/88),
page-switch & open-list (86d), table ops (86e). The single-flow lab capture has been mined for all it offers.

**Decisive unblock:** ONE genuine multi-action capture session — drive the genuine Vanessa TestManager THROUGH
`protocol_proxy.py` (`capture_session.sh`) to: input a number/date/checkbox, switch a page, click a button,
open a list, edit a table row. That single capture unblocks 86c, 86d, 86e and card 88 at once. Infra exists
(`capture_session.sh`, `protocol_proxy.py`, `vanessa_mcp_call.py`, memory `vanessa-mcp-linux-genuine-manager`).

## Delivered

`navigation.retarget_nav_link` (variable-length nav retarget, decoded framing) + tests (full suite 205).
The live navigation proofs are deferred to the genuine multi-action capture.
