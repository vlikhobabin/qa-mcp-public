# Card 97 change 3 — report / ТабличныйДокумент capture (for REPLAY): connect+open the fixture form, then click
# PF_RUN_REPORT. The command fills the form's ТабличныйДокумент attribute PF_REPORT ON THE SERVER (cells
# PF_RPT_R1C1 / R1C2 / R2C1 / R2C2), so the spreadsheet content is sent manager->client in the click response
# (where the spreadsheet-read decode finds the cell markers). No get_form_analysis inside the tcpdump window.
Функционал: QA card-97 ch3 capture report spreadsheet

Сценарий: connect open and run the report
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я нажимаю на кнопку 'PF_RUN_REPORT'
