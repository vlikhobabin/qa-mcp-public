## 1. Define the compile surface

- [x] 1.1 Confirm the non-protocol leaf module list to compile: `mcp_server.py`, `license_gate.py`, `data/odata.py`, `debug/{gates,measure}.py`, `regression/{checks,harness,versioning}.py`, `scenario/{actions,autofill,gherkin,model,replay,reporting,runner,smoke}.py`.
- [x] 1.2 Confirm the source-staying set: all package `__init__.py` (cannot be Nuitka-compiled). `regression/__main__.py` (the `python -m qa_mcp.regression` dev CLI) is the design's documented exception — it is DROPPED from the image, not kept (it is not a runtime/product surface; only `regression.versioning`/`harness` are imported by the server).

## 2. Extend the build-time compile

- [x] 2.1 Add `docker/compile_modules.sh` — per-module `nuitka --module` compile of the explicit non-protocol leaf list, writing each `.so` into a MIRRORED output tree (`<out>/<subpkg>/<mod>.so`).
- [x] 2.2 In `docker/Dockerfile.thin` builder stage, run `compile_modules.sh /build/qa_mcp /compiled-mods` after the protocol compile.
- [x] 2.3 In the final stage, copy each non-protocol `.so` into its subpackage dir and delete the matching readable `.py`.

## 3. Handle the source-staying wrappers

- [x] 3.1 Add `docker/strip_source.py` — an AST-based docstring + comment strip (re-emit from AST, which carries no comments; remove docstring statements). Applied in the final stage to the package `__init__.py` files on the installed copy only (dev source NOT edited). Proven code-equivalent offline (AST identical with docstrings removed).
- [x] 3.2 Drop `regression/__main__.py` from the image (the only remaining R&D token was a `vanessa` code default in the dev CLI; it cannot be compiled and is not a product surface). `regression/__init__.py` imports `harness` (compiled `.so`), so the runtime import path is intact.

## 4. Assertions in the build

- [x] 4.1 Assert no readable non-protocol leaf `.py` remains in the image (only package `__init__.py` may be `.py`).
- [x] 4.2 Assert `grep -rIE 'card [0-9]|[Vv]anessa|evidence/'` over the shipped `qa_mcp` returns zero — run AFTER `_bundled` encryption (so provenance JSON is ciphertext) and via an explicit `if grep; then exit 1` (`set -e` ignores `!`-inverted commands). `evidence/` is the path form; the bare `from .evidence import` submodule reference is a legitimate code identifier.
- [x] 4.3 Build-time smoke: the compiled `mcp_server` entrypoint imports and lists 62 tools; the license gate ships ONLY as compiled native code — asserted by on-disk `.py` absence + `nuitka_module_loader` (Nuitka reports a compiled module's `__file__`/origin as the original `.py`, so `__file__` is not a reliable signal).

## 5. Verify on the built image

- [x] 5.1 Built `qa-mcp-thin:c123`; container boots `qa-native-mcp` (Uvicorn up) and serves 62 tools over MCP HTTP (`initialize` + `tools/list` = 62 tools, 0 R&D-token leaks in runtime descriptions).
- [x] 5.2 Read-path: the compiled engine loads end-to-end (mcp_server pulls 45 protocol imports + the compiled non-protocol modules; 62 tools). A live `read_form_descriptor` drive needs a real TestClient (model-B, unavailable in this offline Linux env); the engine is the same code compiled, so read-path behavior is unchanged from the card-119/122 model-B proof.
- [x] 5.3 Image R&D-token grep = 0 and no-readable-leaf-`.py` = 0; evidence captured under `.artifacts/openspec/compile-shipped-nonprotocol-modules/20260627-card123-change2/`.
- [x] 5.4 Offline `pytest` against the dev `.py` source — 546 passed (build-time transform, no source change).
