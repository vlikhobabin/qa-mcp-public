# Card 97 #1 multi-select INVESTIGATION: does the genuine Vanessa "select all rows" step produce a
# manager->client protocol frame (productizable like the row-op clicks) or is it OS-level (like keyboard,
# VanessaExt — not replayable)? Connect+open+select-all so the pcap captures whatever the step emits.
Функционал: QA card-97 multi-select probe

Сценарий: connect open and select all rows
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в таблице 'PF_TABLE_ITEMS' я выделяю все строки
