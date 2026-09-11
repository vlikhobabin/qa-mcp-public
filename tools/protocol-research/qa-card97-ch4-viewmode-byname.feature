# Card 97 change 4 — dynlist VIEW-MODE capture (by NAME, fresh filename to dodge run_scenario's feature cache).
# Click two «Режим просмотра» commands of the dynlist BY NAME (caption is «Список»/«Иерархический список», so
# «по имени» is required): ДенамическийСписокИерархияСписок (flat) then ...ИерархическийСписок (grouped). The two
# command frames differ only in the UTF-16LE Button leaf (the diff confirms the leaf retarget). No get_form_analysis.
Функционал: QA card-97 ch4 capture dynlist view-mode by name

Сценарий: connect open and switch the dynamic list view mode by name
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я нажимаю на кнопку с именем 'ДенамическийСписокИерархияСписок'
  И я нажимаю на кнопку с именем 'ДенамическийСписокИерархияИерархическийСписок'
