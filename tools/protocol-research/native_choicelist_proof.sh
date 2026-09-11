#!/usr/bin/env bash
# Card 74 follow-up #1 LIVE click proof (SAFE: nav+click only; --max-ordinal stops before the write):
# boot a fresh TestClient -> replay open-list -> select-row -> click "Изменить" (open card) via the
# scenario click_button kind. No data mutation (write ordinals skipped), so no COM revert needed.
#
# Linux port of native_choicelist_proof.ps1. The protocol work is identical (native_action_scenario.py,
# which self-bootstraps src/ onto sys.path); this script is only the OS-specific launcher: Linux 1cv8
# binary, /dev/tcp port wait, backgrounded TestClient + trap-based cleanup.
#
# NOTE: native TestClient runtime parity on Linux is NOT proven yet (see AGENTS.md "Linux Migrated
# Contour" / README). The Windows .ps1 remains the proven reference. This launcher needs a local capture
# fixture and scenario JSON under runtime/protocol-research/ (gitignored) plus a working headless 1cv8
# thin client; it fails fast with a clear message when a required input is missing.
#
# Usage:
#   tools/protocol-research/native_choicelist_proof.sh [--client-bin PATH] [--infobase PATH]
#       [--port N] [--capture-dir DIR] [--scenario FILE] [--out-dir DIR]
#       [--max-ordinal N] [--keep-every-poll N] [--python CMD]
# Every option also has an env-var override (CLIENT_BIN, CLIENT_INFOBASE, TPORT, CAPTURE_DIR,
# SCENARIO_JSON, OUT_DIR, MAX_ORDINAL, KEEP_EVERY_POLL, PYTHON, TC_USER).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Pull contour defaults (PLATFORM_ROOT / INFOBASE_PATH / TEST_CLIENT_USER) from the rendered, gitignored
# profile env when present. Sourced values only feed defaults below; explicit env/flags still win.
ENV_FILE="${REPO_ROOT}/.ai1c/vanessa-qa-mcp.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a; # shellcheck disable=SC1090
    . "$ENV_FILE"; set +a
fi

# "Администратор" (kept as base64 to match the .ps1 and avoid a literal in the launcher).
DEFAULT_USER="$(printf %s '0JDQtNC80LjQvdC40YHRgtGA0LDRgtC+0YA=' | base64 -d)"

PLATFORM_ROOT="${PLATFORM_ROOT:-/opt/1cv8/x86_64/8.3.27.2130}"
CLIENT_BIN="${CLIENT_BIN:-${PLATFORM_ROOT}/1cv8}"
CLIENT_INFOBASE="${CLIENT_INFOBASE:-${INFOBASE_PATH:-/opt/1c-dev/vanessa_client}}"
TC_USER="${TC_USER:-${TEST_CLIENT_USER:-$DEFAULT_USER}}"
TPORT="${TPORT:-15381}"
CAPTURE_DIR="${CAPTURE_DIR:-${REPO_ROOT}/runtime/protocol-research/captures/fixture-choice-list-cap2}"
SCENARIO_JSON="${SCENARIO_JSON:-${REPO_ROOT}/runtime/protocol-research/choicelist_scenario.json}"
SCENARIO_PY="${REPO_ROOT}/tools/protocol-research/native_action_scenario.py"
OUT_DIR="${OUT_DIR:-}"
MAX_ORDINAL="${MAX_ORDINAL:-291}"
KEEP_EVERY_POLL="${KEEP_EVERY_POLL:-8}"
PYTHON="${PYTHON:-python3}"  # set PYTHON="uv run python" if third-party deps live only in the uv venv

usage() { sed -n '2,21p' "${BASH_SOURCE[0]}"; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --client-bin)      CLIENT_BIN="$2"; shift 2 ;;
        --infobase)        CLIENT_INFOBASE="$2"; shift 2 ;;
        --port)            TPORT="$2"; shift 2 ;;
        --capture-dir)     CAPTURE_DIR="$2"; shift 2 ;;
        --scenario)        SCENARIO_JSON="$2"; shift 2 ;;
        --out-dir)         OUT_DIR="$2"; shift 2 ;;
        --max-ordinal)     MAX_ORDINAL="$2"; shift 2 ;;
        --keep-every-poll) KEEP_EVERY_POLL="$2"; shift 2 ;;
        --python)          PYTHON="$2"; shift 2 ;;
        -h|--help)         usage; exit 0 ;;
        *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

[[ -z "$OUT_DIR" ]] && OUT_DIR="${REPO_ROOT}/runtime/protocol-research/native-choicelist-proof/$(date +%Y%m%d-%H%M%S)"

# Fail fast with actionable messages instead of a deep Python traceback.
[[ -x "$CLIENT_BIN" ]]      || { echo "ERROR: 1cv8 binary not found/executable: $CLIENT_BIN" >&2; exit 2; }
[[ -e "$CLIENT_INFOBASE" ]] || { echo "ERROR: infobase path missing: $CLIENT_INFOBASE" >&2; exit 2; }
[[ -f "$SCENARIO_PY" ]]     || { echo "ERROR: scenario driver missing: $SCENARIO_PY" >&2; exit 2; }
[[ -d "$CAPTURE_DIR" ]]     || { echo "ERROR: capture fixture missing (Linux runtime input): $CAPTURE_DIR" >&2; exit 3; }
[[ -f "$SCENARIO_JSON" ]]   || { echo "ERROR: scenario JSON missing (Linux runtime input): $SCENARIO_JSON" >&2; exit 3; }

mkdir -p "$OUT_DIR"

# Wait until the TestClient listens on the agent port (bash /dev/tcp probe; no external tools needed).
wait_port() {
    local port="$1" timeout="${2:-120}" deadline=$(( SECONDS + timeout ))
    while (( SECONDS < deadline )); do
        if (exec 3<>"/dev/tcp/127.0.0.1/${port}") 2>/dev/null; then
            exec 3>&- 2>/dev/null || true
            return 0
        fi
        sleep 0.5
    done
    return 1
}

TC_PID=""
cleanup() {
    if [[ -n "$TC_PID" ]] && kill -0 "$TC_PID" 2>/dev/null; then
        kill "$TC_PID" 2>/dev/null || true
        wait "$TC_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Boot a fresh headless TestClient bound to the agent port (needs DISPLAY for the thin client on Linux).
"$CLIENT_BIN" ENTERPRISE \
    /IBConnectionString "File=\"${CLIENT_INFOBASE}\";" \
    "/N${TC_USER}" \
    /TESTCLIENT -TPort "$TPORT" \
    /DisableStartupDialogs /DisableStartupMessages \
    /Out "${OUT_DIR}/testclient.out" -NoTruncate &
TC_PID=$!

if ! wait_port "$TPORT" 120; then
    echo "ERROR: port $TPORT not listening after 120s" >&2
    exit 1
fi
echo "testclient-listening=${TPORT}"
sleep 2

# Drive the SAFE nav+click prefix (--max-ordinal stops before any write). Mirror the .ps1: do not abort
# on a non-zero scenario exit; surface it instead.
set +e
"$PYTHON" "$SCENARIO_PY" "$CAPTURE_DIR" \
    --host 127.0.0.1 --port "$TPORT" \
    --scenario "$SCENARIO_JSON" \
    --max-ordinal "$MAX_ORDINAL" --keep-every-poll "$KEEP_EVERY_POLL" \
    --output-dir "${OUT_DIR}/choicelist" 2>&1 | tee "${OUT_DIR}/choicelist_log.txt" >/dev/null
rc=${PIPESTATUS[0]}
set -e

echo "choicelist-exit=${rc}"
echo "out-dir=${OUT_DIR}"
