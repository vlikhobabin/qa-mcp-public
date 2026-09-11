# Card 90 LIVE VERIFY: after deploying the page-field fix (PF_PAGE_A_FIELD / PF_PAGE_B_FIELD made editable),
# inputting into a field on a tab page must SUCCEED (was read-only).
Функционал: QA card-90 verify page-field input

Сценарий: connect open and input into page fields
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qapf' | 'qapf'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_PAGE_A_FIELD' я ввожу текст 'PAGEA1'
