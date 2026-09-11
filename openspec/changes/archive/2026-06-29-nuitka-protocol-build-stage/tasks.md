## 1. Add the Nuitka builder stage to `docker/Dockerfile.thin`

- [x] 1.1 Made `docker/Dockerfile.thin` multi-stage. `protocol-builder` stage
  `FROM python:3.13-slim` installs `build-essential` + `patchelf` + `pip install
  nuitka==4.1.3` (pinned to the spike-proven version) and `COPY src/qa_mcp` (the
  source package to compile).
- [x] 1.2 Per-module-compile every `qa_mcp/protocol/*.py` to a `.so` via
  `docker/compile_protocol.sh` (`python -m nuitka --module qa_mcp/protocol/<mod>.py
  --output-dir=/compiled`). **No `--include-package`** needed — relative + cross-pkg
  imports resolve at runtime against the sibling `.so` (the flag would only bloat).
  `__init__.py` is EXCLUDED: Nuitka rejects a package `__init__.py` as a `--module`
  target; it stays source (re-exports only). 17 modules compiled.
- [x] 1.3 (folded into stage 2) The compiled `.so` are emitted to `/compiled`; the
  final stage swaps them into the installed package and drops the `.py`. The
  `protocol/` dir + data files (`bootstrap_frames_1to3.json`, `assets/`) are kept.

## 2. Assemble the final thin image from the compiled package

- [x] 2.1 Final stage `FROM python:3.13-slim`: keeps the locale setup, `pip install .`,
  then `COPY --from=protocol-builder /compiled` + a swap RUN: copy the 17 `.so` into
  site-packages `qa_mcp/protocol/`, delete `protocol/*.py` (≠`__init__.py`), and
  **also** remove the build context source (`/opt/qa-mcp/src`) AND the setuptools
  `/opt/qa-mcp/build` tree (a second plaintext copy `pip install .` leaves) +
  egg-info. The `qa-native-mcp` entrypoint resolves from the installed package.
  All existing `ENV` runtime contract + `CMD` preserved.
- [x] 2.2 `mcp_server.py` and the non-protocol modules stay `.py` (only `protocol/`
  compiled). Verified present as source in the image.

## 3. Build and inspect the image

- [x] 3.1 `DOCKER_BUILDKIT=0 docker build -f docker/Dockerfile.thin -t
  qa-mcp-thin:protected .` succeeds. Image **309 MB** (vs ~261 MB unprotected:
  +17 `.so` ~15 MB + transitive `cryptography`). Build adds the Nuitka compile
  (~8 min, single-thread per module; `native_write.py` 148 KB is the slow one).
- [x] 3.2 Built-image assert: `find / -path '*/qa_mcp/protocol/*.py' !
  -name __init__.py` is EMPTY; protocol/ has 17 `.so` + `__init__.py`; data files
  (`bootstrap_frames_1to3.json`, `assets/calendar_button.png`) present.

## 4. Verify functional parity (image smoke + lab e2e)

- [x] 4.1 Local smoke: ran the image — Uvicorn started on 0.0.0.0:8000; MCP
  `initialize` → 200 (session-id) → `tools/list` → 200 with **62 tools** over HTTP;
  in-process `mcp.list_tools()` = 62. Evidence:
  `.artifacts/openspec/nuitka-protocol-build-stage/20260627-card122-change1/verification.md`.
- [ ] 4.2 Lab e2e (Windows lab `historical-user@192.0.2.202`, model-B): from the compiled
  image, `read_form_descriptor(host=host.docker.internal, port=<TPort>)` returns
  live form fields — parity with the readable build. **PENDING the lab session.**
  **DEFERRED — shared card-121 Windows-lab e2e gate; non-blocking for archive
  (offline pytest + image-build verification complete).**
- [x] 4.3 Offline `pytest` stays green (dev `.py` path untouched — no `src/` edits):
  `514 passed in 4.92s`.

## 5. Verification

- [x] 5.1 Acceptance confirmed locally: image has no readable `protocol/*.py` (only
  17 `.so` + `__init__.py`); compiled engine imports + serves the full 62-tool
  surface over HTTP; `mcp_server.py` stays `.py`; in-package data reachable; offline
  suite green. Only the lab e2e "drives a real client" (4.2) remains. See the
  Verification Matrix in `design.md`.
