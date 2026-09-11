# Card 98 #3 — a Vanessa-canonical .feature that transpiles 100% against qa-mcp (no Vanessa).
# Run live with run_scenario; preview the mapping with transpile / search_for_steps.
Функционал: QA MCP Vanessa-style demo

Сценарий: Прочитать форму и значения
  Когда Я получаю сводку формы
  И Я читаю значение поля 'PF_EDIT_STRING'
  И результат содержит 'PF_EDIT_STRING_VALUE'
  И Значение поля 'PF_FIXTURE_VERSION' содержит 'protocol-fixture'

Сценарий: Действия на форме
  Когда В поле с именем 'PF_EDIT_STRING' я ввожу текст 'NEWVALUE'
  И Я нажимаю на кнопку с именем 'PF_ADD_ROW'
  И Я перехожу к закладке с именем 'PF_PAGE_A'
