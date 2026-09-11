#!/usr/bin/env bash
# Card 85 live test: launch a real TestClient on an OWNED Xvfb display, capture an OS-level screenshot via
# the MCP tool (a SEPARATE process — proving the display persists independently of the launcher), then stop.
# No Vanessa. The PNG path is printed at the end for visual inspection.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
TPORT="${TPORT:-15381}"
OUT="$REPO/runtime/protocol-research/screenshot-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
safety_cleanup(){ pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null
  pkill -f 'Xvfb :1' 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null
  sudo -n systemctl start apache2 2>/dev/null; }
trap safety_cleanup EXIT

echo "== A: launch_test_client on an owned display (auto), manage_apache =="
uv run --frozen python -c "
from qa_mcp.mcp_server import launch_test_client
import json
r = launch_test_client(port=$TPORT, manage_apache=True, display='auto')
open('$OUT/pid','w').write(str(r['pid']))
open('$OUT/xvfb_pid','w').write(str(r['xvfb_pid']))
open('$OUT/display','w').write(str(r['display']))
print(json.dumps(r, ensure_ascii=False, indent=1))
" 2>&1 | tee "$OUT/A-launch.json"
PID="$(cat "$OUT/pid" 2>/dev/null || true)"; XVFB="$(cat "$OUT/xvfb_pid" 2>/dev/null || true)"
DISPLAY_N="$(cat "$OUT/display" 2>/dev/null || true)"
[ -n "$PID" ] && [ -n "$DISPLAY_N" ] || { echo 'ERR: launch did not return pid/display'; exit 1; }

echo "== B: capture_screenshot on $DISPLAY_N (SEPARATE process) — full display + by-window =="
uv run --frozen python -c "
from qa_mcp.mcp_server import capture_screenshot
import json
full = capture_screenshot('$DISPLAY_N', out_path='$OUT/full.png')
print('FULL', json.dumps(full, ensure_ascii=False))
win = capture_screenshot('$DISPLAY_N', window='1С', out_path='$OUT/window.png')
print('WINDOW', json.dumps(win, ensure_ascii=False))
" 2>&1 | tee "$OUT/B-capture.json"

echo "== C: stop_test_client (client + owned Xvfb + apache) =="
uv run --frozen python -c "
from qa_mcp.mcp_server import stop_test_client
import json
print('STOP', json.dumps(stop_test_client($PID, xvfb_pid=${XVFB:-None}, manage_apache=True), ensure_ascii=False))
" 2>&1 | tee "$OUT/C-stop.json"
echo "PNG_FULL=$OUT/full.png"
echo "PNG_WINDOW=$OUT/window.png"
echo "out=$OUT"
