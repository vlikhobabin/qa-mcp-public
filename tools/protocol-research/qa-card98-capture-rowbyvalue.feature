# Card 98 follow-up — capture the DYNLIST «перехожу к строке <column>=<value>» (go-to-row-by-value) on a real
# catalog list form, to enable read_list_row(where=…). Open the Товары list in flat view, then position to a row
# BY a Наименование value (two different values → decode-by-diff isolates the value field from the command shell,
# the card-90 row-addressing recipe), reading Код after each to prove the cursor actually moved to that row
# (Сапоги→000000002, Туфли→000000003). No get_form_analysis inside the tcpdump window.
Функционал: QA card-98 capture dynlist go-to-row by value

Сценарий: connect open list flat-view go to a row by name and read it
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qrvc' | 'qrvc'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму списка справочника "Товары"
  И я нажимаю на кнопку с именем 'ФормаСписок'
  И в таблице "Список" я перехожу к строке:
    | 'Наименование' |
    | 'Сапоги'       |
  И я запоминаю значение поля с именем 'Код' таблицы "Список" как "К1"
  И в таблице "Список" я перехожу к строке:
    | 'Наименование' |
    | 'Туфли'        |
  И я запоминаю значение поля с именем 'Код' таблицы "Список" как "К2"
