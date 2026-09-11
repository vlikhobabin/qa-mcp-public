# Card 86 genuine MULTI-ACTION capture driver (run via the genuine Vanessa TestManager run_scenario).
# Connects a thin client to the vanessa_client file infobase, opens the protocol fixture processor, and
# performs a chain of native UI actions. Each input is followed by another action, so the PRIOR input
# commits (focus-change) and its genuine SET/command is captured. Yields genuine command frames for:
# DATE input, NUMBER input, STRING input, and page-SWITCH. (Tab-page FIELD inputs are dropped: PF_PAGE_*_FIELD
# is not a plain text control — «Неподходящий тип элемента управления» — tracked in card 90.)
# Capture a post-input READ sweep by calling get_form_analysis after this feature (so read-back frames exist).
Функционал: QA multi-action capture

Сценарий: capture native actions on the protocol fixture
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'   | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'        | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qacap' | 'qacap'   | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И в поле с именем 'PF_EDIT_DATE' я ввожу текущую дату
  И в поле с именем 'PF_EDIT_NUMBER' я ввожу текст '654,32'
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'MULTICAP'
  И я перехожу к закладке с именем 'PF_PAGE_B'
  И я перехожу к закладке с именем 'PF_PAGE_A'
