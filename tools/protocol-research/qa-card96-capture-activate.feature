# Card 96 / E3 activate-only capture: connect + open the fixture form, open the Контрагенты catalog list, drill
# a row to open a record card (card becomes topmost; fixture + list buried behind it), then bring the buried
# fixture form to front by title — «активизирую окно "QA MCP Protocol Fixture V1"». NOTHING is closed, so the
# activate is unambiguous: the fixture window must stay alive AND become the active/reported window.
Функционал: QA card-96 activate capture

Сценарий: open fixture, open Контрагенты list, open a card, activate the buried fixture (no close)
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qaw5' | 'qaw5'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я перехожу по навигационной ссылке "e1cib/list/Справочник.Контрагенты"
  И я нажимаю на кнопку с именем 'ФормаИзменить'
  И я активизирую окно "QA MCP Protocol Fixture V1"
