#!/usr/bin/env bash
# qa-mcp container entrypoint: validate the runtime mounts, then serve the MCP over HTTP.
set -euo pipefail

QA_MCP_HOME="${QA_MCP_HOME:-/work}"
PLATFORM_ROOT="${PLATFORM_ROOT:-/opt/1cv8/current}"
INFOBASE_PATH="${INFOBASE_PATH:-/infobase}"
warn() { printf '\033[33m[qa-mcp] WARN: %s\033[0m\n' "$1" >&2; }

# Writable workdir: under --user (host-platform mode) /work must be a mounted writable dir; fall back to a
# temp dir if it is not writable so the server still starts. Give fontconfig/Xvfb a writable cache too
# (avoids the «No writable cache directories» spam when running as a non-root host user).
if ! mkdir -p "$QA_MCP_HOME/runtime" 2>/dev/null; then
  QA_MCP_HOME="$(mktemp -d)"; warn "QA_MCP_HOME not writable — using $QA_MCP_HOME (mount a writable -v ...:/work to keep evidence)"
  mkdir -p "$QA_MCP_HOME/runtime"
fi
export QA_MCP_HOME XDG_CACHE_HOME="${XDG_CACHE_HOME:-$QA_MCP_HOME/.cache}"
mkdir -p "$XDG_CACHE_HOME"

# Friendly preflight — runtime inputs the user must mount (image ships none of them).
client_bin="$PLATFORM_ROOT/1cv8"
[ -x "$client_bin" ] || warn "1C platform binary not found/executable at $client_bin — mount your 1C-for-Linux install to /opt/1cv8 (set PLATFORM_ROOT to the versioned dir) so the TestClient can launch."
[ -e "$INFOBASE_PATH" ] || warn "infobase path $INFOBASE_PATH does not exist — mount your file infobase (.1CD dir) there, or pass INFOBASE_PATH / CONNECTION_STRING."
# License can live in several places; only warn if NONE has a .lic (host-platform mode mounts ~/.1cv8 → /work/.1cv8).
have_lic=
for d in "$HOME/.1cv8/1C/1cv8/conf" "$QA_MCP_HOME/.1cv8/1C/1cv8/conf" /var/1C/licenses /opt/1cv8/conf; do
  ls "$d"/*.lic >/dev/null 2>&1 && { have_lic=1; break; }
done
[ -n "$have_lic" ] || warn "no 1C .lic visible (checked \$HOME/.1cv8, /work/.1cv8, /var/1C/licenses, /opt/1cv8/conf) — see docker/README.md Licensing; a network license server is fine too, but a soft license must be reachable or the TestClient won't start."

printf '[qa-mcp] serving MCP over %s on %s:%s (platform=%s infobase=%s)\n' \
  "${QA_MCP_TRANSPORT:-http}" "${QA_MCP_HTTP_HOST:-127.0.0.1}" "${QA_MCP_HTTP_PORT:-8000}" "$PLATFORM_ROOT" "$INFOBASE_PATH"

# `qa-native-mcp` reads QA_MCP_TRANSPORT/HTTP_HOST/HTTP_PORT and the launch env (INFOBASE_PATH/PLATFORM_ROOT/…).
exec qa-native-mcp "$@"
