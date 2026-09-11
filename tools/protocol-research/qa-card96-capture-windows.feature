# Card 96 / E3 windows capture (close + activate): connect + open the fixture form, open the Контрагенты
# catalog list via a navigation link, drill a row to open a record card (NEW window), close the active card
# («закрываю текущее окно»), then bring the buried fixture form to front by title («активизирую окно "…"»).
# Captured full-session via tcpdump so the replay can recreate the windows (close/activate are window-level
# `…SecondaryFrame[<window>] 88 82 81` / `e0 4b` commands). Auto-allow runs ONLY at manager boot, NOT during
# this feature (it would XTEST-contaminate the window ops).
Функционал: QA card-96 windows capture (close + activate)

Сценарий: open fixture, open Контрагенты list, open a card, close it, activate the fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qaw4' | 'qaw4'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я перехожу по навигационной ссылке "e1cib/list/Справочник.Контрагенты"
  И я нажимаю на кнопку с именем 'ФормаИзменить'
  И я закрываю текущее окно
  И я активизирую окно "QA MCP Protocol Fixture V1"
