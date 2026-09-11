#!/usr/bin/env bash
# Card 86b live proof: capture-free WRITE+commit to arbitrary fields on ONE NativeWriteSession (open-once,
# avoiding the cross-session persistent-form desync). Boots a fresh TestClient, runs the 86b probe, stops.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
TPORT="${TPORT:-15381}"
OUT="$REPO/runtime/protocol-research/write-86b-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
safety_cleanup(){ pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null
  pkill -x Xvfb 2>/dev/null; sudo -n systemctl start apache2 2>/dev/null; }
trap safety_cleanup EXIT

echo "== launch fresh TestClient :$TPORT (MCP lifecycle) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import launch_test_client
r = launch_test_client(port=$TPORT, manage_apache=True)
open('$OUT/pid','w').write(str(r['pid']))
print('listening', r['listening'])
" 2>&1 | tee "$OUT/launch.txt"
PID="$(cat "$OUT/pid" 2>/dev/null || true)"; [ -n "$PID" ] || { echo 'ERR: no pid'; exit 1; }

echo "== 86b probe (single session, multiple fields) =="
uv run --frozen python tools/protocol-research/element_write_86b_probe.py "$TPORT" 2>&1 | tee "$OUT/probe.txt"

echo "== stop TestClient =="
uv run --frozen python -c "
from qa_mcp.mcp_server import stop_test_client
import json
print(json.dumps(stop_test_client($PID, manage_apache=True), ensure_ascii=False))
" 2>&1 | tee "$OUT/stop.json"
echo "out=$OUT"
