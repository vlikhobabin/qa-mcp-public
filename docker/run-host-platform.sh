#!/usr/bin/env bash
# Run qa-mcp using the 1C platform ALREADY INSTALLED ON THIS LINUX HOST, with the host's working license.
#
# Why this works: a 1C soft license is bound to host identity (machine-id, network, OS user). The platform is
# NOT baked into the image — it is mounted read-only — and the container runs TRANSPARENT to the host identity
# (shared network/UTS/IPC namespaces + the host /etc/machine-id + your user + your ~/.1cv8), so the host's
# license validates inside the container exactly as it does on the host. Verified end-to-end: the product
# launches the real 1cv8 /TESTCLIENT in the container and drives a live form over the protocol.
#
# Usage:
#   PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2130 INFOBASE_DIR=/opt/1c-dev/vanessa_client \
#     docker/run-host-platform.sh
#
# Then point your Agent at http://127.0.0.1:8000/mcp  (docker/mcp.json.example).
# NOTE: this transparency trick is a LINUX-host story. On a Windows host (Docker Desktop) the host 1C is a
# Windows build a Linux container cannot run, and the identity does not carry through the VM — there, use a
# network license server / HASP instead (see docker/README.md).
set -euo pipefail

IMAGE="${IMAGE:-qa-mcp:latest}"
PLATFORM_DIR="${PLATFORM_DIR:-/opt/1cv8}"                       # your 1C-for-Linux install root (holds x86_64/<ver>/1cv8)
: "${PLATFORM_ROOT:?set PLATFORM_ROOT to the versioned platform dir, e.g. /opt/1cv8/x86_64/8.3.27.2130}"
: "${INFOBASE_DIR:?set INFOBASE_DIR to your file infobase (.1CD) directory}"
ONEC_HOME="${ONEC_HOME:-$HOME/.1cv8}"                            # where your soft license lives
PORT="${PORT:-8000}"
HTTP_HOST="${QA_MCP_HTTP_HOST:-127.0.0.1}"
BEARER_TOKEN="${QA_MCP_BEARER_TOKEN:-}"
WORK="$(mktemp -d)"                                             # writable HOME + workdir for the container user

case "$HTTP_HOST" in
  127.0.0.1|localhost|::1|"[::1]") ;;
  *)
    if [ -z "$BEARER_TOKEN" ]; then
      echo "[run-host-platform] refusing non-loopback QA_MCP_HTTP_HOST=$HTTP_HOST without QA_MCP_BEARER_TOKEN" >&2
      exit 1
    fi
    ;;
esac

echo "[run-host-platform] image=$IMAGE platform=$PLATFORM_ROOT infobase=$INFOBASE_DIR user=$(id -un) http=$HTTP_HOST:$PORT"
exec docker run --rm --name qa-mcp \
  --network host --uts host --ipc host \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work -e QA_MCP_HOME=/work \
  -e QA_MCP_TRANSPORT=http -e QA_MCP_HTTP_HOST="$HTTP_HOST" -e QA_MCP_HTTP_PORT="$PORT" \
  -e QA_MCP_BEARER_TOKEN="$BEARER_TOKEN" \
  -e PLATFORM_ROOT="$PLATFORM_ROOT" -e INFOBASE_PATH=/infobase \
  -e TEST_CLIENT_USER="${TEST_CLIENT_USER:-Администратор}" -e TEST_CLIENT_PASSWORD="${TEST_CLIENT_PASSWORD:-}" \
  -v "$PLATFORM_DIR":/opt/1cv8:ro \
  -v "$INFOBASE_DIR":/infobase \
  -v "$ONEC_HOME":/work/.1cv8 \
  -v /etc/machine-id:/etc/machine-id:ro \
  -v "$WORK":/work \
  "$IMAGE"
# NB: ~/.1cv8 is mounted read-WRITE on purpose — 1C writes its session/cache state there at startup, exactly as
# it does when you run the platform natively on the host. Mounting it :ro makes 1cv8 fail to start silently.
