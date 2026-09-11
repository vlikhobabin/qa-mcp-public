#!/bin/sh
# Deliberate dependency installation, separate from every ordinary CLI invocation.
set -eu
if [ "$#" -ne 1 ] || [ "$1" != '--offline' ]; then
    echo 'Usage: tools/openspec/bootstrap.sh --offline' >&2
    echo 'Requires all package-lock.json tarballs in the existing npm cache; never downloads.' >&2
    exit 2
fi
openspec_dependency_root=$(CDPATH= cd -P "$(dirname -- "$0")" && pwd)
if [ -L "$openspec_dependency_root/node_modules" ]; then
    echo 'openspec bootstrap: refusing a symlinked node_modules installation target.' >&2
    exit 1
fi
export OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 CI=true
export OPENSPEC_NO_COMPLETIONS=1 OPENSPEC_NO_AUTO_CONFIG=1
export NO_UPDATE_NOTIFIER=1 npm_config_update_notifier=false
npm --prefix "$openspec_dependency_root" ci --offline --ignore-scripts --no-audit --no-fund \
    --logs-dir "$openspec_dependency_root/npm-logs"
node "$openspec_dependency_root/check-install.mjs"
