#!/usr/bin/env bash
# Card 98 — live-verify the PRODUCTIZED write_form_value_xtest engine path (no Vanessa). Boots our native
# /TESTCLIENT + matchbox on Xvfb :89, then calls qa_mcp.protocol.native_xtest.write_form_value_xtest, which
# inline: protocol open+focus-by-name -> xdotool type (Unicode) -> Tab blur -> Ctrl+S save -> read-back.
# Pass a VALUE (ASCII or Cyrillic). Mirrors what the MCP tool write_form_value_xtest does.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"
DISP="${DISP:-:89}"; TPORT="${TPORT:-15394}"; VALUE="${1:-ZZPROD42}"
OUT="$REPO/runtime/protocol-research/xtest-prod/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
XVFB=""; WM=""; C1C=""; APACHE_STOPPED=""
cleanup(){ for p in "$C1C" "$WM" "$XVFB"; do [ -n "$p" ] && kill -9 "$p" 2>/dev/null; done
  [ -n "$APACHE_STOPPED" ] && sudo -n systemctl start apache2 2>/dev/null && echo "apache-restarted"; }
trap cleanup EXIT
# demo_1_0_41_3 can hold an apache OData session at 8.3.27.1936 (www-data) -> file-base version contention
# blocks our 2130 /TESTCLIENT. Free it: stop apache + clear the stale session files for the boot.
echo "== free demo from any apache/1936 session =="; sudo -n systemctl stop apache2 2>/dev/null && APACHE_STOPPED=1 && echo "apache-stopped"
echo "== Xvfb $DISP + matchbox =="; Xvfb "$DISP" -screen 0 1280x1024x24 >/dev/null 2>&1 & XVFB=$!; sleep 2
export DISPLAY="$DISP"; matchbox-window-manager -use_titlebar no >/dev/null 2>&1 & WM=$!; sleep 1
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8.1CL "$IB"/1Cv8tmp.1CL "$IB"/1Cv8tmp.1CD "$IB"/1Cv8snc.1CD 2>/dev/null
echo "== boot native /TESTCLIENT (1cv8 thick, default HOME for license) :$TPORT =="
"$PLAT/1cv8" ENTERPRISE /IBConnectionString "File=\"$IB\";" /N"Администратор" /TESTCLIENT -TPort "$TPORT" \
  /DisableStartupMessages /DisableStartupDialogs /Out "$OUT/tc.out" -NoTruncate >"$OUT/c.out" 2>&1 & C1C=$!
for i in $(seq 1 150); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; tail -8 "$OUT/tc.out" 2>/dev/null; exit 1; }
sleep 4; echo "client-up"
echo "== call write_form_value_xtest('$VALUE') (PRODUCTIZED engine path) =="
PYTHONPATH=src python3 - "$VALUE" "$TPORT" "$DISP" "$REPO" <<'PY'
import sys, json
from pathlib import Path
from qa_mcp.protocol.native_xtest import write_form_value_xtest
value, port, disp, repo = sys.argv[1], int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
r = write_form_value_xtest("genuine-card98-demo-write", value, "Наименование",
                           port=port, display=disp, save=True, repo_root=repo)
print(json.dumps(r, ensure_ascii=False))
PY
DISPLAY="$DISP" scrot -o "$OUT/saved.png" 2>/dev/null && echo "screenshot: $OUT/saved.png"
echo "out=$OUT"
