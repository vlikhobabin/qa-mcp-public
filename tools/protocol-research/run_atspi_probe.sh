#!/usr/bin/env bash
# Card 98 — does the 1C thin client expose its UI via the Linux accessibility bus (AT-SPI)? Boots Xvfb + a
# session D-Bus + the a11y bus-launcher, launches an INTERACTIVE 1cv8c against demo_1_0_41_3 with accessibility
# enabled, then dumps the AT-SPI tree (native X11 windows too). Answers whether form elements are introspectable
# natively (vs only via the TestClient protocol), and whether editable fields expose EditableText/Action.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"
DISP="${DISP:-:88}"; HOMED=/tmp/atspi-home; mkdir -p "$HOMED"
OUT="$REPO/runtime/protocol-research/atspi-probe/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
XVFB=""; C1C=""; LAUNCHER=""; WM=""; REG=""; CTRL=""
cleanup(){ for p in "$C1C" "$CTRL" "$REG" "$LAUNCHER" "$WM" "$XVFB" "${DBUS_SESSION_BUS_PID:-}"; do [ -n "$p" ] && kill -9 "$p" 2>/dev/null; done
  for n in at-spi-bus-launcher at-spi2-registryd; do for q in $(pgrep -f "$n" 2>/dev/null); do kill -9 "$q" 2>/dev/null; done; done; }
trap cleanup EXIT

echo "== Xvfb $DISP =="; Xvfb "$DISP" -screen 0 1280x1024x24 >/dev/null 2>&1 & XVFB=$!; sleep 2
export DISPLAY="$DISP"
echo "== window manager (matchbox, auto-maximizes) =="; matchbox-window-manager -use_titlebar no >/dev/null 2>&1 & WM=$!; sleep 1
echo "== session D-Bus =="; eval "$(dbus-launch --sh-syntax)"; echo "  $DBUS_SESSION_BUS_ADDRESS"
echo "== a11y bus launcher =="; /usr/libexec/at-spi-bus-launcher --launch-immediately >/dev/null 2>&1 & LAUNCHER=$!; sleep 2
echo "  org.a11y.Bus on session bus?"; busctl --address="$DBUS_SESSION_BUS_ADDRESS" list 2>/dev/null | grep -i a11y || echo "  (not found)"
echo "== at-spi2-registryd =="; /usr/libexec/at-spi2-registryd >/dev/null 2>&1 & REG=$!; sleep 2

export NO_AT_BRIDGE=0 GNOME_ACCESSIBILITY=1 QT_ACCESSIBILITY=1 GTK_MODULES=atk-bridge ACCESSIBILITY_ENABLED=1
echo "== control GTK3 app (validates the a11y stack) =="; python3 tools/protocol-research/atspi_control.py >/dev/null 2>&1 & CTRL=$!; sleep 3
pgrep -x 1cv8c >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
echo "== launch interactive 1cv8c against $IB (a11y enabled) =="
HOME="$HOMED" "$PLAT/1cv8c" ENTERPRISE /F"$IB" /N"Администратор" /DisableStartupMessages /DisableStartupDialogs >"$OUT/client.out" 2>&1 & C1C=$!
echo "  pid=$C1C; waiting for render + a11y registration..."
for i in $(seq 1 75); do xdotool search --onlyvisible --class "" >/dev/null 2>&1 && break; sleep 1; done
sleep 12

echo "== native X11 windows (xwininfo -> file) =="; xwininfo -root -tree >"$OUT/windows.txt" 2>/dev/null
grep -aoE '0x[0-9a-f]+ "[^"]+": \("[^"]*" "[^"]*"\)[^+]*' "$OUT/windows.txt" 2>/dev/null | grep -avE '"(matchbox|1cv8c)":' | head -20
echo "  (1C-titled windows present in windows.txt: $(grep -acE 'Валют|Демонстр|приложение|Предприятие|Начальн' "$OUT/windows.txt"))"
echo "== AT-SPI tree dump =="; DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" timeout 60 python3 tools/protocol-research/atspi_dump.py 10 2>&1 | tee "$OUT/atspi.txt" | head -160
echo "out=$OUT"
