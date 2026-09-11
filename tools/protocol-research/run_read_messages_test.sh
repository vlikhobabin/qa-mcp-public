#!/usr/bin/env bash
# Card 96 / E5 — capture-free user-message READ live-verify: boot the native TestClient on :15381 and run
# read_user_messages_probe.py (replays the choice-from-list flow whose callback Сообщит a known marker, then
# decodes the messages-to-user panel). Needs vanessa_client FREE: apache stopped (restarted on exit). Mirrors
# run_close_window_test.sh.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"; USER="${TEST_CLIENT_USER:-Администратор}"; TPORT="${TPORT:-15381}"
CAP="${CAP:-runtime/protocol-research/captures/genuine-card96-choicelist-20260618/traffic}"
EXP="${EXP:-PF_CHOICE=PF_CHOICE_B}"
OUT="$REPO/runtime/protocol-research/read-messages-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
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
echo "== read_user_messages probe (expected=$EXP) =="
PYTHONPATH=src python3 tools/protocol-research/read_user_messages_probe.py "$TPORT" "$CAP" "$EXP" 2>&1 | tee "$OUT/log.txt"
echo "out=$OUT"
