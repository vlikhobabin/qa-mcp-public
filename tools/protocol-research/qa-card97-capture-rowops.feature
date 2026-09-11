# Card 97 #1 ACTION-ONLY capture: table row ops on the ALREADY-open fixture form on the already-connected
# client (no connect/open step) so the pcap stays a single clean manager<->client connection. Each click is a
# genuine form-command invoke (Button[NAME] 88 81 81 e1) on the fixture's new row-op commands. Order: COPY first
# (grows the table so MOVE/DELETE always have a row), then MOVE_DOWN, MOVE_UP, DELETE last. Call
# get_form_analysis after for a read-back sweep (PF_TABLE_SNAPSHOT / PF_LAST_ACTION).
Функционал: QA card-97 capture row ops

Сценарий: capture copy move delete on the open fixture form
  Допустим я нажимаю на кнопку 'PF_COPY_ROW'
  И я нажимаю на кнопку 'PF_MOVE_ROW_DOWN'
  И я нажимаю на кнопку 'PF_MOVE_ROW_UP'
  И я нажимаю на кнопку 'PF_DELETE_ROW'
