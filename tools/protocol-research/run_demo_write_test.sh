#!/usr/bin/env bash
# Card 98 / change 5 (the 🚩 GATE) — live-verify the WRITE path on a 2nd (real, non-fixture) config: boot a
# FRESH demo_1_0_41_3 TestClient and replay the genuine demo write capture with a RETARGETED value, then
# verify commit (read-back) via the shipped write_form_value. demo_1_0_41_3 is NOT apache-published, so
# apache stays up. Port :15392 so it never clashes with the :15381 fixture / :15382 read-probe harnesses.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"; CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${IB:-/opt/1c-dev/demo_1_0_41_3}"; TPORT="${TPORT:-15392}"; NUSER="${NUSER:-Администратор}"
NEWVAL="${NEWVAL:-ZZGATEOK26}"
OUT="$REPO/runtime/protocol-research/demo-write-test/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
pkill -9 -x 1cv8c 2>/dev/null; sleep 1
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null
NARG=(); [ -n "$NUSER" ] && NARG=("/N$NUSER")
TC_PID=""
cleanup(){ [ -n "$TC_PID" ] && { pkill -TERM -P "$TC_PID" 2>/dev/null; kill -TERM "$TC_PID" 2>/dev/null; }
  pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; sleep 1; }
trap cleanup EXIT
echo "== boot FRESH demo_1_0_41_3 TestClient :$TPORT (user='$NUSER') =="
nohup xvfb-run -a "$CLIENT_BIN" ENTERPRISE /IBConnectionString "File=\"$IB\";" "${NARG[@]}" \
  /TESTCLIENT -TPort "$TPORT" /DisableStartupDialogs /DisableStartupMessages \
  /Out "$OUT/testclient.out" -NoTruncate >"$OUT/client.out" 2>&1 &
TC_PID=$!
for i in $(seq 1 150); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
if ! ss -ltn 2>/dev/null | grep -q ":$TPORT "; then
  echo "ERR: $TPORT not listening. client.out / testclient.out:"; tail -15 "$OUT/client.out" "$OUT/testclient.out" 2>/dev/null; exit 1
fi
sleep 4; echo "client-up pid=$TC_PID"
echo "== demo write replay (retarget -> '$NEWVAL') =="
PYTHONPATH=src python3 tools/protocol-research/demo_write_probe.py "$TPORT" "$NEWVAL" 2>&1 | tee "$OUT/log.txt"
echo "out=$OUT"
