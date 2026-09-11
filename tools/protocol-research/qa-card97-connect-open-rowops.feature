# Card 97 #1 SELF-CONTAINED capture for REPLAY: connect a fresh client + open the fixture form (the form-open
# render becomes the replay SETUP) + click the 4 row-op commands. The FIRST click (PF_COPY_ROW) immediately
# follows the form-open, so derive_command_click("PF_COPY_ROW") yields setup=form-open + a clean click block,
# which click_command retargets (Button leaf) to PF_DELETE_ROW / PF_MOVE_ROW_UP / PF_MOVE_ROW_DOWN.
Функционал: QA card-97 connect open and row ops

Сценарий: connect open and click row ops
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я нажимаю на кнопку 'PF_COPY_ROW'
  И я нажимаю на кнопку 'PF_MOVE_ROW_DOWN'
  И я нажимаю на кнопку 'PF_MOVE_ROW_UP'
  И я нажимаю на кнопку 'PF_DELETE_ROW'
