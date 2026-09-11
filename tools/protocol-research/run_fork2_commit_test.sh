#!/usr/bin/env bash
# Card 80 Fork-2 live test: prove qa_mcp (no Vanessa) can WRITE a value and have it COMMIT, by replaying
# SET (input) + a FOCUS-CHANGE (the commit trigger isolated by the 2026-06-16 frame-diff) against a live
# TestClient, then reading the field back. effect_verified=true => Fork 2 is real.
#
# Boots a headless TestClient on vanessa_client (Xvfb), runs native_effect_probe.py with --commit-frames,
# restores apache. Usage: run_fork2_commit_test.sh [--commit-frames 471-474] [--no-commit]
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
set -a; [ -f .ai1c/vanessa-qa-mcp.env ] && . .ai1c/vanessa-qa-mcp.env; set +a
PLAT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"
CLIENT_BIN="${CLIENT_BIN:-$PLAT/1cv8}"
IB="${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}"
USER="${TEST_CLIENT_USER:-Администратор}"
TPORT=15381
TPL="$REPO/runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"
ACTION_CAPTURE="${ACTION_CAPTURE:-fixture-input-capture}"
MARKER="${MARKER:-PF_INPUT_PROOF}"
DEFAULT_VALUE="${DEFAULT_VALUE:-PF_EDIT_STRING_VALUE}"
LEAD_IN="${LEAD_IN:-3}"
COMMIT_FRAMES="471-474"
RESEQ=""
while [ $# -gt 0 ]; do case "$1" in
  --action-capture) ACTION_CAPTURE="$2"; shift 2;;
  --marker) MARKER="$2"; shift 2;;
  --default-value) DEFAULT_VALUE="$2"; shift 2;;
  --lead-in) LEAD_IN="$2"; shift 2;;
  --commit-frames) COMMIT_FRAMES="$2"; shift 2;;
  --no-commit) COMMIT_FRAMES=""; shift;;
  --reseq) RESEQ="--reseq"; shift;;
  *) echo "unknown arg $1" >&2; exit 2;;
esac; done
OUT="$REPO/runtime/protocol-research/fork2-commit/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"

echo "== stop apache (free vanessa_client from 8.3.27.1936) =="
sudo -n systemctl stop apache2 && echo apache-stopped
pgrep -x 1cv8 >/dev/null || rm -f "$IB"/1Cv8*.1CL 2>/dev/null

TC_PID=""
cleanup(){
  [ -n "$TC_PID" ] && { pkill -TERM -P "$TC_PID" 2>/dev/null; kill -TERM "$TC_PID" 2>/dev/null; }
  pkill -x 1cv8 2>/dev/null; pkill -x 1cv8c 2>/dev/null; pkill -f 'xvfb-run' 2>/dev/null; pkill -x Xvfb 2>/dev/null
  sleep 2
  echo "== restart apache =="; sudo -n systemctl start apache2 && echo apache-started
}
trap cleanup EXIT

echo "== boot TestClient :$TPORT under Xvfb =="
nohup xvfb-run -a "$CLIENT_BIN" ENTERPRISE /IBConnectionString "File=\"$IB\";" "/N$USER" \
  /TESTCLIENT -TPort "$TPORT" /DisableStartupDialogs /DisableStartupMessages \
  /Out "$OUT/testclient.out" -NoTruncate >"$OUT/client.out" 2>&1 &
TC_PID=$!
for i in $(seq 1 120); do ss -ltn 2>/dev/null | grep -q ":$TPORT " && break; sleep 0.5; done
ss -ltn 2>/dev/null | grep -q ":$TPORT " || { echo "ERR: $TPORT not listening"; exit 1; }
sleep 3; echo "client-up pid=$TC_PID"

echo "== run native_effect_probe (commit-frames='$COMMIT_FRAMES') =="
set +e
PYTHONPATH=src python3 tools/protocol-research/native_effect_probe.py \
  --host 127.0.0.1 --port "$TPORT" \
  --manager-templates "$TPL" \
  --action-capture "$ACTION_CAPTURE" --marker "$MARKER" --default-value "$DEFAULT_VALUE" \
  --open-frames 11-17 --value-frames 218-221 --lead-in "$LEAD_IN" \
  ${COMMIT_FRAMES:+--commit-frames "$COMMIT_FRAMES"} $RESEQ \
  --output-dir "$OUT/probe" 2>&1 | tee "$OUT/probe_log.txt"
rc=${PIPESTATUS[0]}
set -e
echo "probe-exit=$rc  out=$OUT"
