# API coverage limitations (deferred to a future qa-mcp version)

This document records automated-testing API members that the capture → decode →
probe → compare pipeline **cannot currently accept**, and *why*. These are honest
`candidate` rows in `api-inventory/mutation-evidence-map.json` /
`scope-tracker.md` — the protocol member is real and not broken; we simply cannot
build a clean Vanessa-driven reference capture for it in the present setup. Each has
a concrete path to resolution in a later version.

Status as of 2026-06-13 (after Phase 1 `mutation` and Phase 2 `safe_ui_action`):

- `mutation` bucket — **9/9 accepted, 0 candidate.** The one Phase-1 blocker
  (`TestedFormDecoration.Click`, which needs a hyperlink decoration) was resolved by
  adding the `Расширение1` fixture (data processor `Расш1_Обработка1` with
  `Гиперссылка=Истина` decorations) to `vanessa_client`. See
  `evidence/mutation-corpus/ext-decoration-hyperlink-click/`.
- `safe_ui_action` bucket — **22/29 accepted, 7 candidate** (the list below).

## The 7 `safe_ui_action` candidates, by root cause

### Class A — no Vanessa step driver (5 members)
The acceptance methodology uses a VanessaAutomation step as the reference oracle.
These platform methods have **no step** that calls them (verified: no call site in
the UITestRunner `step_definitions` module, none in the live step database), so there
is nothing to capture/compare against through the Vanessa-driven pipeline. This is a
driver/tooling gap, **independent of the demo configuration**.

| Member | API method | Note |
| --- | --- | --- |
| `TestedClientApplicationWindow.GotoStartPage` | `ПерейтиКНачальнойСтранице` | no step |
| `TestedClientApplicationWindow.GotoNextWindow` | `ПерейтиКСледующемуОкну` | no step |
| `TestedClientApplicationWindow.GotoPreviousWindow` | `ПерейтиКПредыдущемуОкну` | no step |
| `TestedClientApplicationWindow.ChooseUserMessage` | `ВыбратьСообщениеПользователю` | no step |
| `TestedForm.Activate` | `ТестируемаяФорма.Активизировать` | `я активизирую форму "X"` activates the *window* (`ТекОкно.Активизировать()`), not the form |

Resolution path: add custom step wrappers (e.g. via VAExtension or a project step
library) that call these methods directly, then capture/probe/promote normally.

Evidence: `evidence/safe-ui-corpus/window-members-blocked/findings.md`,
`evidence/safe-ui-corpus/activate-no-driver/findings.md`.

### Class B — platform/test-API rejects the action on the available element (1 member)
| Member | API method | Note |
| --- | --- | --- |
| `TestedFormTable.Expand` | `Развернуть` | throws `Неподходящее состояние элемента управления` on a collapsed **dynamic-list** group row (both `Развернуть()` and `Развернуть(,Истина)`), although `Collapse` works on the same row |

The element exists (the hierarchical `Справочник.Товары` list has folders), and
`Expand` itself is fine — `TestedFormGroup.Expand` was accepted on a *form* group
(`Контрагенты` → `Прочее`). It is specifically `TestedFormTable.Expand` on a
**dynamic-list tree** that the test API rejects.

Resolution path: a form carrying a static tree (`ДеревоЗначений`) where Expand of a
collapsed node is valid; the demo has no such form today.

Evidence: `evidence/safe-ui-corpus/tovary-hierarchy-batch/`.

### Class C — no suitable UI element in the demo configuration (1 member)
| Member | API method | Note |
| --- | --- | --- |
| `TestedFormButton.Activate` | `ТестируемаяКнопкаФормы.Активизировать` | no `активизирую кнопку` step; the generic field-finder does **not** reach command-bar buttons (`ПереключитьАктивность` → `Элемента формы с именем <…> не найдено`), and the demo has no body-level form button to target |

Resolution path: add a fixture form with a body-level `UsualButton`, then drive
`я активизирую поле с именем '<button>'`.

Evidence: `evidence/safe-ui-corpus/activate-no-driver/findings.md`.

## Summary of resolution levers for the next version
1. **Custom step wrappers** (VAExtension/project step library) for the 4 window-nav
   methods and `TestedForm.Activate` (Class A) — the highest-count lever.
2. **Fixture forms** in `vanessa_client`: a static-tree form (Class B, `Table.Expand`)
   and a body-button form (Class C, `Button.Activate`) — same approach as the
   `Расширение1` hyperlink-decoration fixture that unblocked Phase 1.

None of these block the breadth methodology itself; they are per-member driver/fixture
gaps to be picked up deliberately. Tracked on the board: card 71.
