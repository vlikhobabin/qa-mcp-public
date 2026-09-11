## Context

The thin model-B image (`docker/Dockerfile.thin`, `python:3.13-slim`) currently
`pip install .`s the package, shipping `qa_mcp/protocol/*.py` as readable source.
The protocol engine is stdlib-only and import-clean behind `from .protocol …`, so
it can be compiled independently of the orchestration layer. A Nuitka 4.x spike
(card 122) proved per-module compilation of `protocol/*.py → *.so` works and keeps
the in-package data files reachable.

## Goals / Non-Goals

- **Goal:** the thin image ships `protocol/` as `.so` only, with full functional
  parity (server starts, full tool surface, drives a real client).
- **Goal:** zero `src/` edits — protection is a build-time transform; the dev `.py`
  stays research-complete.
- **Non-Goal:** encrypting `_bundled` data (adjacent change `encrypt-bundled-data`).
- **Non-Goal:** compiling `mcp_server.py` or other non-protocol modules (that is
  card 123's image-comment scrub).
- **Non-Goal:** the CI wiring (`ci-nuitka-release`) and model A.

## Decisions

- **D1 — Per-module compile, keep the `protocol/` dir.** Compile each
  `protocol/*.py → *.so` in place. The directory and its data files
  (`bootstrap_frames_1to3.json`, `assets/calendar_button.png`) survive, so
  `Path(__file__)`-relative loads keep working. A single-package `.so` is rejected:
  `bootstrap_synth.TEMPLATE_PATH = Path(__file__).parent / "bootstrap_frames_1to3.json"`
  no longer resolves under it.
- **D2 — Compile in a `python:3.13` builder stage.** A `.so` is Python-version +
  arch specific; the thin image is `python:3.13-slim` / linux-amd64, so the builder
  must match exactly. Multi-stage: builder (`pip install nuitka` + gcc, install the
  package, compile each `protocol/*.py`, delete the `.py`) → final (copy the
  installed `site-packages/qa_mcp` carrying the `.so`).
- **D3 — `mcp_server.py` stays `.py`.** Orchestration, not the RE crown jewel; the
  `from .protocol …` boundary is clean. Its runtime-exposed docstrings are card
  123's concern, not this one.
- **Build approach:** install the package in the builder (so `qa_mcp` is importable
  for `--include-package=qa_mcp`), run `python -m nuitka --module
  qa_mcp/protocol/<mod>.py --include-package=qa_mcp` for each module to produce the
  `.so` next to the source, then remove `protocol/*.py` from the installed package.
  The final stage copies the compiled `site-packages/qa_mcp` and re-exposes the
  `qa-native-mcp` entrypoint.
- **Verification = image-level.** The change is invisible to offline `pytest` (dev
  `.py` path); correctness is proven by building the image and driving a real
  client from it.

## Risks / Trade-offs

- **Build time:** Nuitka compiling ~18 modules adds minutes. Acceptable in CI;
  `ccache` (absent in the spike) is a later optimization, out of scope here.
- **Hidden `__file__` / data-path assumptions:** mitigated by D1 (keep the dir) and
  the image smoke that drives a real read path (`read_form_descriptor`).
- **Entrypoint / package-data resolution after compile:** verified by listing the
  tools and exercising a tool on the built image, not just by a successful build.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery build | `docker/Dockerfile.thin` multi-stage Nuitka compile | thin image ships `.so`, no `protocol/*.py` | built image: `find …/qa_mcp/protocol -name '*.py'` empty; image size recorded | image-smoke notes in `tasks.md` §4 | planned | qa-mcp | — |
| QA/TestClient runtime | compiled engine drives a real client | parity: server starts + full tool list + a real read | `read_form_descriptor` returns live fields from the compiled image (lab) | `.artifacts/openspec/nuitka-protocol-build-stage/<run-id>/` | planned | qa-mcp | — |
| Offline suite | dev `src/` `.py` path (unchanged) | green throughout | `pytest` pass count unchanged | CI / local run log | planned | qa-mcp | — |

Residual risk: image-level parity depends on the Windows lab for the full model-B
read (`host.docker.internal` → host TestClient); a local Linux smoke can prove the
server starts + lists tools + the package has no `protocol/*.py` before the lab e2e.
