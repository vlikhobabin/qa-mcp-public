# Card 98 change-1 generalization — connect + open ONLY the fixture form (the active window), so a
# get_form_analysis / get_active_window_data call introspects that form. Captured to decode the element
# ENUMERATION command (the part that lists every element of the live form), for splice-replay (no per-form capture).
Функционал: QA card-98 form introspection capture

Сценарий: open the fixture form
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qai'  | 'qai'     | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
