# Card 97 change 4 — dynamic-list SEARCH-STRING capture (for REPLAY): connect+open the fixture form, then type
# two DIFFERENT search strings into the dynlist's search-string addition (ДенамическийСписокИерархияСтрокаПоиска)
# so the two SET frames differ only in value (diff-decode). The search addition filters the list incrementally
# (searchOnInput=Auto). No get_form_analysis inside the tcpdump window (keep the connection a single clean stream).
Функционал: QA card-97 ch4 capture dynlist search-string

Сценарий: connect open and search the dynamic list
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице "ДенамическийСписокИерархия" в дополнение формы с именем 'ДенамическийСписокИерархияСтрокаПоиска' я ввожу текст 'Молоко'
  И в таблице "ДенамическийСписокИерархия" в дополнение формы с именем 'ДенамическийСписокИерархияСтрокаПоиска' я ввожу текст 'Творог'
