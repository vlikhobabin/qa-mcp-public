#!/usr/bin/env bash
# =============================================================================
# deliver-platform-support.sh  (qa-mcp)
#
# Case-B executor for the platform-support factory: drive a new-family / RED
# platform-support OpenSpec card through headless Codex `$opsx-deliver`
# (ff -> do -> review -> pub), unattended, in THIS qa-mcp repo.
#
# WHEN to use this (Case B): `python -m qa_mcp.platform_support probe <ver>` said
#   * case B  — an unsupported family (a genuinely new wire contour), OR
#   * a case-A build whose `validate` went RED (the wire actually moved).
# Both need real development (lab, capture, version-conditional code) — NOT the
# deterministic `validate`+`bless` path. That is what this driver hands to Codex.
#
# For each card it runs (effectively):
#     cd <qa-mcp> && <portable-wrapper> exec \
#         --skip-git-repo-check --sandbox danger-full-access \
#         -c approval_policy="never" '$opsx-deliver <card.md>'
#
# Notes / safety:
#   * `$opsx-deliver` runs the FULL pipeline incl. the `pub` phase -> scoped git
#     COMMIT + PUSH in this repo. This script is WRITE + PUSH. Review first.
#   * A genuine wire move may still need a human capture step (tcpdump + Vanessa
#     TestManager, per docs/capture-refresh-runbook.md) that headless Codex cannot
#     perform. Structure the card so the capture is pre-bundled or its `$opsx-do`
#     step calls the lab tooling; otherwise Codex will (correctly) stop at it.
#   * Sequential by design: platform work monopolizes the TestClient (port 15381),
#     Apache and the Xvfb display — never run two in parallel.
#   * CODEX_HOME is composed by bin/codex (single path): qa-mcp .codex/config.toml
#     + .codex/skills (both incl. the `opsx-deliver` and `qa-add-platform` skills)
#     + the operator's ChatGPT auth. No mutation of the tracked .codex tree.
#
# Usage:
#   scripts/deliver-platform-support.sh <card.md> [<card2.md> ...]   # deliver card(s)
#   DRY_RUN=1 scripts/deliver-platform-support.sh <card.md>          # print the resolved command only
#   scripts/deliver-platform-support.sh --list                      # show board cards, do nothing
#   CARD_TIMEOUT=5400 scripts/deliver-platform-support.sh <card.md>  # per-card wall-clock cap (s)
#
# Env knobs (defaults): SANDBOX=danger-full-access  DRY_RUN=0  STOP_ON_FAIL=1
#   CARD_TIMEOUT=  LOG_DIR=<repo>/runtime/platform-support/opsx-deliver-runs
#   SUITE_ROOT=/opt/ai-dev-suite-for-1c  LIHV_AUTH=~/.codex/auth.json
# =============================================================================
set -uo pipefail   # NOT -e: we record per-card failures and decide ourselves.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUITE_ROOT="${SUITE_ROOT:-/opt/ai-dev-suite-for-1c}"
SANDBOX="${SANDBOX:-danger-full-access}"
DRY_RUN="${DRY_RUN:-0}"
STOP_ON_FAIL="${STOP_ON_FAIL:-1}"
CARD_TIMEOUT="${CARD_TIMEOUT:-}"            # empty = no timeout
LOG_DIR="${LOG_DIR:-$REPO_ROOT/runtime/platform-support/opsx-deliver-runs}"
# The launcher owns CODEX_HOME composition (config + skills + operator auth) and the proxy env.
CODEX_LAUNCHER="${CODEX_LAUNCHER:-$REPO_ROOT/bin/codex}"
BOARD_DIRS=(1.backlog 2.todo 3.inprogress)

ts()  { date -u +%Y%m%dT%H%M%SZ; }
say() { printf '%s\n' "$*"; }
hr()  { printf '%s\n' "------------------------------------------------------------"; }

# Resolve a card basename to its absolute path anywhere on the active board columns.
resolve_card() {
  local card="$1" d p
  for d in "${BOARD_DIRS[@]}"; do
    p="$REPO_ROOT/openspec/board/$d/$card"
    [ -f "$p" ] && { printf '%s' "$p"; return 0; }
  done
  return 1
}

list_board() {
  hr; say "qa-mcp platform-support board cards (repo=$REPO_ROOT):"; hr
  local d
  for d in "${BOARD_DIRS[@]}"; do
    say "[$d]"
    ls -1 "$REPO_ROOT/openspec/board/$d/" 2>/dev/null | sed 's/^/  /' || true
  done
  hr
}

_wrap() {
  if [ -n "$CARD_TIMEOUT" ]; then timeout --signal=TERM "$CARD_TIMEOUT" "$@"; else "$@"; fi
}

# Delegate to bin/codex — the single CODEX_HOME composition path (config + skills + operator auth + proxy).
launch_codex() {
  local prompt="$1"
  ( cd "$REPO_ROOT" || exit 97
    _wrap "$CODEX_LAUNCHER" exec --skip-git-repo-check \
        --sandbox "$SANDBOX" -c approval_policy="never" "$prompt" </dev/null )
}

preflight() {
  command -v codex >/dev/null 2>&1 || { say "ERROR: codex not on PATH"; exit 2; }
  [ -x "$CODEX_LAUNCHER" ] || { say "ERROR: launcher not executable: $CODEX_LAUNCHER"; exit 2; }
  [ -f "$REPO_ROOT/.codex/config.toml" ] || { say "ERROR: no .codex/config.toml in $REPO_ROOT"; exit 2; }
  [ -r "${AI1C_CODEX_AUTH:-$HOME/.codex/auth.json}" ] || say "WARN: no readable Codex auth (run: codex login)"
  mkdir -p "$LOG_DIR"
  say "codex   : $(command -v codex)"
  say "launcher: $CODEX_LAUNCHER"
  say "login   : $(codex login status 2>/dev/null | head -1 || echo 'unknown - run: codex login')"
  say "repo    : $REPO_ROOT"
  say "logs    : $LOG_DIR"
  say "sandbox=$SANDBOX  approval_policy=never  stop_on_fail=$STOP_ON_FAIL  dry_run=$DRY_RUN  card_timeout=${CARD_TIMEOUT:-none}"
  say "WARNING: \$opsx-deliver includes the 'pub' phase -> scoped git COMMIT + PUSH in this repo."
}

main() {
  case "${1:-}" in
    --list|-l) list_board; exit 0 ;;
    -h|--help) sed -n '2,52p' "$0"; exit 0 ;;
    "") say "usage: $0 <card.md> [<card2.md> ...]   (or --list)"; exit 2 ;;
  esac

  preflight
  local -a results=()
  local i=0 card cardpath prompt log rc
  for card in "$@"; do
    i=$((i+1))
    if ! cardpath="$(resolve_card "$card")"; then
      say ">> [$i] card NOT FOUND on the board: $card (looked in ${BOARD_DIRS[*]})"
      results+=("$i NOTFOUND $card")
      [ "$STOP_ON_FAIL" = "1" ] && { _summary results[@]; exit 3; }
      continue
    fi
    prompt="\$opsx-deliver ${card}"     # literal $ kept; codex sees: $opsx-deliver <card.md>
    log="$LOG_DIR/$(ts)-$(printf '%02d' "$i")-${card%.md}.log"
    hr
    say ">> [$i] DELIVER card='$card'"
    say "   path  : $cardpath"
    say "   prompt: $prompt"
    say "   log   : $log"
    if [ "$DRY_RUN" = "1" ]; then
      say "   DRY: ( cd $REPO_ROOT && bin/codex exec --skip-git-repo-check --sandbox $SANDBOX -c approval_policy=never '$prompt' )"
      say "        bin/codex composes CODEX_HOME=runtime/codexhome (config+skills of .codex + operator auth)"
      results+=("$i DRY $card"); continue
    fi
    { say "### deliver $card @ $(ts)"; say "### prompt: $prompt"; } >"$log"
    launch_codex "$prompt" 2>&1 | tee -a "$log"
    rc=${PIPESTATUS[0]}
    say "   exit=$rc"
    if [ "$rc" -eq 0 ]; then
      results+=("$i PASS $card")
    else
      results+=("$i FAIL(rc=$rc) $card")
      [ "$STOP_ON_FAIL" = "1" ] && { hr; say "STOPPING at [$i] $card (rc=$rc). Set STOP_ON_FAIL=0 to continue."; _summary results[@]; exit "$rc"; }
    fi
  done
  _summary results[@]
}

_summary() {
  local arr=("${!1}")
  hr; say "SUMMARY ($(ts)):"; hr
  printf '%s\n' "${arr[@]}"
  hr
}

main "$@"
