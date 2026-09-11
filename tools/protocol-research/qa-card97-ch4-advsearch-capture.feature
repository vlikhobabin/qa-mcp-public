# Card 97 change 4 — dynlist FILTER via «Расширенный поиск» (UniversalListFindExtForm) capture (for REPLAY):
# connect+open → click «Расширенный поиск» (…Найти) → the dialog opens → pick the Наименование field → type the
# search pattern → click «&Найти» (Find) → the list filters. A modal-dialog FILL flow (open new window → SET a
# field in it → confirm), the reusable "drive a dialog" pattern. No get_form_analysis inside the tcpdump window.
Функционал: QA card-97 ch4 capture dynlist advanced-search filter

Сценарий: connect open advanced-search and filter by name
  Допустим Я подключаю клиент тестирования с параметрами один на информационную базу:
    | 'Имя'  | 'Синоним' | 'Порт' | 'Строка соединения'                  | 'Логин'         | 'Пароль' | 'Запускаемая обработка' | 'Дополнительные параметры строки запуска' |
    | 'qa97' | 'qa97'    | ''     | 'File="/opt/1c-dev/vanessa_client";' | 'Администратор' | ''       | ''                      | ''                                        |
  И я открываю основную форму обработки "ФикстураПротоколаTestClient"
  И я нажимаю на кнопку с именем 'ДенамическийСписокИерархияНайти'
  И в поле с именем 'Pattern' я ввожу текст 'Молоко'
  И я нажимаю на кнопку с именем 'Find'
