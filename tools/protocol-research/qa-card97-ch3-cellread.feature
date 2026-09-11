# Card 97 change 3 — confirm option (b): the spreadsheet cell is read IN THE CLIENT (1C method on the live
# ТабличныйДокумент object), not by decoding a wire blob. Run the report, then navigate to cell R1C1 and store
# the CURRENT cell's value into a Vanessa variable — these are in-client reads of the live object.
Функционал: QA card-97 ch3 confirm in-client spreadsheet cell read

Сценарий: run the report and read a spreadsheet cell in the client
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я нажимаю на кнопку 'PF_RUN_REPORT'
  И в табличном документе "PF_REPORT" я перехожу к ячейке "R1C1"
  И я запоминаю значение текущей ячейки "PF_REPORT" в переменную "CELL11"
