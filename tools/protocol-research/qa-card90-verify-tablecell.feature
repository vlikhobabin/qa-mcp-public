# Card 90 LIVE VERIFY: after deploying the table-cell fixture fix (table made editable),
# the table-cell input steps must SUCCEED (previously "ВвестиТекст не может быть вызван").
Функционал: QA card-90 verify table-cell editable

Сценарий: connect open and input into the table cell
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qatv2' | 'qatv2'  | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "TBLOK"
