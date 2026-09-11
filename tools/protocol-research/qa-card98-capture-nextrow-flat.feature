# Card 98 follow-up — capture the DYNLIST next-row navigation in FLAT view («Список»), so read_list_grid can read
# NESTED items (Товары defaults to hierarchical → only the 4 top-level folders are visible). Open the Товары list,
# switch the dynamic list to flat view (the standard «СписокСписок» view-mode command), position to the first row +
# read, then step next-row + read twice. The view-switch is baked INTO the capture so a faithful full-sequence
# replay opens + flattens + reads in one cold session (read_list_grid_replay drops in by pointing capture_dir here).
# No get_form_analysis inside the tcpdump window.
Функционал: QA card-98 capture dynlist FLAT-view next-row navigation

Сценарий: connect open list switch to flat view iterate rows via next-row and read each
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qflc' | 'qflc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму списка справочника "Товары"
  И я нажимаю на кнопку с именем 'ФормаСписок'
  И в таблице "Список" я перехожу к первой строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р1"
  И в таблице "Список" я перехожу к следующей строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р2"
  И в таблице "Список" я перехожу к следующей строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р3"
