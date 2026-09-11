#!/usr/bin/env bash
# Card 80 Fork-3 (3a): full-session replay of the GENUINE input capture (from frame 0 = the rich
# 2-round handshake) against a fresh TestClient, with live GUID rebind (native_samesession_commit_probe).
# Tests whether reproducing the genuine session SETUP makes the client ACCEPT input (set_response echoes
# the value). If yes -> the input-authorization is on the wire (RE-able). If no -> off-wire (card-76).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"; USER="${TEST_CLIENT_USER:-Администратор}"; TPORT=15381
CAPTURE="${CAPTURE:-genuine-commit-converted}"; MARKER="${MARKER:-QAGENUINE2026}"
READ_FRAMES="${READ_FRAMES:-356-362}"; STOP_AFTER="${STOP_AFTER:-364}"; RETARGET="${RETARGET:-}"
OUT="$REPO/runtime/protocol-research/fullreplay/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"

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

echo "== full-session replay of $CAPTURE (handshake frame 0 -> SET -> focus-change) =="
set +e
PYTHONPATH=src python3 tools/protocol-research/native_samesession_commit_probe.py \
  --capture "$CAPTURE" --marker "$MARKER" --host 127.0.0.1 --port "$TPORT" \
  --read-frames "$READ_FRAMES" --stop-after "$STOP_AFTER" ${RETARGET:+--retarget "$RETARGET"} \
  --output-dir "$OUT/probe" 2>&1 | tee "$OUT/probe_log.txt"
rc=${PIPESTATUS[0]}; set -e
echo "probe-exit=$rc out=$OUT"
