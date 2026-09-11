# Card 90 SELF-CONTAINED page-field capture (replayable): connect + open + input PF_PAGE_A_FIELD (a field
# nested in a tab page Group[PF_PAGES_MAIN].Group[PF_PAGE_A]) + a focus-change commit (PF_EDIT_NUMBER).
Функционал: QA card-90 self-contained page-field capture

Сценарий: connect open input page-A field and commit
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qapfc' | 'qapfc'   | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_PAGE_A_FIELD' я ввожу текст 'PGFLDA'
  И в поле с именем 'PF_EDIT_NUMBER' я ввожу текст '42'
