# Card 97 #2 capture: connect+open + add a row + edit the NUMBER cell (PF_TABLE_NUMBER) + the DATE cell
# (PF_TABLE_DATE, new column) + a trailing string input so each cell COMMITS via the next focus-change. Decode
# whether number/date cells use a different per-type value buffer than the proven string cell (card 86c).
Функционал: QA card-97 number/date cell capture

Сценарий: add row and edit number and date cells
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_NUMBER' я ввожу текст "777"
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_DATE' я ввожу текст "15.08.2026"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст "C97COMMIT"
