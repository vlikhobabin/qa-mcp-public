# Card 90 ACTION-ONLY capture, part 2: table row ops (add row + edit cells) and a radio attempt.
# Table first (high value, 86e); radio last so a radio failure does not abort the table capture.
# Each cell input is followed by another action so the prior cell commits via focus-change.
Функционал: QA card-90 capture table

Сценарий: capture table row ops on the open fixture form
  Допустим в таблице "PF_TABLE_ITEMS" я добавляю строку
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "C90ROW"
  И в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_NUMBER' я ввожу текст "777"
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'C90TBL'
  И я меняю значение переключателя с именем 'PF_CHOICE_MODE' на 'PF_CHOICE_A'
