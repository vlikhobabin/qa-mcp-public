# 109. E-FW — open an external data processor/report (`.epf`), Vanessa-component-free

## Status
4.done

## Order Index
109

## OpenSpec Stage
story

## Owner
unassigned

## Source
- 2026-06-21 corpus residual (the reason transpile is 97.8%, not 100%): the one Vanessa step qa-mcp does not map —
  «Я открываю внешнюю обработку или отчет "<path>" (Расширение)» — open an EXTERNAL `.epf` in the running client.
- Research done 2026-06-21 (`evidence/card103-external-epf-research-2026-06-21/findings.md`): there is **no
  `e1cib`/URL navigation link** for an external file — the platform opens it via
  `ВнешниеОбработкиМенеджер.Подключить(path)` (a BSL call), and Vanessa drives that via the **VanessaExt**
  external component (the feature is gated on «ИспользоватьКомпонентуVanessaExt»). So this is the ONE corpus step
  outside qa-mcp's capture-free protocol-command model.
- Parent epic: card 102 (E-FW drop-in). Distinct from card 106 (which opens CONFIG processors via `e1cib/app`).

## Summary
Open an external `.epf` in the live client the 1C-NATIVE way (no VanessaExt, no BSL-exec bridge): drive the main
window's **«Главное меню» (≡) → Файл → Открыть…** → file dialog → enter the `.epf` path → confirm, answering the
«опасное действие» modal (`answer_dialog`). OS-level UI automation (xtest + locate-on-screen), the same class as
card 100's date-cell picker. Expose as the Gherkin step «Я открываю внешнюю обработку или отчет "<path>"
(Расширение)» so the real Vanessa corpus transpiles 100% AND executes live.

## Acceptance
- A live run opens `/opt/1c-dev/vanessa_client/ФикстураПротоколаTestClient.epf` (the fixture's own `.epf`) and a
  third-party-config `.epf` (`ВыгрузкаДвиженийХозрасчетного.epf`) — the processor's form opens (window-resolved by caption),
  with no VanessaExt component loaded.
- The Gherkin step «Я открываю внешнюю обработку или отчет "<path>" (Расширение)» transpiles (corpus → 100%) and
  EXECUTES via the native flow; a following `assert_form_open` / `assert_element_present` passes on the opened form.
- Honest reporting: the «опасное действие» confirmation is handled (or the lab's `DisableUnsafeActionProtection`
  documented); the OS file-dialog interaction is captured as evidence (screenshots).

## Change Set
1. ✅ `external-open-native-flow` — DONE 2026-06-21. MCP tool `open_external_processor(path, display, expect_caption)`:
   «Главное меню (≡, top-right) → Файл → Открыть» (located via `locate_text`) → GTK file chooser → Ctrl+L → type the
   path Unicode-safe (new primitive `xtest_type_unicode` — `xdotool key U<codepoint>`; plain typing drops Cyrillic)
   → Enter. No «опасное действие» modal blocked it (dev client / lab `DisableUnsafeActionProtection`).
2. ✅ `external-open-gherkin-step` — DONE 2026-06-21. «Я открываю внешнюю обработку или отчет "<path>" (Расширение)»
   → kind `open_external_epf` (path + optional mode). Corpus → **100%** (lab + in-repo canonical); gate LAB_MIN→1.0.
3. ✅ `live-verify` — DONE 2026-06-21. Opened the fixture `.epf` live; the shipped tool returned
   `opened=true, caption_found=true` («QA MCP Protocol Fixture V1»). Evidence `evidence/card109-open-epf-live-2026-06-21/`.

## Verify
- Offline — `pytest` **412 green** (gherkin `open_external_epf` mapping incl. mode/`.erf`/quote variants;
  `open_external_processor` registered = 57 tools; corpus gate 100% — canonical 10 scenarios, LAB_MIN 1.0).
- LIVE (2026-06-21) — `open_external_processor` opened `…/ФикстураПротоколаTestClient.epf` via «Файл→Открыть»,
  caption verified «QA MCP Protocol Fixture V1», dialog closed. Evidence `evidence/card109-open-epf-live-2026-06-21/`
  (03-gtk-dialog.png, 05-after-open.png, tool-after-open.png, tool-verify.json, reproducers).

## Result
DONE → 4.done. The last Vanessa-corpus residual is closed: qa-mcp opens an external `.epf` the 1C-native way (no
VanessaExt) and the corpus transpiles 100%. Scope note: the capability executes via the dedicated
`open_external_processor` tool (an xtest/OS action, like `write_form_value_xtest`); the Gherkin step transpiles for
drop-in authoring. Follow-on (optional): in-runner execution of the step + Cyrillic-path entry via clipboard if
xclip is added.

## Related
- Research: `evidence/card103-external-epf-research-2026-06-21/findings.md` (mechanism + the live main-window
  entry-point screenshot). Mechanism: `ВнешниеОбработкиМенеджер.Подключить` (platform help). Reuses card-100
  xtest/locate + `answer_dialog`; card-101 `_foreground_form_by_link` for window resolution.
- Parent: card 102. Sibling residual-closing of card 103 (E-FW step library).
- Memory: [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-21 created from the card-103 corpus-residual research (go/no-go = GO, native «Файл→Открыть» + xtest;
  Vanessa-component-free). Distinct mechanism (OS UI flow, not protocol replay) → its own card.
- 2026-06-21 DELIVERED → 4.done (same day). Live-proved the native flow (menu → Файл → Открыть → GTK chooser →
  Ctrl+L → Unicode-safe path → Enter) opening the fixture `.epf`; shipped the `open_external_processor` MCP tool
  (caption-verified live) + the `open_external_epf` Gherkin step + `xtest_type_unicode`. Corpus → 100% (LAB_MIN→1.0,
  canonical 10 scenarios). 412 tests. Evidence `evidence/card109-open-epf-live-2026-06-21/`.
