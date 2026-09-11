# Card 90 ACTION-ONLY capture: runs against the ALREADY-open fixture form on the already-connected
# client (no connect/open step) so the pcap stays a single clean manager<->client connection.
# Keystone checkbox SETs first (both values), then choice, then table; each input followed by another
# action so the prior commits via focus-change. Call get_form_analysis after for a read-back sweep.
Функционал: QA card-90 capture actions only

Сценарий: capture checkbox choice table on the open fixture form
  Допустим в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90STR'
  И я устанавливаю флаг с именем 'PF_CHECKBOX_FALSE'
  И я снимаю флаг с именем 'PF_CHECKBOX_TRUE'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на '3'
  И в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "C90ROW"
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_NUMBER' я ввожу текст "777"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90END'
