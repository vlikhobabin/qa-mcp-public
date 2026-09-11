# Card 90 genuine capture: checkbox (Boolean / Флаг), choice (Переключатель), table-row ops.
# Run via the genuine Vanessa TestManager (run_scenario) with tcpdump on the client TPort range.
# Order = decreasing confidence: the KEYSTONE checkbox SETs come first so a later table-step
# abort still leaves clean checkbox capture. Each input is followed by another action so the prior
# input COMMITS via focus-change. Checkbox/radio fire ПриИзменении on click (self-committing).
# Boolean is captured for BOTH values: set FALSE->true and clear TRUE->false (decodes the bool buffer).
# After this feature, call get_form_analysis to capture a post-action READ sweep (read-back frames).
Функционал: QA card-90 capture checkbox/choice/table

Сценарий: capture native checkbox choice table actions on the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacap' | 'qacap'   | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90STR'
  И я устанавливаю флаг с именем 'PF_CHECKBOX_FALSE'
  И я снимаю флаг с именем 'PF_CHECKBOX_TRUE'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на '3'
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "C90ROW"
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_NUMBER' я ввожу текст "777"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90END'
