#!/usr/bin/env bash
# Card 98 hybrid step (2) — write_form_value_xtest end-to-end, VANESSA-FREE: our engine opens Справочник.Валюты
# + focuses Наименование BY NAME (protocol replay), xdotool types the value + Tab (blur), then our engine reads
# the field back. Boots our native /TESTCLIENT under Xvfb :89 + matchbox (default HOME for license). The xdotool
# input is the OS-level piece that makes the OBJECT attribute commit (protocol SetEditText cannot).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"
DISP="${DISP:-:89}"; TPORT="${TPORT:-15394}"; VALUE="${1:-ZZXTEST88}"
OUT="$REPO/runtime/protocol-research/xtest-write/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
READY="$OUT/ready"; TYPED="$OUT/typed"; rm -f "$READY" "$TYPED"
XVFB=""; WM=""; C1C=""; PROBE=""
cleanup(){ for p in "$PROBE" "$C1C" "$WM" "$XVFB"; do [ -n "$p" ] && kill -9 "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "== Xvfb $DISP + matchbox =="; Xvfb "$DISP" -screen 0 1280x1024x24 >/dev/null 2>&1 & XVFB=$!; sleep 2
export DISPLAY="$DISP"; matchbox-window-manager -use_titlebar no >/dev/null 2>&1 & WM=$!; sleep 1
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
echo "== boot native /TESTCLIENT (1cv8 thick) :$TPORT =="
"$PLAT/1cv8" ENTERPRISE /IBConnectionString "File=\"$IB\";" /N"Администратор" /TESTCLIENT -TPort "$TPORT" \
  /DisableStartupMessages /DisableStartupDialogs /Out "$OUT/tc.out" -NoTruncate >"$OUT/c.out" 2>&1 & C1C=$!
for i in $(seq 1 150); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; tail -8 "$OUT/tc.out" 2>/dev/null; exit 1; }
sleep 4; echo "client-up"
echo "== PROTOCOL: open form + focus Наименование (our engine) =="
PYTHONPATH=src python3 tools/protocol-research/demo_xtest_write_probe.py "$TPORT" "$VALUE" "$READY" "$TYPED" 17 28 25 >"$OUT/probe.log" 2>&1 & PROBE=$!
for i in $(seq 1 40); do [ -f "$READY" ] && break; sleep 1; done
[ -f "$READY" ] || { echo "ERR: probe never reached READY"; cat "$OUT/probe.log"; exit 1; }
DISPLAY="$DISP" scrot -o "$OUT/01-focused.png" 2>/dev/null
echo "== XTEST: type '$VALUE' + Tab (blur) into the focused field =="
DISPLAY="$DISP" xdotool type --delay 60 "$VALUE"; sleep 1
DISPLAY="$DISP" scrot -o "$OUT/02-typed.png" 2>/dev/null
DISPLAY="$DISP" xdotool key Tab; sleep 1
DISPLAY="$DISP" scrot -o "$OUT/03-blurred.png" 2>/dev/null
echo "== XTEST: click Записать (save -> DB) =="
DISPLAY="$DISP" xdotool mousemove 219 235 click 1; sleep 3
DISPLAY="$DISP" scrot -o "$OUT/04-saved.png" 2>/dev/null
echo "== saved window title (should become '$VALUE (Валюта)') =="
DISPLAY="$DISP" xdotool search --class 1cv8 2>/dev/null | while read w; do n=$(DISPLAY="$DISP" xdotool getwindowname "$w" 2>/dev/null); [ -n "$n" ] && echo "  wid=$w name='$n'"; done | grep -aiE "Валюта|$VALUE" | head
touch "$TYPED"
wait "$PROBE" 2>/dev/null; grep -aE "readback|RESULT|READY" "$OUT/probe.log"
echo "out=$OUT"
