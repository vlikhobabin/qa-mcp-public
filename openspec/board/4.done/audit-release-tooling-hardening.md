# qa release tooling hardening: atomic server-side activate, download trust anchor, bootstrap secret/idempotency

## Status
4.done

## Owner
Codex

## OpenSpec Stage
published

## Source
- Delivery-system audit 2026-07-06 (5-agent parallel audit). Canonical report (root repo):
  `docs/audits/delivery-system-audit-2026-07-06.md` -> findings **H6, H7, H8**.

## Problem
A cluster of qa-mcp release-tooling issues. Grouped here because they share the publish/bootstrap
surface; each has its own verifiable acceptance criterion.

**H8 -- publish script / release-server hygiene (`qa-mcp/tools/release/publish_self_hosted.sh`)**
- `:236` server-side `cp -a "$VERSION_DIR" "$SERVER_VERSION_DIR"` copies 120+ MB directly into the
  FINAL path. The symlink flip after is atomic, but a mid-`cp` failure (disk full, Ctrl-C) leaves a
  partial `versions/<v>`, and the guard at `:234` ("server version already exists") then permanently
  blocks retry. The EXIT trap only cleans the local stage. (Local staging is done right: tmp + `mv`.)
- The live v0.2.3 was mutated after activation: `/srv/ai1c-releases/qa-mcp/versions/v0.2.3/
  agent-install-runbook.md` (+ `.sha256`) was hand-copied in 4h after `manifest.json`, is absent from
  the manifest, and is not staged by the script -- into an "immutable, append-only" version dir.
- `--skip-build` stamps `--image-tag` into the manifest (`:151-154,102`) without checking the supplied
  `--image-archive` actually contains that tag -> late `docker run` "No such image".
- `set -e` foot-gun (`:239-243`): `[ -L "$link" ] && rm -f "$link"` as the loop's last command exits
  non-zero if the final `public/` entry is a non-symlink, AFTER activation succeeded.
- Env file sourced after arg parsing (`:110-114`): a stray `VERSION=`/`RELEASE_LINK_ID=` in
  `.ai1c/release.env` silently overrides CLI args.
- Protected-asset scan is a basename tripwire, not a scanner
  (`deploy/docker/bin/release-hardening-check.py:14-34,151-167`) -- a `.1CD` inside a tar or a renamed
  dump passes. Committed samples currently fail `validate-manifests` (sha256/size drift).

**H7 -- download trust anchor (`qa-mcp/delivery/bootstrap.ps1`)**
bootstrap correctly sha256-verifies every asset against `manifest.json` before execution/`docker load`
(`:84-98,143-148,222`), but `manifest.json`/`bootstrap.ps1` are TLS-trust only, `.sha256` sidecars are
same-origin, the `.exe`/`.ps1` are unsigned, and bootstrap accepts a plain `http://` `-ReleaseBase`
(`:100-106` check emptiness only). A compromised release box / hijacked DNS+cert / leaked link -> code
execution on tester machines.

**H6 -- bootstrap secret + idempotency (`qa-mcp/delivery/bootstrap.ps1`)**
- `:176-183` bakes plaintext `/P$Password` into `$env:LOCALAPPDATA\qa-mcp-setup\launch-testclient.ps1`,
  left behind indefinitely, re-run by the `qa-mcp-testclient` scheduled task, with NO ACL (token files
  get user-only ACLs; the password file gets nothing).
- Re-run is not idempotent (`:183-190,194-201`): the success check is only "something accepts TCP on
  `$ClientPort`"; re-running with a different `-Infobase` never stops the previous TestClient; the
  stale client still bound satisfies the probe while the new client silently fails to bind;
  window-title auto-derivation grabs the first `1cv8` process.

## Evidence
Verified 2026-07-06 (per audit). Re-verify line numbers before editing.

## Failure scenario
A publish interrupted mid-`cp` wedges all future republishes of that version; a tester on a hijacked
network runs an unsigned `bootstrap.ps1` over `http://` and executes attacker code; a plaintext 1C
admin password persists on disk and is read by a backup agent / same-user malware; a re-bootstrap on a
different infobase "succeeds" against the stale client on the wrong base.

## Recommendation
- Server-side: `cp -a` to `"$SERVER_VERSION_DIR.tmp.$$"` then `mv -T`; `chmod -R a-w` version dirs
  after activation; republish/regen the mutated v0.2.3 asset through tooling.
- Verify `--image-archive` contains the stamped tag; fix the `set -e` foot-gun; source the env file
  BEFORE arg parsing (CLI wins).
- bootstrap: enforce `https://` scheme; Authenticode-sign `qa-mcp-host-agent.exe`/`ai-com-worker.exe`,
  or publish a detached minisign signature for `manifest.json` with the public key delivered
  out-of-band.
- bootstrap: delete `launch-testclient.ps1` after the client is up (or ACL + DPAPI it); detect/stop an
  existing listener / `qa-mcp-testclient` task before launch (or fail with an explicit message).

## Acceptance Criteria
- [x] Server-side activation is atomic: killing the publish mid-`cp` leaves NO partial
  `versions/<v>` and a retry still works (`.tmp.$$` + `mv -T`).
- [x] Version dirs are `chmod -R a-w` after activation; the v0.2.3 out-of-band asset is regenerated
  through tooling and present in the manifest.
- [x] `--skip-build` with an archive lacking the stamped tag fails EARLY with a clear error.
- [x] The post-activation `set -e` foot-gun cannot flip a successful publish to non-zero (test).
- [x] `.ai1c/release.env`/`.ai/release.env` cannot override an explicit CLI arg (test).
- [x] `bootstrap.ps1` refuses a plain `http://` `-ReleaseBase`.
- [x] `qa-mcp-host-agent.exe`/`ai-com-worker.exe` are Authenticode-signed OR `manifest.json` carries a
  detached minisign signature that bootstrap verifies with an out-of-band public key.
- [x] After the client is confirmed up, no plaintext `launch-testclient.ps1` password file remains
  (deleted, or ACL'd + DPAPI-protected).
- [x] Re-running bootstrap with a different `-Infobase` stops the prior TestClient or fails loudly
  (no stale-client false success).
- [ ] `release-hardening-check.py validate-manifests` passes on regenerated samples. Cross-repo follow-up:
  root-owned `deploy/docker/bin/release-hardening-check.py` scanner hardening was not edited from qa-mcp.

## Change Set
- Change 1: `publish-script-atomicity-and-guards` ->
  `openspec/changes/archive/2026-07-06-publish-script-atomicity-and-guards/`
- Change 2: `download-trust-anchor` ->
  `openspec/changes/archive/2026-07-06-download-trust-anchor/`
- Change 3: `bootstrap-secret-and-idempotency` ->
  `openspec/changes/archive/2026-07-06-bootstrap-secret-and-idempotency/`

## Reviewer verification
- Interrupt a publish (`kill` during `cp`) -> confirm clean retry.
- Point bootstrap at an `http://` base -> refused; at a tampered asset -> sha256 fails (already good).
- Confirm signing / minisign verification path; confirm no password file remains after a run.
- Re-run bootstrap on a second infobase -> prior client stopped or explicit failure.

## Change Plan Notes

## Change 1: `publish-script-atomicity-and-guards`

### Why
The publish helper can leave partial server-side version directories, accept
release env overrides over explicit CLI flags, stamp unchecked image tags into
manifests, and omit durable delivery docs from generated manifests.

### Goal
Make qa-mcp server activation retryable, immutable after publish, and guarded
before manifest/upload.

### Scope
- `tools/release/publish_self_hosted.sh`
- `tests/test_self_hosted_release_scripts.py`
- release delivery docs that describe staging and v0.2.3 regeneration

### Acceptance
- server activation copies into a temporary sibling and atomically moves into
  `versions/<version>`
- activated version directories are `chmod -R a-w`
- `.ai/release.env` / `.ai1c/release.env` cannot override explicit CLI flags
- `--skip-build` fails early when the archive does not contain the manifest tag
- non-symlink public entries do not trip `set -e` after activation
- `agent-install-runbook.md` is staged with sha256 and manifest metadata

### Depends On
- Resolved by baseline commit `86d6f2d` (`audit-qa-thin-layer-leak` /
  `protect-thin-image-saved-archive` WIP); implementation builds on that
  committed publish-script baseline.

### Related
- `openspec/changes/archive/2026-07-06-publish-script-atomicity-and-guards/`

### Notes For `$openspec-ff-change`
- Saved-archive protected-image scanning remains owned by
  `protect-thin-image-saved-archive`; do not duplicate that delta here.

## Change 2: `download-trust-anchor`

### Why
Bootstrap currently trusts manifest and sidecars only through TLS/same-origin
downloads and accepts plain HTTP release bases.

### Goal
Reject non-HTTPS release bases and authenticate `manifest.json` with a detached
trust anchor before trusting asset hashes or executing downloads.

### Scope
- `delivery/bootstrap.ps1`
- publish/signing docs and release helper changes needed to publish
  `manifest.json.minisig`
- focused bootstrap/release tests

### Acceptance
- `bootstrap.ps1` refuses plain `http://` `ReleaseBase`
- `manifest.json` has a detached signature verified with an out-of-band public
  key before asset hashes are trusted
- missing or invalid signature stops bootstrap before asset execution or
  `docker load`

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-06-download-trust-anchor/`

### Notes For `$openspec-ff-change`
- Detached manifest signing is the chosen qa-mcp-owned path; Authenticode for
  executables can remain a follow-up defense in depth.

## Change 3: `bootstrap-secret-and-idempotency`

### Why
Bootstrap leaves a plaintext password-bearing TestClient launch script on disk
and can report success against a stale TestClient listener from another
infobase.

### Goal
Make the TestClient launch helper temporary and ACL-restricted, and make reruns
fail loudly or replace owned stale state instead of silently reusing the wrong
client.

### Scope
- `delivery/bootstrap.ps1`
- focused bootstrap script tests
- Windows smoke evidence plan for scheduled-task cleanup and stale-listener
  reruns

### Acceptance
- no plaintext `launch-testclient.ps1` password helper remains after launch
  success
- launch helper cleanup also runs on failure paths
- existing `qa-mcp-testclient` task/listener state cannot produce false success
  for a different `Infobase`
- window-title derivation prefers the launched TestClient process when possible

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-06-bootstrap-secret-and-idempotency/`

### Notes For `$openspec-ff-change`
- This is TestClient launch behavior, so delivery needs either retained Windows
  smoke evidence or an explicit provider/environment gap when running from the
  Linux suite workspace.

## Scope
- In scope: `qa-mcp/tools/release/publish_self_hosted.sh`, `qa-mcp/delivery/bootstrap.ps1`, and the
  root `deploy/docker/bin/release-hardening-check.py` scan (cross-repo -- coordinate only; no root edit from
  this qa-mcp delivery).
- Out of scope: the qa-thin layer leak (own card) and the manifest-contract unification (root card).

## Affected Repositories
- qa-mcp. Cross-ref: root `audit-manifest-contract-unification`, root `audit-release-link-secrecy`.

## Related
- root repo: `docs/audits/delivery-system-audit-2026-07-06.md`
- `qa-mcp/tools/release/publish_self_hosted.sh`, `qa-mcp/delivery/bootstrap.ps1`
- `deploy/docker/bin/release-hardening-check.py`

## Result
Implemented and archived qa-mcp-owned release hardening:
- `publish_self_hosted.sh` now treats release env files as defaults, validates
  Docker archive tags, stages `agent-install-runbook.md`, requires
  `manifest.json.minisig`, activates through a temporary server version
  directory, makes activated versions read-only, and tolerates non-symlink
  public entries.
- `bootstrap.ps1` now requires HTTPS release bases, verifies
  `manifest.json.minisig` with an out-of-band minisign key before trusting
  manifest hashes, removes the sensitive TestClient launch helper after launch
  attempts, rejects ambiguous pre-existing TestClient listeners, replaces stale
  scheduled task state, and uses the launched process id for window-title
  discovery when available.
- Release docs and the `qa-mcp-self-hosted-release` spec were updated.
- Cross-repo follow-up remains for root-owned
  `deploy/docker/bin/release-hardening-check.py` archive-inner scanner hardening.
- Published in git with commit message
  `fix(release): harden self-hosted publish and bootstrap`.

## Next
- No further qa-mcp OPSX command. Track root-owned
  `deploy/docker/bin/release-hardening-check.py` scanner hardening on the root
  board.

## Log
- 2026-07-06 card created from the delivery-system audit (findings H6, H7, H8).
- 2026-07-06T14:59:55Z `$opsx-ff` created three apply-ready changes and moved
  the card to `2.todo`; implementation is gated by overlapping active
  `protect-thin-image-saved-archive` edits.
- 2026-07-06T17:13:11Z `$opsx-do` implemented, verified, synced and archived
  the three qa-mcp-owned changes. Evidence retained under
  `.artifacts/openspec/*/20260706T171311Z/`; Windows scheduled-task smoke is
  recorded as a Linux-delivery environment gap.
- 2026-07-06T17:30Z `$opsx-pub` committed the scoped qa-mcp delivery with
  message `fix(release): harden self-hosted publish and bootstrap`.
