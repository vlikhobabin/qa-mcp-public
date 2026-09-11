## 1. Cache-boundary regression coverage

- [x] 1.1 Add a focused test that requires both shipped Dockerfiles to install metadata-declared dependencies before `COPY src` and to install qa-mcp source with dependency/build isolation disabled; run it against the current files and retain the expected RED result. RED: `python3 -m pytest -q tests/test_self_hosted_release_scripts.py::test_container_dependency_layers_precede_mutable_source` failed as expected because `qa-mcp-build-requirements.txt` was absent; retained as `cache-boundary-red`.

## 2. Container build restructuring

- [x] 2.1 Split the normal `Dockerfile` into metadata-only dependency installation followed by mutable source copy and dependency-free project installation.
- [x] 2.2 Split the `docker/Dockerfile.thin` protected-package flow into stable build/runtime dependency installation followed by mutable source copy and dependency-free project installation without changing compilation, encryption, secret, sanitization, or final-prefix behavior. Focused cache-boundary regression is GREEN (`cache-boundary-green`).

## 3. Verification and evidence

- [x] 3.1 Run the focused cache-boundary test and the protected release/archive test modules; record command and observed GREEN outcomes. `cache-boundary-green` passed; `python3 -m pytest -q tests/test_self_hosted_release_scripts.py tests/test_verify_protected_image_archive.py` passed 21 tests in 7.54s (`protected-release-tests`).
- [x] 3.2 Run a cold protected BuildKit build followed by a source-only warm build and retain plain-progress evidence that the dependency layer is cached while downstream source work is reevaluated. `protected-build-cold` passed from `--no-cache`; `protected-build-source-edit` passed after a harmless comment-only edit to packaged `qa_mcp` source. Its log shows protected dependency step `#13 CACHED`, while `COPY src ./src` was `DONE 0.1s` and the dependency-free project install ran again.
- [x] 3.3 Save and scan the optimized protected image, then run the external-key protected verifier so compiled imports, the 68-tool surface, encrypted bundled data, no readable protected source, and no key material remain green. `protected-image-runtime-verify` reported 68 tools, compiled private entrypoint, clean protocol `.so` leak scan, and 16 encrypted/decryptable bundled files; `protected-archive-scan` reported the 116 MB saved archive clean across layers/config/history.
- [x] 3.4 Run an equivalent focused Dockerfile ordering/install assertion in a Windows-native PowerShell contour against the same payload and retain the command/outcome; this is the configured Windows-native verification floor for this Linux-authored container change (the authorized host has Docker but no native Python launcher). `windows-cache-boundary` passed on `HISTORICAL-LAB-HOST`; reported SHA-256 values matched local `Dockerfile` and `docker/Dockerfile.thin`, and owned remote temp files were removed.

## 4. OpenSpec and handoff

- [x] 4.1 Run strict change/all OpenSpec validation, whitespace checks, and delivery-manifest scope reconciliation; summarize evidence in the card and manifest without committing raw build logs or key material. The change/capability and all 22 OpenSpec items validate strictly, `git diff --check` is clean, the evidence index validates with 11 retained entries, and manifest working-tree scope reconciliation reports no missing, extra, or mismatched paths.
