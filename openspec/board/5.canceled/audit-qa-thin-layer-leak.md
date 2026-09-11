# Fix qa-thin protected-image layer leak (protocol source + captures) + secret-mount BUNDLED_DATA_KEY

## Status
5.canceled

## Owner
unassigned

## OpenSpec Stage
canceled/superseded

## Source
- Delivery-system audit 2026-07-06 (5-agent parallel audit). Canonical report (root repo):
  `docs/audits/delivery-system-audit-2026-07-06.md` -> findings **S1 (CRITICAL)** and **H3**.

## Problem
The "protected" qa-thin image ships its own intellectual property in the clear through docker layer
history, defeating the encryption/comment-strip/non-removable-gate work of cards 122/123.

`qa-mcp/docker/Dockerfile.thin:87-90` does `COPY src ./src` + `RUN pip install .` in the **final**
build stage. That creates layers containing plaintext `qa_mcp/protocol/*.py`, readable
`license_gate.py`/`mcp_server.py`, and the **unencrypted** bundled captures/templates. The
stripping/encryption happen in *later* RUN layers (`:95-106`, `:115-140`, `:146-158`), which only
add whiteout entries -- the earlier layer blobs still carry the plaintext. `docker save`
(`qa-mcp/tools/release/publish_self_hosted.sh:163`) ships **all** layers to the tester.
`qa-mcp/docker/verify_protected_image.py` runs *inside* the container (merged filesystem), so it
passes while the layer blobs still carry everything it asserts absent.

**The already-published v0.2.3 tarball contains this** -- `tar -xf qa-mcp-thin-<v>.tar` plus
extracting the `COPY src` / `pip install` layer blob recovers the full reverse-engineered protocol
engine, plaintext captures, and readable license gate.

**H3 -- BUNDLED_DATA_KEY as build ARG.** `Dockerfile.thin:58` + `publish_self_hosted.sh:159` pass the
real key via `--build-arg`, recorded in builder-stage layer history / buildkit cache (extractable
from cache exports/intermediate images), even though it is confined out of the final image. A
committed dev-default key exists with no assert-differs guard.

## Evidence
Verified 2026-07-06 (per audit): final-stage COPY+install at `Dockerfile.thin:87-90`; strip/encrypt
at the later RUN layers; `docker save` in `publish_self_hosted.sh:163`; verifier scans the runtime
fs only. Re-verify current line numbers before editing.

## Failure scenario
A tester (or anyone who obtains the release tarball / the guessable release link) runs
`docker save qa-mcp-thin:<v> -o img.tar; tar -xf img.tar` and extracts the `COPY src` layer ->
full plaintext protocol source + unencrypted captures + license-gate logic.

## Recommendation
- Do COPY+install+strip+encrypt in an **intermediate** build stage and `COPY --from=` only the
  sanitized site-packages/venv (no source) into the final stage; or `RUN --mount=type=bind` the
  source so plaintext never lands in any final-stage layer.
- Extend `verify_protected_image.py` (or add a sibling) to scan the **layers of the saved archive**
  (`docker save` -> per-layer `tar`), not the merged runtime fs.
- Provide `BUNDLED_DATA_KEY` via `RUN --mount=type=secret`; assert the supplied key != the committed
  dev default in the publish path.
- Re-publish v0.2.3 after the fix (operator action).

## Acceptance Criteria
- [ ] Build the thin image, `docker save` it, and inspect EVERY layer tar: no layer contains
  plaintext `qa_mcp/protocol/*.py`, readable `license_gate.py`, or unencrypted captures. Encode this
  as an automated check.
- [ ] `verify_protected_image.py` (or a new sibling) scans the SAVED ARCHIVE layers and FAILS on the
  current Dockerfile, PASSES after the fix (prove both).
- [ ] The fix uses an intermediate stage (`COPY --from=` sanitized venv only) or a bind mount so
  plaintext never lands in a final-stage layer.
- [ ] `BUNDLED_DATA_KEY` is supplied via `RUN --mount=type=secret`: 0 hits in
  `docker history --no-trunc` AND 0 hits in any saved layer tar; the publish path asserts the supplied
  key != the committed dev default.
- [ ] v0.2.3 is re-published after the fix (recorded as done/assigned).

## Reviewer verification
- `docker build`, then `docker save qa-mcp-thin:<v> -o /tmp/img.tar`, `mkdir x && tar -xf /tmp/img.tar
  -C x`, and for each `x/*/layer.tar`: `tar -tf` + `grep -l` for `protocol/`/`license_gate`/capture
  filenames -> none present.
- Run the new archive-scanner on the OLD image (fails) and the NEW image (passes).
- `docker history --no-trunc qa-mcp-thin:<v> | grep -i BUNDLED_DATA_KEY` -> nothing; grep the saved
  layers for the key -> nothing.

## Scope
- In scope: `qa-mcp/docker/Dockerfile.thin`, `qa-mcp/docker/verify_protected_image.py`,
  `qa-mcp/tools/release/publish_self_hosted.sh` (secret handling + archive-scan gate).
- Out of scope: the release-link secrecy (root card) and server-side publish atomicity (see
  `audit-release-tooling-hardening`).

## Affected Repositories
- qa-mcp. Operational: re-publish v0.2.3 to the release server.

## Change Set
1. `protect-thin-image-saved-archive` - make the protected thin image archive-safe
   by removing protected plaintext from final image layers, scanning saved
   archives, and switching bundled-data key injection to BuildKit secrets.

## Change 1: `protect-thin-image-saved-archive`

### Why
The protected image currently proves only the merged runtime filesystem. Docker
release archives still include earlier final-stage layers with plaintext source
and data, and the bundled-data key is supplied through a build arg.

### Goal
The saved `qa-mcp-thin` archive is the release invariant: every layer and image
config/history record is free of readable protected source, plaintext bundled
data, and bundled-data key material before the publish helper can stage it.

### Scope
- `docker/Dockerfile.thin` final-image build flow.
- `docker/verify_protected_image.py` saved-archive scanner.
- `tools/release/publish_self_hosted.sh` secret handling and archive-scan gate.
- Focused tests and OpenSpec specs for the protected release archive contract.

### Acceptance
- The fixed Dockerfile never copies plaintext protected source/data into a final
  image layer.
- The archive scanner fails on a deliberately leaky/current-style saved archive
  and passes on the fixed archive.
- `BUNDLED_DATA_KEY` is provided through a BuildKit secret, not a build arg, and
  the publish path rejects the committed development key.
- The card records that v0.2.3 needs operator republish after the fixed archive
  gate passes.

### Depends On
- none

### Related
- `openspec/changes/protect-thin-image-saved-archive/`

### Notes For `$openspec-ff-change`
- Modified capabilities: `qa-mcp-protected-release-assets` and
  `qa-mcp-protocol-lab`.
- This is Docker/release tooling only; 1C runtime matrix rows are not
  applicable except as explicit N/A rationale in `design.md`.

## Related
- root repo: `docs/audits/delivery-system-audit-2026-07-06.md`
- `qa-mcp/docker/Dockerfile.thin`, `qa-mcp/docker/verify_protected_image.py`,
  `qa-mcp/tools/release/publish_self_hosted.sh`
- cards 122/123 (encryption / comment-free build / non-removable gate)
- `openspec/changes/protect-thin-image-saved-archive/`

## Result
Canceled/superseded during 2026-08-01 alpha-release triage.

The original source/key layer leak investigation produced valid hardening that
must stay: the image must not ship readable protected source, plaintext bundled
data or runtime key material. However, the remaining work recorded on this card
was coupled to the old product-license model: bootstrap key wiring through a
license lease, `QA_MCP_LICENSE_GATE=1`, broker activation and signed re-cut tied
to entitlement enforcement.

Operator decision 2026-08-01: qa-mcp is a free component both standalone and in
the suite. No product-license check or control is allowed at startup, runtime or
update time. The remaining security/cache work is now split into:

- `openspec/board/2.todo/remove-product-license-gate-for-free-qa-mcp.md`
  for removing/neutralizing license gate, broker and bootstrap activation.
- `openspec/board/2.todo/optimize-container-dependency-layers.md` for protected
  image dependency-layer/cache hygiene while preserving no-readable-source and
  no-key-in-image invariants.

Historical RCA/evidence below is retained as audit trail; do not use this card
as the delivery source for the current release.

The bug that was found and fixed: the bundled-data AES key was
build-injected into `_bundled_crypto.py` as `_EMBEDDED_KEY_B64` and the module is compiled to a
`.so`; nuitka compilation does NOT hide string constants, so the key survives VERBATIM as a plain
string in `_bundled_crypto.cpython-312-x86_64-linux-gnu.so`. Anyone with the shipped image recovers
it with `strings _bundled_crypto*.so | grep -oE '[A-Za-z0-9+/]{43}='`, then decrypts every bundled
capture/IP. Definitively proven 2026-07-06: a `--no-cache` build with a KNOWN key
(`az82Up…cWcw=`) -> `grep -F` finds that exact key in the `.so`; the project scanner
(`verify_protected_image.py --key-env`) independently flags it: "bundled-data key bytes found in
layer …_bundled_crypto…so". Log: docs/retro/opsx-deliver-runs/20260706T*-thin-leak-DEFINITIVE.log.

RETRACTION: the earlier "GREEN" (commit 8243adb, card->4.done) was a FALSE POSITIVE. BuildKit does
not include `--secret` content in its layer cache key, so the confirmation proof reused a cached
secret layer built with a DIFFERENT key while the scanner searched for the current key -> spurious
"clean". The pre-fix `qa-mcp-thin` v0.2.3 and v0.2.4 have the same issue (identical embed->compile
flow), BUT (operator-confirmed 2026-07-06) they were staged on the release server and NEVER
distributed/handed to any tester — so there is NO external exposure. They are simply superseded by the
fixed build and must not be handed out; no revocation/incident is needed.

The `--secret` change (key no longer in build-args/history) and the archive scanner are both good
and should stay — the scanner CORRECTLY blocked the v0.3.0 publish. The unmet AC is "key/IP not
recoverable from the shipped image": that is not achievable while the image self-decrypts with an
embedded key (whitebox-crypto problem). A real fix needs a design decision (see Next) — do NOT
publish any thin image until it is resolved.

## Next
none.

Historical 2026-07-06 decision, superseded by the 2026-08-01 no-license policy:
**runtime key from OUTSIDE the image** — ship the ENCRYPTED bundled IP but NO key; the decryption key arrives at runtime (image alone cannot decrypt, so `strings` yields
nothing). Re-plan `protect-thin-image-saved-archive` (or a successor change) to this model:

- **Choke point:** `src/qa_mcp/protocol/_bundled_crypto.py::_embedded_key()` — stop reading a build-
  injected `_EMBEDDED_KEY_B64`; instead resolve the key at runtime from an external source.
- **Key source (MVP):** `BUNDLED_DATA_KEY` env supplied at `docker run` (delivered out-of-band by
  `delivery/bootstrap.ps1` / install, like the minisign public key). **Upgrade path:** deliver the key
  via the existing license broker lease (`ai1c-license`, schema `ai1c.license.check.output.v1`), so a
  valid license is required to decrypt (no license ⇒ no key ⇒ no IP). Prefer wiring the lease path.
- **Build:** `docker/Dockerfile.thin` keeps the `--secret` mount ONLY to encrypt the bundled data at
  build time (`encrypt_bundled.py`); it must NOT bake the key into `_bundled_crypto` or any layer. The
  encryption key used at build == the key delivered at runtime (out-of-band), rotated per release.
- **Publish:** `publish_self_hosted.sh` no longer bakes/needs the key in the image; the archive scanner
  must find NO key in any layer (that becomes the pass condition).
- **Runtime failure mode:** missing/wrong key ⇒ clean, diagnostic failure with NO plaintext IP served.

### Revised acceptance (replaces the old "0 hits" that a self-decrypting image can't meet)
- [x] A fresh **`--no-cache` build with a KNOWN key** ⇒ that key is ABSENT from every layer/.so
  (`grep -F` on the extracted `.so` AND `verify_protected_image.py --key-env` both clean). Verified
  2026-07-06 (MVP commit 1f9cec3). A new in-Dockerfile build-guard also fails the build if the key
  appears in the compiled `.so`.
- [x] The shipped image contains only ENCRYPTED bundled data; with NO key at runtime, the provider
  serves no bundled IP and fails cleanly (RuntimeError, not ciphertext passthrough). Verified.
- [x] With the correct runtime key (`BUNDLED_DATA_KEY_FILE`/`BUNDLED_DATA_KEY`), decryption works
  end-to-end (bundled capture decrypted: 28 frames). Verified.
- [x] `--secret` build mount + archive scanner retained (scanner now PASSES because no key ships).
- [ ] DELIVERY (remaining): wire the key into `delivery/bootstrap.ps1` (pass at `docker run`), then
  upgrade to license-lease delivery via `ai1c-license` (no license ⇒ no key ⇒ no IP).
- [ ] Re-cut/publish a signed release from the fixed image (supersedes the never-distributed
  v0.2.3/v0.2.4).

- Operator note: v0.2.3/v0.2.4 were staged but NEVER distributed (no external exposure) — do not hand
  them out; the fixed v0.3.0 supersedes them. Separately, rotate `qa-mcp/vlikhobabin.key` (a plaintext
  GitHub PAT in the working tree, gitignored/not committed).

## Log
- 2026-07-06 card created from the delivery-system audit (findings S1, H3).
- 2026-07-06 `$opsx-ff`: decomposed to one apply-ready change,
  `protect-thin-image-saved-archive`; card moved to `2.todo`; specs added for
  saved-archive scanning and BuildKit secret key injection.
- 2026-07-06 `$opsx-do`: moved to `3.inprogress`; implementation started.
- 2026-07-06 `$opsx-do`: Dockerfile, archive verifier, release helper,
  workflow, docs and focused tests implemented. Offline gates passed
  (`718 passed`; smoke `2 passed`; OpenSpec strict validation clean). Safety
  stop before sync/archive: Docker build proof blocked because `docker buildx`
  is not installed (`.artifacts/openspec/protect-thin-image-saved-archive/20260706T144900Z/docker-build.log`).
- 2026-07-06 WIP committed (86d6f2d) to preserve the implementation while the buildx proof was pending.
- 2026-07-06 FINALIZED (LATER RETRACTED): installed `docker-buildx` 0.30.1, ran a BuildKit
  `--secret` build + archive-scan that reported GREEN, archived the change, moved card to 4.done.
- 2026-07-06 REOPENED (4.done -> 3.inprogress): while cutting v0.3.0 for republish, the publish
  gate FAILED — the real per-build key is present in `_bundled_crypto.so`. Root-caused the false
  GREEN to BuildKit `--secret` layer caching (proof reused a cached layer built with a different
  key). Confirmed definitively with a `--no-cache` known-key build (`grep -F` finds the exact key
  in the `.so`) and reproduced on published v0.2.3/v0.2.4. S1 is UNRESOLVED. No thin image published.
  Fix now needs a key-model design decision (see Result/Next). The `--secret` mount + archive scanner
  are kept; the scanner correctly caught this.
- 2026-07-06 DECISION (operator): runtime key from OUTSIDE the image (encrypted IP shipped, key supplied
  at runtime). Recorded on the card (commit 8cd43bf).
- 2026-07-06 MVP IMPLEMENTED + VERIFIED (commit 1f9cec3): `_bundled_crypto._embedded_key()` reads the
  key at runtime (`BUNDLED_DATA_KEY_FILE`/`BUNDLED_DATA_KEY`); `Dockerfile.thin` no longer bakes the key
  and a build-guard fails the build if the key reaches the `.so`; added runtime-key tests. Verified with
  a `--no-cache` known-key build: key ABSENT from the `.so`, archive scanner clean, runtime WITH key
  decrypts (28 frames), runtime WITHOUT key fails cleanly; 38 crypto/bundled tests pass. S1 leak (key
  recoverable from the shipped image) is RESOLVED. Remaining before 4.done: bootstrap key delivery +
  license-lease upgrade + signed re-cut/publish + revoke leaky v0.2.3/v0.2.4.
- **2026-07-07 UPDATE:** all four "remaining before 4.done" delivery items above are now **DONE** via the
  v0.3.0 release: bootstrap delivers `-BundledDataKey` to a private 0600 secret-file volume; license gate ON;
  signed v0.3.0 published (and re-cut today for the BOM fix); leaky v0.2.x links revoked (public/ carries only
  the current v0.3.0 link, `…5f75994…`→404). See [[qa-mcp-standalone-release-proven]].
  **The ONE thing left to close this card = the H3 plaintext-source LAYER leak** (title's "protocol source +
  captures"): confirm whether `Dockerfile.thin` was restructured so `COPY src` + `pip install` happen in an
  **earlier build stage** (so the FINAL stage carries no plaintext protocol `.py`/captures layer blobs), OR
  whether `verify_protected_image.py` still only checks the MERGED filesystem while the earlier-layer blobs
  still ship the plaintext. Verify with `docker save … | tar -x` layer inspection, restructure if needed,
  then → `4.done`. (Key leak = closed; source-in-layers = verify/restructure.)
- 2026-08-01 canceled as a delivery card because its remaining plan depends on
  qa-mcp product-license enforcement, which is no longer allowed. Security
  invariants move to the new no-license/license-removal and protected-layer
  hygiene cards.
