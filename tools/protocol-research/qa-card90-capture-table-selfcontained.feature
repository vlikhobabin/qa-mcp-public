# Card 90 SELF-CONTAINED table-cell capture (replayable): connect + open + add 2 rows + edit
# PF_TABLE_TEXT on each (different values for decode-by-diff) + a final string commit (focus-change).
# Mirrors the checkbox/choice self-contained captures so the cell SET is replayable standalone.
Функционал: QA card-90 self-contained table-cell capture

Сценарий: connect open add-rows and edit table cells on the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qatc' | 'qatc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "CELLAA"
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "CELLBB"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90CMT'
