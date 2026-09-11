# Card 98 #2 (remainder) — window-list capture: connect + open the fixture form, then open the Товары
# catalog list via a navigation link, so the client has SEVERAL windows/tabs (Начальная страница + the
# fixture form + the Товары list = ≥3 SecondaryFrames). After this feature, call get_window_list_testclient
# (the Vanessa MCP window-list tool) while tcpdump records the manager↔client port — the response should
# enumerate the open windows. Auto-allow runs ONLY at manager boot, NOT during the window-list call.
Функционал: QA card-98 window-list capture

Сценарий: open the fixture form and the Товары list (several windows)
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qawl' | 'qawl'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я перехожу по навигационной ссылке "e1cib/list/Справочник.Товары"
