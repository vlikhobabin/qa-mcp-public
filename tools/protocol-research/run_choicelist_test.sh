#!/usr/bin/env bash
# Card 96 / E2 — capture-free CHOOSE-FROM-LIST live-verify: boot the native TestClient on :15381 and run
# choose_from_list_probe.py (clicks the choice-list command, picks a value re-targeted from the captured one,
# confirms the Сообщить("PF_CHOICE=...") marker). Needs vanessa_client FREE: the genuine Vanessa manager must
# be DOWN and apache2 stopped (restarted on exit). Mirrors run_table_cell_test.sh.
#
#   VALUE=PF_CHOICE_A tools/protocol-research/run_choicelist_test.sh
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"; USER="${TEST_CLIENT_USER:-Администратор}"; TPORT="${TPORT:-15381}"
CAP="${CAP:-runtime/protocol-research/captures/genuine-card96-choicelist-20260618/traffic}"
VALUE="${VALUE:-PF_CHOICE_A}"
# Menu twin: CAP=…/genuine-card96-menu-20260618/traffic VALUE=PF_MENU_2 BASE_COMMAND=PF_SHOW_CHOICE_MENU \
#   CAPTURED_VALUE=PF_MENU_1 MSG_PREFIX='PF_MENU=' tools/protocol-research/run_choicelist_test.sh
BASE_COMMAND="${BASE_COMMAND:-PF_SHOW_CHOICE_LIST}"; CAPTURED_VALUE="${CAPTURED_VALUE:-PF_CHOICE_B}"; MSG_PREFIX="${MSG_PREFIX:-PF_CHOICE=}"
OUT="$REPO/runtime/protocol-research/choicelist-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
echo "== stop apache =="; sudo -n systemctl stop apache2 && echo apache-stopped
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
TC_PID=""
cleanup(){ [ -n "$TC_PID" ] && { pkill -TERM -P "$TC_PID" 2>/dev/null; kill -TERM "$TC_PID" 2>/dev/null; }
  pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; pkill -x Xvfb 2>/dev/null
  sleep 2; echo "== restart apache =="; sudo -n systemctl start apache2 && echo apache-started; }
trap cleanup EXIT
echo "== boot TestClient :$TPORT under Xvfb =="
nohup xvfb-run -a "$CLIENT_BIN" ENTERPRISE /IBConnectionString "File=\"$IB\";" "/N$USER" \
  /TESTCLIENT -TPort "$TPORT" /DisableStartupDialogs /DisableStartupMessages \
  /Out "$OUT/testclient.out" -NoTruncate >"$OUT/client.out" 2>&1 &
TC_PID=$!
for i in $(seq 1 120); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; exit 1; }
sleep 3; echo "client-up pid=$TC_PID"
echo "== choose_from_list probe (value=$VALUE base_command=$BASE_COMMAND) =="
PYTHONPATH=src python3 tools/protocol-research/choose_from_list_probe.py \
  "$TPORT" "$CAP" "$VALUE" "$BASE_COMMAND" "$CAPTURED_VALUE" "$MSG_PREFIX" 2>&1 | tee "$OUT/log.txt"
echo "out=$OUT"
