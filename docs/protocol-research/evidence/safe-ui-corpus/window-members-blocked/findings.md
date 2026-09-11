# Window-navigation safe_ui_action members — candidate (no Vanessa step driver)

Four `TestedClientApplicationWindow` `safe_ui_action` members have **no VanessaAutomation
step** that drives them, so they cannot be captured through the Vanessa-driven pipeline
(the reference oracle is produced by a Vanessa step; without one there is nothing to
capture/compare against):

| Member | API method | Vanessa step |
| --- | --- | --- |
| `GotoStartPage` | `ПерейтиКНачальнойСтранице` | none found |
| `GotoNextWindow` | `ПерейтиКСледующемуОкну` | none found |
| `GotoPreviousWindow` | `ПерейтиКПредыдущемуОкну` | none found |
| `ChooseUserMessage` | `ВыбратьСообщениеПользователю` | none found |

Verified by grepping the upstream UITestRunner step_definitions module for each method
call site (none) and the live Vanessa step database by keyword (none). The methods exist
on the platform object but VanessaAutomation 51f920f exposes no step wrapper for them.

To accept these, a step driver would be needed (a VAExtension step or a custom step
calling the method). Recorded as `candidate`.
