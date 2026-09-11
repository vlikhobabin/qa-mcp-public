## Context

`nuitka-protocol-build-stage` compiles `protocol/*.py` but leaves `_bundled/` (the
genuine captures + templates that encode the wire format) as plaintext JSON/JSONL
in the image. The `_bundled` path helpers live in `qa_mcp/_bundled/__init__.py`
(outside `protocol/`); the actual reads happen in `protocol/bootstrap.py`
(`CaptureBootstrap.load` opens `traffic.jsonl` and `json.loads` per line) and in
the template / accepted-mappings loaders. The decrypt logic + key must live in
compiled code so neither ships as readable `.py`.

## Goals / Non-Goals

- **Goal:** image `_bundled` is AES-GCM ciphertext; the engine decrypts in memory
  from compiled code; the key is only in the `.so`.
- **Goal:** dev `_bundled` stays plaintext; offline tests unchanged; no call-site
  churn.
- **Non-Goal:** per-release key rotation (a future option; v1 embeds one key).
- **Non-Goal:** encrypting anything outside `_bundled` (the `protocol/` in-package
  data `bootstrap_frames_1to3.json` / `assets/` is already inside the compiled
  package; encrypting it is optional and out of scope for v1).

## Decisions

- **D1 — AES-GCM, key embedded in compiled code.** A `cryptography`-based AES-GCM
  decrypt helper in a **compiled** module (folded into `protocol/`, e.g.
  `protocol/_bundled_crypto.py`) holds the key constant. After Nuitka compile the
  key is in machine code, not plaintext. Honest framing: a client-side key is
  RE-able — this raises cost, the license (card 121) is the commercial lever.
- **D2 — Detect-and-decrypt (dev/image duality).** The read helper inspects each
  file for an encryption marker (a fixed magic prefix on the ciphertext, or a
  `.enc` sidecar). Encrypted → decrypt with the embedded key; plaintext → read as
  today. So the same code path serves the plaintext dev tree and the encrypted
  image with **no call-site changes** and no repo re-encoding.
- **D3 — Route the existing reads through the helper.** `CaptureBootstrap.load`
  reads `traffic.jsonl` bytes → feed through the decrypt helper before line-splitting
  / `json.loads`. The manager-frame template, value-read template and
  accepted-mappings loaders do the same on their JSON reads. The `_bundled/__init__.py`
  helpers keep returning **paths**; the decrypt happens at the **read**, which is in
  compiled `protocol/` code.
- **D4 — Build-time encrypt step.** A small build script (run in the Dockerfile
  builder stage, later in `release.yml`) walks the installed `_bundled` tree and
  rewrites each data file as AES-GCM ciphertext with the same key the compiled
  helper embeds. The key is supplied to the build (build-arg / file) and baked into
  the compiled module — it is **not** committed to the repo.
- **D5 — Key provisioning.** v1: a single key, provided at build time and embedded
  in the compiled helper; the same key encrypts the data. Document that rotating it
  is a rebuild. (Pinning the key into the dev source is avoided — it enters only via
  the build.)

## Risks / Trade-offs

- **Key is in the binary:** RE-able like any client-side key; acceptable (cost-raising).
- **Crypto dep size:** `cryptography` adds to the thin image; acceptable, or use an
  AES-GCM implementation already available. Confirm wheel availability on
  `python:3.13-slim`/amd64.
- **Decrypt-path correctness:** mitigated by the image smoke driving a real read
  (capture replay + template + accepted-mappings all exercised) and by the offline
  suite proving the plaintext path is unbroken.
- **Two key sources of truth (encrypt step + compiled helper):** keep them reading
  one build-time key input to avoid drift.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager code | `_bundled` decrypt path in compiled `protocol/` | detect-and-decrypt read helper; loaders routed through it | offline `pytest` green on plaintext dev tree | CI / local run log | planned | qa-mcp | — |
| Delivery build | build-time AES-GCM encrypt of `_bundled` | image `_bundled` is ciphertext; key absent from readable `.py` | `file`/grep over image `_bundled` shows non-JSON; key-grep empty | image-smoke notes in `tasks.md` §4 | planned | qa-mcp | — |
| QA/TestClient runtime | decrypt-and-replay parity | engine opens a real form from decrypted data | `read_form_descriptor` live fields from the protected image (lab) | `.artifacts/openspec/encrypt-bundled-data/<run-id>/` | planned | qa-mcp | — |

Residual risk: the embedded key is recoverable by binary RE; mitigated by the
license gate (card 121) as the commercial control. Key rotation is a rebuild (v1).
