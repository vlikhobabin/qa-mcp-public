#!/usr/bin/env bash
# Card 86a live proof: boot a TestClient (via the card-84 MCP lifecycle) and run the capture-free
# element-addressing READ probe — read arbitrary fields by path substitution, no per-field capture. No Vanessa.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
TPORT="${TPORT:-15381}"
OUT="$REPO/runtime/protocol-research/addressing-read-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
safety_cleanup(){ pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null
  pkill -x Xvfb 2>/dev/null; sudo -n systemctl start apache2 2>/dev/null; }
trap safety_cleanup EXIT

echo "== launch TestClient :$TPORT (MCP lifecycle) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import launch_test_client
import json
r = launch_test_client(port=$TPORT, manage_apache=True)
open('$OUT/pid','w').write(str(r['pid']))
print(json.dumps({k:r[k] for k in ('pid','listening','connection')}, ensure_ascii=False))
" 2>&1 | tee "$OUT/launch.json"
PID="$(cat "$OUT/pid" 2>/dev/null || true)"; [ -n "$PID" ] || { echo 'ERR: no pid'; exit 1; }

echo "== run element-addressing READ probe =="
uv run --frozen python tools/protocol-research/element_addressing_read_probe.py "$TPORT" 2>&1 | tee "$OUT/probe.txt"
RC=${PIPESTATUS[0]}

echo "== stop TestClient =="
uv run --frozen python -c "
from qa_mcp.mcp_server import stop_test_client
import json
print(json.dumps(stop_test_client($PID, manage_apache=True), ensure_ascii=False))
" 2>&1 | tee "$OUT/stop.json"
echo "out=$OUT  probe_rc=$RC"
exit $RC
