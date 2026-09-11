#!/usr/bin/env bash
# Card 83 step 2 smoke: drive a Gherkin WRITE scenario end-to-end through the MCP tool
# (qa_mcp.mcp_server.run_write_scenario_tool) against a live TestClient — proves input_text steps
# route through the COMMIT-capable NativeWriteSession in the runner (no Vanessa).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"; USER="${TEST_CLIENT_USER:-Администратор}"; TPORT=15381
OUT="$REPO/runtime/protocol-research/gherkin-write-smoke/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
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
echo "== call MCP tool run_write_scenario_tool with a Gherkin .feature =="
uv run --frozen python -c "
from qa_mcp.mcp_server import run_write_scenario_tool
import json
feature = '''Функционал: native write
Сценарий: commit values from gherkin
  Когда в поле с именем 'PF_EDIT_STRING' я ввожу текст 'GHERKIN_W01'
  И в поле с именем 'PF_EDIT_STRING' я ввожу текст 'SECOND_VAL'
  Тогда в поле с именем 'PF_EDIT_STRING' я ввожу текст 'LAST'
'''
print(json.dumps(run_write_scenario_tool(port=$TPORT, feature_text=feature), ensure_ascii=False, indent=1))
" 2>&1 | tee "$OUT/smoke.json"
echo "out=$OUT"
