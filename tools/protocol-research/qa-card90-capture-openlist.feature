# Card 90 open-list capture: connect + open fixture form + open the Товары catalog list (the fixture's dynamic
# list ДенамическийСписокИерархия is based on Catalog.Товары) via a navigation link e1cib/list/Справочник.Товары.
Функционал: QA card-90 open-list capture

Сценарий: connect open form and open the Товары catalog list
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qaol' | 'qaol'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я перехожу по навигационной ссылке "e1cib/list/Справочник.Товары"
