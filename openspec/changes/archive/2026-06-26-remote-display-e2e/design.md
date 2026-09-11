## Context

Card 119 proved the model-B TCP protocol path and introduced guard returns for
display-local tools. Card 120's spike proved that Win32 `SendInput` can type
ASCII and Cyrillic into the 1C managed-form field that pure protocol writes
cannot commit. This change proves the integrated product path: Python MCP tool
-> remote backend -> Windows host agent -> visible 1C client.

## Goals / Non-Goals

**Goals:**

- Prove at least one genuine object-attribute commit path or, if lab read-back
  is contended, retain screenshot plus read-only data assertion evidence.
- Prove `capture_screenshot` returns a real PNG from the host-rendered client.
- Smoke the remaining display-subset tools and document unsupported or deferred
  rows with concrete reasons.
- Keep raw runtime output out of git and commit only compact curated evidence.

**Non-Goals:**

- Do not broaden into UIA, self-update or host lifecycle management.
- Do not run business-data mutation outside reviewed test data.
- Do not require a 1C TestManager instance.

## Decisions

- Use the Windows lab host `historical-user@192.0.2.202` and the existing
  `vanessa_client` contour named by the card.
- Prefer evidence families that match the suite matrix: active-window/window
  list, screenshot, scenario log, optional data assertion and cleanup note.
- Treat object-attribute writes as mutation-risk UI evidence. Use the existing
  disposable lab object/form path and record cleanup or residual state.
- If a date-cell or label-write path is blocked by fixture availability, retain
  a provider/project gap row instead of claiming a pass.
- Use the existing `docs/protocol-research/evidence/card120-*` directory
  family for curated summaries and keep raw runtime screenshots/traces under
  ignored artifact/runtime roots unless they are deliberately sanitized.

## Risks / Trade-offs

- Shared Windows desktop contention can make protocol read-back flaky ->
  screenshot and data-layer assertion are accepted proof for the display
  primitive, while commit read-back remains a separate diagnostic.
- Live lab access can be unavailable -> record a runtime gap before execution
  rather than discovering it mid-card.
- Screenshot content may include sensitive UI state -> curate or redact before
  committing evidence.

## Migration Plan

1. Run Linux/offline verification first.
2. Start or attach to the Windows TestClient and host agent.
3. Execute the genuine-input and screenshot checks.
4. Collect compact evidence and update the evidence index/docs.
5. Stop only processes started by this run or explicitly owned by the lab
   workflow.

## Open Questions

- None for v1. Broader automation and self-update are follow-up cards.
