#!/usr/bin/env bash
# Card 98 hybrid step (1) — boot OUR native /TESTCLIENT (no Vanessa) under Xvfb :89 + matchbox, replay the demo
# open+focus frames via the engine, and screenshot to confirm the form renders (so xdotool has a focused control
# to type into for step 2). Uses 1cv8c thin (matches the genuine capture's client) against demo_1_0_41_3.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"
DISP="${DISP:-:89}"; TPORT="${TPORT:-15393}"; HOMED=/tmp/render-home; mkdir -p "$HOMED"
OUT="$REPO/runtime/protocol-research/render-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
XVFB=""; WM=""; C1C=""; PROBE=""
cleanup(){ for p in "$PROBE" "$C1C" "$WM" "$XVFB"; do [ -n "$p" ] && kill -9 "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "== Xvfb $DISP + matchbox =="; Xvfb "$DISP" -screen 0 1280x1024x24 >/dev/null 2>&1 & XVFB=$!; sleep 2
export DISPLAY="$DISP"; matchbox-window-manager -use_titlebar no >/dev/null 2>&1 & WM=$!; sleep 1
pgrep -x 1cv8c >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
echo "== boot native /TESTCLIENT (1cv8 thick) :$TPORT against $IB (default HOME for license) =="
"$PLAT/1cv8" ENTERPRISE /IBConnectionString "File=\"$IB\";" /N"Администратор" /TESTCLIENT -TPort "$TPORT" \
  /DisableStartupMessages /DisableStartupDialogs /Out "$OUT/tc.out" -NoTruncate >"$OUT/c.out" 2>&1 & C1C=$!
for i in $(seq 1 150); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; tail -10 "$OUT/c.out" "$OUT/tc.out" 2>/dev/null; exit 1; }
sleep 4; echo "client-up pid=$C1C"
echo "== replay open+focus (engine) and HOLD =="
PYTHONPATH=src python3 tools/protocol-research/demo_render_probe.py "$TPORT" 17 35 >"$OUT/probe.log" 2>&1 & PROBE=$!
for i in $(seq 1 30); do grep -q HOLDING "$OUT/probe.log" 2>/dev/null && break; sleep 1; done
cat "$OUT/probe.log"
sleep 4
echo "== screenshot =="; DISPLAY="$DISP" scrot -o "$OUT/render.png" 2>/dev/null && echo "saved $OUT/render.png"
echo "== windows on $DISP =="; DISPLAY="$DISP" xdotool search --class 1cv8c 2>/dev/null | while read w; do echo "  wid=$w name='$(DISPLAY=$DISP xdotool getwindowname "$w" 2>/dev/null)' $(DISPLAY=$DISP xdotool getwindowgeometry "$w" 2>/dev/null | grep -oE 'Geometry: [0-9x]+')"; done
echo "out=$OUT"
