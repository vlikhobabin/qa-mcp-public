## Why

Rebuilding the protected **thin** delivery image (`docker/Dockerfile.thin`) from
current `main` fails to build. The protected build keeps three hand-maintained,
hard-coded lists/constants that must track the shipped surface but have no
automated guard, and all three drifted after the last successful thin build
(v0.3.0, `3cb6f00`):

- The leaf-module compile list (`docker/compile_modules.sh` `MODULES`) and the
  matching drop loop (`docker/Dockerfile.thin`) omit two runtime tool modules
  added afterward — `com_host.py` (host-side COM query tools, `7f4677c`) and
  `doctor.py` (`qa_mcp_doctor` diagnostics). Their readable `.py` therefore
  survives and the final "no readable source" gate aborts the build.
- The final-stage tool-count smoke asserts `67`, but the true shipped count is
  `68` — and the two other authorities already agree on `68` (the
  protected-package stage smoke and `docker/verify_protected_image.py`).

Net: any thin release/rebuild from HEAD (the successor to v0.3.0) is blocked.
This is the same class of drift as the earlier `platform_support/` fix.

## What Changes

- Add `com_host.py` and `doctor.py` to `docker/compile_modules.sh` `MODULES` and
  to the `docker/Dockerfile.thin` drop loop (kept in sync, per that file's header).
- Align the final-stage tool-count assertion to `68`, consistent with the
  protected-package stage smoke and `docker/verify_protected_image.py`.
- Make the "no readable leaf source" gate fail **loudly**, naming any offending
  leaf module, so a future drift is an actionable error instead of a cryptic
  empty-string test.

Out of scope (noted follow-ups): fully deriving the leaf-module list from the
package tree, single-sourcing the tool-count literal across the Dockerfile and
the verifier, and refreshing the stale "63 tools" number in the existing
`qa-mcp-comment-free-image` scenario prose.

## Impact

- Affected capability: `qa-mcp-comment-free-image`
- Affected code: `docker/compile_modules.sh`, `docker/Dockerfile.thin`
- Restores the ability to build and release the thin tester image from HEAD and
  makes the next added leaf module fail early with a clear, actionable message.
