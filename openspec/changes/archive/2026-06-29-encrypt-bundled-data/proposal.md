## Why

Compiling the protocol **code** to `.so` (change `nuitka-protocol-build-stage`)
leaves the protocol **data** in the clear. `src/qa_mcp/_bundled/` (2.2 MB: 13
genuine capture `traffic.jsonl` + the manager-frame / value-read templates +
`accepted_mappings.json`) **literally encodes the reverse-engineered wire
format** — anyone who pulls the image can read the bytes the engine replays
straight out of the JSON. Protecting the code but shipping the captures as
plaintext defeats the point.

This change encrypts the `_bundled` data **at rest in the image** and decrypts it
**in memory at runtime** from inside the compiled package, so the readable wire
data and the decryption key never ship as plaintext.

This change touches **Python manager code** (the `_bundled` loaders + a decrypt
helper) and **delivery/build config** (a build-time encrypt step); it requires
**only offline capture evidence** (the engine must still open a form from the
decrypted data) plus the image smoke. It honors the D6 principle: the **dev
`_bundled` stays plaintext** (research-complete); only the IMAGE ships ciphertext.

## What Changes

- **Build-time encrypt:** each `_bundled` data file (per-version `captures/*/traffic.jsonl`,
  `templates/*.json`, `accepted_mappings.json`) is encrypted with **AES-GCM** during
  the image build, replacing the plaintext in the image with ciphertext.
- **Runtime decrypt folded into compiled code:** a decrypt helper lives in a
  **compiled** module (inside `protocol/`, which `nuitka-protocol-build-stage`
  compiles) and holds the key; the `_bundled` loaders (`resolve_capture_dir` /
  `CaptureBootstrap.load`, the template + accepted-mappings readers) route file
  reads through it. The **key is embedded in the compiled `.so`** (machine code),
  not plaintext in the image — extracting it requires reversing the binary.
- **Transparent dev/image duality:** the loader **detects** whether a file is
  encrypted (magic header / sidecar marker) and decrypts only then; in the dev tree
  the files are plaintext and read directly. No call sites change; no `src/` data is
  re-encoded in the repo.
- The `_bundled/__init__.py` path helpers stay, but the **decrypt + key** live only
  in compiled code (folded into `protocol/`), so they never ship as readable `.py`.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: the bundled protocol **data** (`_bundled` captures,
  templates, accepted-mappings) ships **encrypted at rest** in the delivery image;
  the engine **decrypts in memory** at runtime from compiled code whose embedded
  key is never plaintext, and still opens a real form — while the dev `_bundled`
  tree stays plaintext for research.

## Impact

- **Python manager code:** a decrypt helper inside the compiled `protocol/`
  package; the `_bundled` loaders (`protocol/bootstrap.py:resolve_capture_dir` /
  `CaptureBootstrap.load`, the manager-frame + value-read template loaders, the
  accepted-mappings loader) gain a detect-and-decrypt read path. New crypto dep:
  AES-GCM (Python `cryptography`, or stdlib-compatible AES-GCM) added to the thin
  image runtime deps.
- **Delivery/build:** a build-time encrypt step in `docker/Dockerfile.thin` (and,
  later, `release.yml` via `ci-nuitka-release`).
- **No change** to the dev `_bundled` files (stay plaintext), the offline tests
  (read plaintext), the tool API or schemas.
- **Depends on** `nuitka-protocol-build-stage` (the compiled module that holds the
  key + decrypt logic). **Out of scope:** the CI wiring (`ci-nuitka-release`).
