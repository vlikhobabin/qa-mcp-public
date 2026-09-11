#!/usr/bin/env bash
# Card 80 (option B) — Linux capture wrapper: record manager<->client native protocol on Linux.
#
# Architecture (mirrors the Windows run_protocol_capture.ps1 essence, minimal):
#   driver --> proxy(:PROXY_PORT) --> TestClient(:CLIENT_PORT)
#   protocol_proxy.py records both directions to <capture-dir>/traffic.jsonl (read_capture_chunks format).
#
# The TestClient (thin client) needs a DISPLAY → booted under xvfb-run. The proxy + a Python driver are
# headless. The genuine 1C TestManager driver (vanessa_manager harness) is Milestone 2; for now the
# driver is any command that connects to 127.0.0.1:$PROXY_PORT (e.g. our own Python manager, to PROVE
# the pipeline). Env var PROXY_PORT / CLIENT_PORT / CAPTURE_DIR are exported into the --driver command.
#
# Usage:
#   tools/protocol-research/capture_session.sh --capture-name NAME --driver 'CMD' [opts]
#   opts: --client-port N (15381) --proxy-port N (15382) --client-bin PATH --infobase PATH
#         --user NAME --python CMD --boot-timeout SEC --no-driver (start client+proxy, wait for SIGINT)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.ai1c/vanessa-qa-mcp.env"
if [[ -f "$ENV_FILE" ]]; then set -a; . "$ENV_FILE"; set +a; fi

PLATFORM_ROOT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"
CLIENT_BIN="${CLIENT_BIN:-${PLATFORM_ROOT}/1cv8}"
CLIENT_INFOBASE="${CLIENT_INFOBASE:-${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}}"
TC_USER="${TC_USER:-${TEST_CLIENT_USER:-Администратор}}"
CLIENT_PORT="${CLIENT_PORT:-15381}"
PROXY_PORT="${PROXY_PORT:-15382}"
PYTHON="${PYTHON:-python3}"
BOOT_TIMEOUT="${BOOT_TIMEOUT:-120}"
CAPTURE_NAME=""
DRIVER_CMD=""
NO_DRIVER=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --capture-name) CAPTURE_NAME="$2"; shift 2 ;;
        --driver)       DRIVER_CMD="$2"; shift 2 ;;
        --no-driver)    NO_DRIVER=1; shift ;;
        --client-port)  CLIENT_PORT="$2"; shift 2 ;;
        --proxy-port)   PROXY_PORT="$2"; shift 2 ;;
        --client-bin)   CLIENT_BIN="$2"; shift 2 ;;
        --infobase)     CLIENT_INFOBASE="$2"; shift 2 ;;
        --user)         TC_USER="$2"; shift 2 ;;
        --python)       PYTHON="$2"; shift 2 ;;
        --boot-timeout) BOOT_TIMEOUT="$2"; shift 2 ;;
        -h|--help)      sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -n "$CAPTURE_NAME" ]] || { echo "ERROR: --capture-name required" >&2; exit 2; }
[[ "$CAPTURE_NAME" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "ERROR: bad --capture-name" >&2; exit 2; }
[[ -x "$CLIENT_BIN" ]] || { echo "ERROR: 1cv8 not executable: $CLIENT_BIN" >&2; exit 2; }
[[ -e "$CLIENT_INFOBASE" ]] || { echo "ERROR: infobase missing: $CLIENT_INFOBASE" >&2; exit 2; }

CAPTURE_DIR="${REPO_ROOT}/runtime/protocol-research/captures/${CAPTURE_NAME}"
PROXY_SCRIPT="${REPO_ROOT}/tools/protocol-research/protocol_proxy.py"
mkdir -p "$CAPTURE_DIR"
RUN_DIR="${REPO_ROOT}/runtime/protocol-research/capture-session/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_DIR"

# Check the LISTEN socket via ss (does NOT open a connection): the TestClient accepts ONE manager and
# treats a connect+close as the manager leaving, so a /dev/tcp probe would destabilize it before the
# real driver connects. ss inspects kernel socket state without connecting.
wait_listen() { local p="$1" d=$(( SECONDS + ${2:-120} ))
    while (( SECONDS < d )); do ss -ltn 2>/dev/null | grep -q ":${p} " && return 0; sleep 0.5; done; return 1; }

TC_PID=""; PROXY_PID=""
cleanup() {
    # stop the proxy FIRST (SIGTERM → flushes traffic.jsonl), then the client + its xvfb tree
    [[ -n "$PROXY_PID" ]] && kill -TERM "$PROXY_PID" 2>/dev/null && wait "$PROXY_PID" 2>/dev/null || true
    if [[ -n "$TC_PID" ]] && kill -0 "$TC_PID" 2>/dev/null; then
        pkill -TERM -P "$TC_PID" 2>/dev/null || true
        kill -TERM "$TC_PID" 2>/dev/null || true
        wait "$TC_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "=== boot TestClient (:$CLIENT_PORT) under Xvfb ==="
nohup xvfb-run -a "$CLIENT_BIN" ENTERPRISE \
    /IBConnectionString "File=\"${CLIENT_INFOBASE}\";" "/N${TC_USER}" \
    /TESTCLIENT -TPort "$CLIENT_PORT" /DisableStartupDialogs /DisableStartupMessages \
    /Out "${RUN_DIR}/testclient.out" -NoTruncate > "${RUN_DIR}/client_boot.out" 2>&1 &
TC_PID=$!
wait_listen "$CLIENT_PORT" "$BOOT_TIMEOUT" || { echo "ERROR: client port $CLIENT_PORT not up" >&2; exit 1; }
sleep 2  # let the TestClient finish warming up after the port opens (matches the proven direct-probe boots)
echo "client-listening=$CLIENT_PORT pid=$TC_PID"

echo "=== start proxy (:$PROXY_PORT -> :$CLIENT_PORT), capture -> $CAPTURE_DIR ==="
rm -f "${CAPTURE_DIR}/proxy.ready.json"
"$PYTHON" "$PROXY_SCRIPT" --listen-port "$PROXY_PORT" --target-port "$CLIENT_PORT" \
    --capture-dir "$CAPTURE_DIR" --ready-file "${CAPTURE_DIR}/proxy.ready.json" \
    > "${CAPTURE_DIR}/proxy.out" 2> "${CAPTURE_DIR}/proxy.err" &
PROXY_PID=$!
# Wait on the proxy's READY-FILE, not a TCP probe: probing :$PROXY_PORT would open a connection that the
# proxy forwards all the way to the TestClient, and the client accepts only ONE manager connection — that
# spurious connect+close consumes the slot and the real driver then gets reset.
proxy_deadline=$(( SECONDS + 30 ))
while (( SECONDS < proxy_deadline )); do [[ -f "${CAPTURE_DIR}/proxy.ready.json" ]] && break; sleep 0.3; done
[[ -f "${CAPTURE_DIR}/proxy.ready.json" ]] || { echo "ERROR: proxy ready-file not written" >&2; exit 1; }
echo "proxy-listening=$PROXY_PORT pid=$PROXY_PID"

if [[ "$NO_DRIVER" == "1" ]]; then
    echo "=== --no-driver: client+proxy up; drive 127.0.0.1:$PROXY_PORT externally, Ctrl-C to stop+flush ==="
    sleep infinity
else
    echo "=== run driver against the proxy ==="
    export PROXY_PORT CLIENT_PORT CAPTURE_DIR
    set +e
    bash -lc "$DRIVER_CMD" 2>&1 | tee "${RUN_DIR}/driver.log"
    rc=${PIPESTATUS[0]}
    set -e
    echo "driver-exit=$rc"
fi
echo "capture-dir=$CAPTURE_DIR"
echo "run-dir=$RUN_DIR"
