# Card 98 — capture the genuine TABLE-CELL READ command (Vanessa «я запоминаю значение поля с именем … таблицы …
# как …», type Переменные.Сохранить значение.Таблица.Поле таблицы). connect + open fixture + add a row + write a
# KNOWN value into PF_TABLE_TEXT + commit it (focus-change to PF_EDIT_STRING) + READ the cell value by name. The
# read step is LAST so the get-cell command + its row-data response are the tail of the capture.
Функционал: QA card-98 capture table-cell read

Сценарий: connect open populate-cell and READ a table cell value by field name
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qatc' | 'qatc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "CELLREAD7"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'COMMIT7'
  И я запоминаю значение поля с именем 'PF_TABLE_TEXT' таблицы "PF_TABLE_ITEMS" как "ЯЧ"
