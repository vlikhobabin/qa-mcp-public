## 1. Add the compiled decrypt helper + key

- [x] 1.1 Added `src/qa_mcp/protocol/_bundled_crypto.py`: AES-GCM `encrypt_bytes` /
  `decrypt_bytes(blob, key=None)` + `is_encrypted(blob)` (magic `QAMCPENC1\0` +
  nonce(12) + ciphertext) + `read_decrypted_bytes/text` + `encrypt_file`. The key
  is a build-injected constant `_EMBEDDED_KEY_B64 = ""` (empty placeholder; not
  committed); in dev the data is plaintext so the helpers passthrough and never use
  it. `cryptography` is imported lazily (passthrough needs no dep).
- [x] 1.2 `cryptography` is a wheel on `python:3.13-slim`/amd64 (49.0.0, already
  transitive via mcp — confirmed present in the image). Added `cryptography>=42`
  to `pyproject.toml` dependencies as an explicit direct runtime dep.

## 2. Route `_bundled` reads through detect-and-decrypt

- [x] 2.1 `protocol/bootstrap.py:CaptureBootstrap.load`: reads `traffic.jsonl` via
  `read_decrypted_text(...).splitlines()` (transparent decrypt; plaintext passthrough).
- [x] 2.2 Routed every `_bundled` read: `native_write.py:_read_chunks` (the 2nd
  `traffic.jsonl` reader), `templates.py:ProtocolTemplates.load` (covers BOTH the
  manager-frame + value-read templates — all 7 call sites), `evidence.py:load_accepted_mappings`.
- [x] 2.3 `_bundled/__init__.py` still returns paths; decrypt happens at the read.
  No tool call-site changes (offline suite green proves it).

## 3. Build-time encrypt step

- [x] 3.1 `docker/encrypt_bundled.py` walks the installed `_bundled` tree
  (`*/captures/*/traffic.jsonl`, `*/templates/*.json`, `*/accepted_mappings.json`)
  and AES-GCM-encrypts each in place via the compiled helper's embedded key
  (idempotent); then verifies all are ciphertext AND runs a decrypt+read smoke
  (capture + template + mappings).
- [x] 3.2 Wired into `docker/Dockerfile.thin`: the key is INJECTED into
  `_bundled_crypto.py` source (sed, `grep -q` verified) BEFORE the Nuitka compile so
  it lives only in the `.so`; the final stage runs `encrypt_bundled.py` after the
  swap. Default dev/local key in the builder `ARG BUNDLED_DATA_KEY`; CI overrides via
  `--build-arg` (card `ci-nuitka-release`). `!docker/encrypt_bundled.py` added to the
  `.dockerignore` whitelist.

## 4. Verify (image smoke + lab e2e + offline)

- [x] 4.1 Image: 16/16 `_bundled` data files are ciphertext (0 plaintext; head =
  `QAMCPENC1\0…`, not JSON); no readable `.py` contains the key (grep empty). Evidence:
  `.artifacts/openspec/encrypt-bundled-data/20260627-card122-change2/verification.md`.
- [ ] 4.2 Lab e2e: from the protected image, the engine decrypts and drives a real
  client (`read_form_descriptor` live fields). **PENDING the lab session** (shared
  with `nuitka-protocol-build-stage` task 4.2). **DEFERRED — non-blocking for
  archive (offline pytest + image-build verification complete).**
- [x] 4.3 Offline `pytest` green against the plaintext dev tree (passthrough):
  `tests/test_bundled_crypto.py` 8 passed; full suite 544 passed. Real-data
  round-trip (non-mutating temp copies) + the live loaders decrypt encrypted copies.

## 5. Verification

- [x] 5.1 Acceptance confirmed (local + image): `_bundled` ships ciphertext; runtime
  decrypt drives the read path (`CaptureBootstrap.load` → 28 frames from an encrypted
  capture; build-time decrypt+read smoke on capture/template/mappings); the key is
  only in the compiled `.so` (absent from readable `.py`); dev plaintext + offline
  suite unaffected. 62 tools intact. Only the lab e2e (4.2) remains. See the
  Verification Matrix in `design.md`.
