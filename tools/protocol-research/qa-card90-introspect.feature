# Card 90 introspection: connect a thin client to vanessa_client, open the protocol fixture form.
# After this runs, call get_form_analysis to read the exact element types/values (checkbox state,
# radio PF_CHOICE_MODE choice values, table PF_TABLE_ITEMS columns) so the capture feature is correct.
Функционал: QA card-90 introspect

Сценарий: connect and open the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacap' | 'qacap'   | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
