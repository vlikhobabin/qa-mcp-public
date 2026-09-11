# Card 96 / E2 menu capture: connect + open the fixture form only. The menu flow (click PF_SHOW_CHOICE_MENU →
# «в меню формы я выбираю 'PF_MENU_1'») is driven afterwards via execute_step_from_text on the OPEN form, for a
# clean single connection (the ПоказатьВыборИзМеню popup reuses the form window). Result: Сообщить("PF_MENU=...").
Функционал: QA card-96 menu capture

Сценарий: connect and open the protocol fixture form
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacm' | 'qacm'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
