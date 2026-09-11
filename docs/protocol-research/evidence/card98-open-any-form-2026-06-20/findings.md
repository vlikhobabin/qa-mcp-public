# Card 98 change-1 — open-any-form wrapper: navigation PROVEN, navigated-form ManagedForm (F) is the last blocker

**Date:** 2026-06-20. **Result:** the open-any-form wrapper's **navigation half is proven** — the engine opens
an ARBITRARY form by nav-link on a held session (capture-free, screenshot-confirmed) — but full introspection of
the navigated form needs its **ManagedForm GUID (F)**, which the navigate / window-list responses do NOT expose.
This precisely maps the final step. The change-1 generalization CORE (live field enumeration of the OPEN form,
`read_form_descriptor(enumerate_live=True)`) is already shipped; this is the remaining "open any form" layer.

## What's proven (the navigation half)

The genuine open-list **navigate command** (`genuine-card90-openlist`, frames 14-15) shares the `… cb 23 95`
header with the value-read — so it splices onto a live header like the descriptor / window-list queries. On a
held session: open the fixture → render a live header → splice the navigate command with the nav-link retargeted
(e.g. `e1cib/list/Справочник.Товары` → `…Контрагенты`, char-count prefix recomputed) → send. **Live-verified:**

- `get_window_list_testclient` after the navigate lists **`Контрагенты`** as a new SecondaryFrame (alongside the
  fixture form, desktop, home page).
- The screenshot shows the **Контрагенты catalog open as a tab** (Покупатели / Поставщики, columns
  Наименование/Код/Телефон/Факс/Вид цен) — a DIFFERENT form than the captured fixture, opened capture-free.
- The source context is `MainFrame[<desktop-guid>]`; the desktop MainFrame GUID is **stable across sessions**
  (config-level, not per-session), so no MainFrame retarget is needed.

So the engine can **open any form by nav-link** on the introspection session — the navigation primitive works.

## The last blocker — the navigated form's ManagedForm (F)

`read_form_descriptor`'s descriptor query and value-read address the form by `SecondaryFrame[S].ManagedForm[F]`.
For the navigated form:

- **S is available** — `get_window_list_testclient` gives the new window's SecondaryFrame GUID (by caption).
- **F is NOT** — no `ManagedForm[…]` GUID appears anywhere in the navigate ACK (346 B) or the window-list
  response. An **S-only** descriptor query (form path = `SecondaryFrame[S]` only) returns a 38 KB response but it
  carries **no parseable element paths** (degenerate without F). The session DOES learn S.F from responses
  (`session.py` `extract_managed_form_guid` / `extract_secondary_frame_guid`, observed on `run_segment`), but the
  navigate ACK doesn't push the new form's full render, so F is never observed.

**⇒ Final step (scoped):** obtain the navigated form's ManagedForm F — trigger/read the form's full render after
the navigate (Vanessa's get_form_analysis issues additional frames against the freshly-activated form), or decode
a "get active form ref" that returns S.F. With F, the existing `splice_descriptor_query` + value-read sweep
introspect the navigated form directly (the descriptor parser + value-read already generalize). Until then,
`read_form_descriptor(enumerate_live=True)` introspects the form the session opens (the fixture); opening a
different form is proven, reading it back needs F.

## Artifacts

- Probe: `tools/protocol-research/open_any_form_probe.py` (navigate splice + window-list + S-only descriptor +
  F search; screenshot `after_nav.png` under runtime/, not tracked). No production code changed — the navigate
  primitive + the F blocker are characterized; the core generalization (`enumerate_live`) ships as-is. Reuses
  the genuine `genuine-card90-openlist` navigate command.
