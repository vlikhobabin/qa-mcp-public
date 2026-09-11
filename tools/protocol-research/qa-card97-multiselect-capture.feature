# Card 97 #1 multi-select PRODUCTIZE capture: connect+open + genuine "select all rows" (the Table-element
# command `Table[PF_TABLE_ITEMS] 88 82 81 20 20 20`, the first action so its setup = form-open) + click
# PF_REFRESH_SELECTION (materializes the PF_SELECTED_ROWS read-back marker = PF_SEL[<n>]=<marker>,…). One clean
# client connection.
Функционал: QA card-97 multi-select capture

Сценарий: select all rows then refresh selection read-back
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице 'PF_TABLE_ITEMS' я выделяю все строки
  И я нажимаю на кнопку 'PF_REFRESH_SELECTION'
