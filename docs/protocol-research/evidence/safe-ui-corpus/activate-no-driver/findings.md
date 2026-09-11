# TestedForm.Activate and TestedFormButton.Activate — candidate (no usable Vanessa step driver)

## TestedForm.Activate (`ТестируемаяФорма.Активизировать`)
No VanessaAutomation step calls `Активизировать()` on a `ТестируемаяФорма` object.
The step `я активизирую форму "X"` (`ЯАктивизируюФорму`) finds the window that
contains the form and calls `ТекОкно.Активизировать()` — i.e. it drives
`TestedClientApplicationWindow.Activate` (already accepted), not the form's own
`Активизировать`. Grep of the UITestRunner step_definitions module shows no
`<form-var>.Активизировать()` call site. Not capturable via the Vanessa pipeline.

## TestedFormButton.Activate (`ТестируемаяКнопкаФормы.Активизировать`)
There is no `я активизирую кнопку` step. The generic `я активизирую поле с именем 'X'`
(`ЯАктивизируюПолеСИменем`) activates any element found by `НайтиРеквизитОткрытойФормыПоЗаголовку`,
but that finder does not reach command-bar buttons: activating the only custom demo
button `ПереключитьАктивность` (in the ТоварныеЗапасы command bar) failed with
`Элемента формы с именем <ПереключитьАктивность> не найдено`. The demo configuration
has no body-level (non-command-bar) form button to target. Without a findable button
element there is no clean driver.

Both recorded as `candidate`. Accepting them would need a body-level button fixture
(for Button.Activate) and/or a step that calls the form/button `.Активизировать()` directly.
