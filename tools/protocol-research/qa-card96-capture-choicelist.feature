# Card 96 (E2) choice-list capture: connect + open fixture form + trigger ПоказатьВыборИзСписка
# (command PF_SHOW_CHOICE_LIST → values PF_CHOICE_A/B/C) and PICK PF_CHOICE_B from the modal.
# The pick result surfaces via Сообщить("PF_CHOICE=PF_CHOICE_B") — captured on the wire.
# Step "я выбираю из списка" drives a list raised by ПоказатьВыборИзСписка() (confirmed via step search).
# A leading string input is an anchor to locate the choice-list flow start in the capture.
Функционал: QA card-96 choice-list capture

Сценарий: connect open form trigger choice list and pick a value
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacl' | 'qacl'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'CLSTR'
  И я нажимаю на кнопку 'PF_SHOW_CHOICE_LIST'
  И я выбираю из списка "PF_CHOICE_B"
