# Card 90 SELF-CONTAINED choice capture: connect + open + change PF_CHOICE_MODE through all 3 variants.
# Includes the form-open handshake (replayable standalone, like the checkbox capture). The radio is
# addressed by name and its variant by the VALUE NAME (PF_CHOICE_A/B/C) — index form was rejected.
# Each change is a discrete action (radio commits on ПриИзменении); string inputs bracket it as anchors.
Функционал: QA card-90 self-contained choice capture

Сценарий: connect open and change radio variants on the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qach'  | 'qach'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'CHSTR'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на 'PF_CHOICE_A'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на 'PF_CHOICE_C'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на 'PF_CHOICE_B'
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'CHEND'
