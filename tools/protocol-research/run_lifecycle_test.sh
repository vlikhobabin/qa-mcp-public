#!/usr/bin/env bash
# Card 84 live test: drive the TestClient lifecycle through the MCP tools across THREE SEPARATE python
# processes — A: launch_test_client -> B: test_client_status + a native read -> C: stop_test_client —
# proving the launched client OUTLIVES the launching process (the MCP stateless pattern). No Vanessa.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
TPORT="${TPORT:-15381}"
OUT="$REPO/runtime/protocol-research/lifecycle-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
PIDFILE="$OUT/pid"
safety_cleanup(){ # belt-and-suspenders: if the MCP teardown failed, force the lab clean
  pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; pkill -x Xvfb 2>/dev/null
  sudo -n systemctl start apache2 2>/dev/null; }
trap safety_cleanup EXIT

echo "== A: launch_test_client via MCP (manage_apache, headless Xvfb) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import launch_test_client
import json
r = launch_test_client(port=$TPORT, manage_apache=True)
open('$PIDFILE','w').write(str(r['pid']))
print(json.dumps(r, ensure_ascii=False, indent=1))
" 2>&1 | tee "$OUT/A-launch.json"
PID="$(cat "$PIDFILE" 2>/dev/null || true)"
[ -n "$PID" ] || { echo 'ERR: launch did not return a pid'; exit 1; }

echo "== B: status + a native read against the launched client (a SEPARATE process) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import test_client_status, run_step
import json
st = test_client_status(pid=$PID, port=$TPORT)
print('STATUS', json.dumps(st, ensure_ascii=False))
rd = run_step('read_active_window', port=$TPORT)
step0 = (rd.get('steps') or [{}])[0]
print('READ', json.dumps({'status': rd.get('status'), 'preview': (step0.get('preview') or '')[:200]}, ensure_ascii=False))
" 2>&1 | tee "$OUT/B-status-read.json"

echo "== C: stop_test_client via MCP (restore apache) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import stop_test_client, test_client_status
import json
print('STOP', json.dumps(stop_test_client($PID, manage_apache=True), ensure_ascii=False))
print('AFTER', json.dumps(test_client_status(pid=$PID, port=$TPORT), ensure_ascii=False))
" 2>&1 | tee "$OUT/C-stop.json"
echo "out=$OUT"
