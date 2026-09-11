#!/usr/bin/env bash
# Debug the multi-write desync: two same-length writes on ONE client, saving responses + screenshots.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"; USER="${TEST_CLIENT_USER:-Администратор}"; TPORT=15381
OUT="$REPO/runtime/protocol-research/multiwrite-debug/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
echo "== stop apache =="; sudo -n systemctl stop apache2 && echo apache-stopped
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
TC_PID=""
cleanup(){ [ -n "$TC_PID" ] && { pkill -TERM -P "$TC_PID" 2>/dev/null; kill -TERM "$TC_PID" 2>/dev/null; }
  pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; pkill -x Xvfb 2>/dev/null
  sleep 2; echo "== restart apache =="; sudo -n systemctl start apache2 && echo apache-started; }
trap cleanup EXIT
echo "== boot TestClient :$TPORT under Xvfb =="
nohup xvfb-run -a -n 77 "$CLIENT_BIN" ENTERPRISE /IBConnectionString "File=\"$IB\";" "/N$USER" \
  /TESTCLIENT -TPort "$TPORT" /DisableStartupDialogs /DisableStartupMessages \
  /Out "$OUT/testclient.out" -NoTruncate >"$OUT/client.out" 2>&1 &
TC_PID=$!
for i in $(seq 1 120); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; exit 1; }
sleep 3; echo "client-up pid=$TC_PID"
n=0
for v in FIRSTWRITE_13 SECONDWRITE13; do
  n=$((n+1))
  echo "== write #$n '$v' =="
  PYTHONPATH=src python3 tools/protocol-research/native_write_probe.py --value "$v" \
    --host 127.0.0.1 --port "$TPORT" --output-dir "$OUT/w$n" 2>&1 | tee -a "$OUT/log.txt"
  DISPLAY=:77 scrot "$OUT/after_w$n.png" 2>/dev/null && echo "screenshot after_w$n.png"
done
echo "out=$OUT"
