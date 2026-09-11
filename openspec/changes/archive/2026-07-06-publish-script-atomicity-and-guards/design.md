## Context

`publish_self_hosted.sh` stages local releases through a temporary directory and
then `mv`s them into the local version path. The server activation path does
not follow the same pattern: it copies directly into
`$SERVER_COMPONENT_ROOT/versions/$VERSION`, so an interrupted copy leaves a
partial final directory and the existing-path guard blocks retries.

The helper also sources `.ai1c/release.env` after parsing CLI flags, so local
defaults can silently overwrite explicit operator arguments. In `--skip-build`
mode the script trusts the user-supplied `--image-archive` while stamping the
requested image tag into `manifest.json`, which can fail later at `docker run`
time instead of during staging.

The active `protect-thin-image-saved-archive` change already owns saved-layer
protected-image scanning and currently has unarchived edits in the same publish
helper and tests. This change must preserve that work and extend it rather than
reimplementing archive scanning.

## Goals / Non-Goals

**Goals:**

- Make server-side activation retryable after interrupted copies.
- Make activated version directories read-only so out-of-band file copies are
  visible as unsupported operations.
- Preserve explicit CLI argument precedence over ignored release env defaults.
- Fail early when a supplied image archive does not contain the tag recorded in
  `manifest.json`.
- Stage all durable release handoff docs through the manifest path.
- Add focused offline tests for the guard behavior.

**Non-Goals:**

- Republish production `v0.2.3` from this automated run.
- Change protected-image archive scanning owned by
  `protect-thin-image-saved-archive`.
- Change TestClient protocol behavior, BSL, metadata, or runtime capture/replay.
- Modify the root `deploy/docker/bin/release-hardening-check.py` without a
  root-owned card or explicit cross-repo handoff.

## Decisions

**D1 - Treat release env files as defaults.**
Load `.ai/release.env` when present, then legacy `.ai1c/release.env`, before
argument parsing. Parsed CLI flags are assigned after env defaults and therefore
win. This keeps local release configuration useful while preventing accidental
or malicious override of explicit operator choices.

**D2 - Use a server-side temporary version directory.**
Copy to a sibling such as `versions/<version>.tmp.$$`, remove that temporary
directory in the activation trap, then `mv -T` it into the final version path.
The public symlink is updated only after the final version directory exists.

Alternative considered: copy into final and delete it on failure. That is less
safe because a trap cannot reliably distinguish a complete copy from a partial
copy after abrupt process termination.

**D3 - Apply immutability before public link exposure.**
Run `chmod -R a-w` on the final server version directory before flipping the
public release link. If chmod fails, activation fails before the release link
points at a mutable directory.

**D4 - Validate Docker archive tags from the archive manifest.**
Inspect `manifest.json` inside `docker save` archives, decompressing `.zst`
archives to a temporary scan file when needed, and require the requested
`IMAGE_TAG` to appear in `RepoTags`. This catches mismatches before sidecars,
manifest generation or upload.

**D5 - Make link cleanup explicit under `set -e`.**
Use an `if [ -L "$link" ]; then rm -f "$link"; fi` form rather than a final
`[ -L "$link" ] && rm -f "$link"` command. The test expression no longer
becomes the loop's status when the entry is not a symlink.

## Risks / Trade-offs

- Activation filesystem semantics vary by server filesystem -> use POSIX
  directory copy plus `mv -T` on the target Linux release host and cover the
  command flow with a temporary local server-root smoke.
- Read-only directories can complicate intentional hotfixes -> the intended
  path is republish through tooling, not hand mutation.
- Archive tag inspection adds another tar/decompression path -> keep it scoped
  to Docker `manifest.json` and share temporary cleanup with the archive scan
  pattern.
- Existing dirty work overlaps the same files -> delivery must stop before
  implementation if `protect-thin-image-saved-archive` remains unarchived.

## Verification Matrix

This is not a 1C runtime, metadata, managed-form, role, posting, report,
migration or live-data change. The applicable verification is release-tooling
evidence in qa-mcp.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `tools/release/publish_self_hosted.sh` server activation path | local server-root publish smoke with interrupted-copy simulation or equivalent focused test | shell syntax, focused pytest, local activation smoke transcript | `.artifacts/openspec/publish-script-atomicity-and-guards/<run-id>/` | required | qa-mcp | N/A for live 1C runtime because this changes release-server file activation only | operator still must republish external v0.2.3 through the fixed tooling |
