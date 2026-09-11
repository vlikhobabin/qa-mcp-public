# Card 98 — capture a DYNLIST current-row position + cell read. The fixture dynlist ДенамическийСписокИерархия is
# over Catalog.Товары (vanessa_client Товары has rows). A dynlist has NO current row on open (unlike a form table),
# so position to the first row, THEN read a column by name. Captures the «перехожу к первой строке» command + the
# read returning a real Товары value.
Функционал: QA card-98 capture dynlist current-row read

Сценарий: connect open position-first-row and READ a dynlist column by name
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qatc' | 'qatc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "ДенамическийСписокИерархия" я перехожу к первой строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "ДенамическийСписокИерархия" как "ЯЧ"
