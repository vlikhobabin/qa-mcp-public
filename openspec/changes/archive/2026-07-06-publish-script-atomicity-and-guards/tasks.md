## 1. Release Defaults And Archive Guards

- [x] 1.1 Move `.ai/release.env` and `.ai1c/release.env` loading before argument parsing so CLI flags override local defaults.
- [x] 1.2 Add tests proving env-provided `VERSION` and `RELEASE_LINK_ID` cannot override explicit CLI arguments.
- [x] 1.3 Add a Docker archive tag check for `--skip-build --image-archive` before staging.
- [x] 1.4 Add a focused test proving an archive without the stamped `--image-tag` fails early with no staged version directory.

## 2. Server Activation

- [x] 2.1 Change `--activate` to copy into a temporary server version directory and `mv -T` it into `versions/<version>` only after the copy completes.
- [x] 2.2 Clean activation temporary directories on normal failure, interrupt and retry paths without removing unrelated server versions.
- [x] 2.3 Apply `chmod -R a-w` to activated version directories before the public release link is flipped.
- [x] 2.4 Rewrite public-link cleanup so non-symlink entries do not cause a non-zero exit under `set -e`.
- [x] 2.5 Add a local server-root smoke or fixture test for interrupted-copy retryability, read-only activation, and non-symlink cleanup.

## 3. Manifested Delivery Docs

- [x] 3.1 Stage `delivery/agent-install-runbook.md` through the publish helper.
- [x] 3.2 Generate `agent-install-runbook.md.sha256` and include `agent-install-runbook.md` in `manifest.json`.
- [x] 3.3 Update release docs to state that v0.2.3 must be regenerated through tooling rather than hand-mutated in place.

## 4. Verification

- [x] 4.1 Run `sh -n tools/release/publish_self_hosted.sh`.
- [x] 4.2 Run focused release tests covering `tests/test_self_hosted_release_scripts.py`.
- [x] 4.3 Run `openspec validate publish-script-atomicity-and-guards --strict`.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Record retained evidence under `.artifacts/openspec/publish-script-atomicity-and-guards/<run-id>/` when activation smoke output is produced.
