# Card 90 SELF-CONTAINED row-addressing capture: connect + open + position to row 2 + position to row 3
# (two row-selects → decode-by-diff) + add a row. PF_SELECTED_ROW_MARKER (fixture OnActivateRow handler) reports
# the active row index+marker for verification.
Функционал: QA card-90 row-addressing capture

Сценарий: connect open select rows and add a row
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qrac' | 'qrac'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я перехожу к строке:
    | 'PF_TABLE_TEXT'   |
    | 'PF_ROW_002_TEXT' |
  И в таблице "PF_TABLE_ITEMS" я перехожу к строке:
    | 'PF_TABLE_TEXT'   |
    | 'PF_ROW_003_TEXT' |
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
