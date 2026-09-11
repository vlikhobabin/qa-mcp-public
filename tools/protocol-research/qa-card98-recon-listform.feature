# Card 98 recon — open the Товары list so get_form_analysis can reveal the dynamic list table name + the
# view-mode command names (Список/Дерево/ИерархическийСписок) before the real capture. NOT a capture feature.
Функционал: QA card-98 recon Товары list form

Сценарий: connect and open the Товары list
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qrc'  | 'qrc'     | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму списка справочника "Товары"
