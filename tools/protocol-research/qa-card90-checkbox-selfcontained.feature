# Card 90 SELF-CONTAINED checkbox capture: connect + open + checkbox toggles + a final string commit.
# Includes the form-open handshake so the capture is replayable standalone (derive_checkbox_toggle +
# toggle_checkbox, mirroring the page-switch productization). No radio/table (those abort/are deeper).
Функционал: QA card-90 self-contained checkbox capture

Сценарий: connect open and toggle checkboxes on the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacb'  | 'qacb'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'CBSTR'
  И я устанавливаю флаг с именем 'PF_CHECKBOX_FALSE'
  И я снимаю флаг с именем 'PF_CHECKBOX_TRUE'
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'CBEND'
