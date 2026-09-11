# Card 96 / E1 dialog capture: connect + open the fixture form only. The dialog flow (click PF_V4_WARNING →
# real ПоказатьПредупреждение opens a NEW window → «я закрываю окно предупреждения» = ОК; or PF_V4_QUESTION_YES →
# ПоказатьВопрос Да/Нет → click «Да») is driven afterwards via execute_step_from_text on the OPEN form. The
# answer commits the result into PF_V4_DIALOG_RESULT (real-dialog fixture edit, card96-dialogs deploy).
Функционал: QA card-96 dialog capture

Сценарий: connect and open the protocol fixture form
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacd' | 'qacd'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
