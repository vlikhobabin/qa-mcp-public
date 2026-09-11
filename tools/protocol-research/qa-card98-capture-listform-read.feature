# Card 98 — capture a SUCCESSFUL dynlist read on a REAL catalog LIST form (named columns + data). The fixture's
# embedded dynlist has auto-generated (unnamed) columns so even Vanessa can't read it; a catalog LIST form's
# dynlist "Список" has named columns (Наименование/Код) over a populated catalog (Товары: Молоко/Творог). connect
# + open the Товары list form + position to the first row + READ column "Наименование" — captures the genuine
# SUCCESSFUL dynlist read to compare with the form-table e0 4b 55 mechanism.
Функционал: QA card-98 capture catalog list-form dynlist read

Сценарий: connect open catalog list-form position-first-row and READ a dynlist column by name
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qatc' | 'qatc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму списка справочника "Товары"
  И в таблице "Список" я перехожу к первой строке
  И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "ЯЧ"
