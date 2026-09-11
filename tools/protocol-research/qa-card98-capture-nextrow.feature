# Card 98 — capture the DYNLIST «перехожу к следующей строке» (next-row) command on a real catalog list form, to
# enable reading the WHOLE grid. Open the Товары list (named columns Наименование/Код over Молоко/Творог/Обувь/…),
# position to the first row + read, then step next-row + read twice. Captures: first-row position + 3 reads +
# 2 next-row commands (decode-by-diff). The reads (row1/row2/row3 Наименование) prove the cursor actually moved.
Функционал: QA card-98 capture dynlist next-row navigation

Сценарий: connect open list iterate rows via next-row and read each
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qnr'  | 'qnr'     | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму списка справочника "Товары"
  И в таблице "Список" я перехожу к первой строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р1"
  И в таблице "Список" я перехожу к следующей строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р2"
  И в таблице "Список" я перехожу к следующей строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р3"
