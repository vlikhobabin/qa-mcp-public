# Card 90 SELF-CONTAINED "write into a specific existing row": connect + open + position to row 2 + edit that
# row's PF_TABLE_TEXT + a focus-change commit. Replaying this writes into row 2 (the row-select is baked into
# the setup; the cell SET hits the active row = row 2). PF_SELECTED_ROW_MARKER confirms the active row.
Функционал: QA card-90 row-2 write capture

Сценарий: connect open select row 2 and write its cell
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qr2w'  | 'qr2w'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я перехожу к строке:
    | 'PF_TABLE_TEXT'   |
    | 'PF_ROW_002_TEXT' |
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "R2WROT"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90RC'
