#!/usr/bin/env bash
# Card 98 / change 5 (the 🚩 GATE) — boot a native TestClient against a 2ND (foreign) config and try the
# capture-free READ path against it (does the vanessa_client bootstrap establish a session there?). Default
# config = demo_1_0_41_3 (a real 1C:БСП base). NOT apache-published, so apache is left running. Port :15382 so
# it never clashes with the :15381 fixture harnesses. Creds: try /NАдминистратор (BSP demo default); override
# via NUSER="" for a no-user base.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"; TPORT="${TPORT:-15382}"; KIND="${KIND:-read_active_window}"
NUSER="${NUSER:-Администратор}"   # set NUSER="" to pass no /N (no-user base)
OUT="$REPO/runtime/protocol-research/second-config-read-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
NARG=(); [ -n "$NUSER" ] && NARG=("/N$NUSER")
TC_PID=""
cleanup(){ [ -n "$TC_PID" ] && { pkill -TERM -P "$TC_PID" 2>/dev/null; kill -TERM "$TC_PID" 2>/dev/null; }
  pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; pkill -x Xvfb 2>/dev/null; sleep 1; }
trap cleanup EXIT
echo "== boot TestClient :$TPORT under Xvfb against $IB (user='${NUSER:-<none>}') =="
nohup xvfb-run -a "$CLIENT_BIN" ENTERPRISE /IBConnectionString "File=\"$IB\";" "${NARG[@]}" \
  /TESTCLIENT -TPort "$TPORT" /DisableStartupDialogs /DisableStartupMessages \
  /Out "$OUT/testclient.out" -NoTruncate >"$OUT/client.out" 2>&1 &
TC_PID=$!
for i in $(seq 1 120); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
if ! ss -ltn 2>/dev/null | grep -q ":$TPORT "; then
  echo "ERR: $TPORT not listening — client failed to start. Tail of client.out / testclient.out:"
  tail -15 "$OUT/client.out" "$OUT/testclient.out" 2>/dev/null; exit 1
fi
sleep 3; echo "client-up pid=$TC_PID"
echo "== second_config read probe (kind=$KIND) =="
PYTHONPATH=src python3 tools/protocol-research/second_config_read_probe.py "$TPORT" "$KIND" 2>&1 | tee "$OUT/log.txt"
echo "out=$OUT"
