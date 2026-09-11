#!/usr/bin/env bash
# Deploy a HAND-edited fixture (the embedded config DataProcessor ФикстураПротоколаTestClient) into the
# vanessa_client infobase via the manual ibcmd export/import/apply procedure (capture-free-epic-state.md §7;
# run_dev_infobase_apply is structurally workspace-locked in-session). Needs vanessa_client FREE: stops apache2
# + any TestManager/TestClient + frees the EDT workspace (SIGTERM the EDT daemon). Restarts apache on exit.
# Backs up the .1CD before apply and ABORTS before import/apply if the EDT export produced too few files.
#   TAG=card96-dialogs tools/protocol-research/deploy_fixture.sh
set -uo pipefail
IBCMD=/opt/1cv8/x86_64/8.3.27.2130/ibcmd
IB=/opt/1c-dev/vanessa_client
WS=/opt/1c-dev/vanessa_qa
PROJECT="$WS/vanessa_client"
CLI=/opt/ai-dev-suite-for-1c/edt-mcp/scripts/1cedtcli.sh
TCUSER="${TEST_CLIENT_USER:-Администратор}"
TAG="${TAG:-card96}"
OUT="${OUT:-/opt/ai-dev-suite-for-1c/qa-mcp/runtime/protocol-research/config-export-$(date +%Y%m%d-%H%M%S)}"
cfg(){ "$IBCMD" config --database-path "$IB" --user "$TCUSER" "$@"; }
cleanup(){ echo "== restart apache =="; sudo -n systemctl start apache2 && echo apache-started; }
trap cleanup EXIT

echo "== free vanessa_client: stop apache + TestManager/Client + EDT daemon =="
sudo -n systemctl stop apache2 && echo apache-stopped
pkill -x 1cv8 2>/dev/null || true; pkill -x 1cv8c 2>/dev/null || true
pkill -f 'org.eclipse.equinox.launcher' 2>/dev/null || true
sleep 3

echo "== generation-id (before) =="; cfg generation-id

echo "== backup .1CD =="; cp -p "$IB/1Cv8.1CD" "$IB/1Cv8.1CD.bak-$TAG-predeploy" && echo "backup: 1Cv8.1CD.bak-$TAG-predeploy"

echo "== EDT export config files -> $OUT =="; mkdir -p "$OUT"
EDT_WORKSPACE="$WS" xvfb-run -a "$CLI" -command "export --project $PROJECT --configuration-files $OUT" 2>&1 | tail -10
n=$(find "$OUT" -type f 2>/dev/null | wc -l)
echo "exported files: $n"
[ "$n" -gt 10 ] || { echo "ERR: export produced too few files ($n) — ABORT before import/apply"; exit 2; }

echo "== ibcmd import config files =="; cfg import "$OUT" 2>&1 | tail -6
echo "== ibcmd apply (db update) =="; cfg apply --dynamic=disable --session-terminate=force --force 2>&1 | tail -6
echo "== generation-id (after) =="; cfg generation-id
echo "== DONE =="
