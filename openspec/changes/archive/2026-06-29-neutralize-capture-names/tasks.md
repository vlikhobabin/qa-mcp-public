## 1. Define the rename map

- [x] 1.1 Fix the neutral-name map for the 13 bundled dirs (collision-checked):
  `genuine-card98-demo-write`→`demo-write`, `genuine-card98-listform-read`→
  `listform-read`, `genuine-card98-nextrow`→`nextrow`,
  `genuine-card98-nextrow-flat`→`nextrow-flat`, `genuine-card98-rowbyvalue`→
  `rowbyvalue`, `genuine-card97-ch3-cellread-20260619`→`cellread`,
  `genuine-card97-ch3-report-20260619`→`report`,
  `genuine-card97-ch4-search-20260619`→`search`,
  `genuine-card97-ch4-advsearch-20260619`→`advsearch`,
  `genuine-card97-ch4-viewmode-20260619`→`viewmode`,
  `genuine-commit-conn`→`commit-conn`,
  `genuine-multiaction-clean-20260617`→`multiaction-clean`.
- [x] 1.2 Decide `tm-v1-ro-batchQ3` (leave as-is — no card#/date — or normalize to
  a clearer neutral); if renamed, update `default_capture` + every `capture_dir`
  default + the bundled dir together.
  **DECISION (D3): left as-is** — it carries no card number / capture date, so the
  spec requirement (no `card N` token, no date suffix) is already met. Leaving it
  also avoids touching the dev-only `runtime/` + `bootstrap_frames_1to3.json`
  references that name it. 12 of the 13 bundled dirs renamed.

## 2. Rename the bundled dirs

- [x] 2.1 `git mv` each of the 13 dirs under `src/qa_mcp/_bundled/8.3/captures/`
  to its neutral name (and the same in any other populated version family).
  Done: 12 dirs `git mv`'d under `8.3/captures/` (renames tracked, `traffic.jsonl`
  history preserved). `8.5` family carries no captures yet (empty slot), so no
  rename there.

## 3. Update code + test references

- [x] 3.1 Update `mcp_server.py` `capture=`/`capture_dir=` defaults,
  `_FOREGROUND_CAPTURE`, and any `resolve_capture_dir(...)` literal that names a
  renamed bundled dir.
- [x] 3.2 Update `scenario/runner.py` and the `protocol/` modules
  (`native_write.py`, `native_xtest.py`, `navigation.py`, `responses.py`) where a
  renamed bundled capture is referenced. (`navigation.py`/`responses.py` named no
  renamed-bundled capture — already clean.) Also updated `docker/encrypt_bundled.py`
  (a post-encrypt assertion named `listform-read`) so the image build stays green.
- [x] 3.3 Update any test that names a renamed bundled capture
  (`tests/test_bundled_versions.py`, `tests/test_form_descriptor.py`).
- [x] 3.4 Grep `src/` + tests for the old bundled names → zero remaining
  references (the dev-only `genuine-card90/96/97-…` defaults are out of scope).

## 4. Verification

- [x] 4.1 Offline `pytest` green (captures load + replay under the new names).
  → **546 passed** (matches the card-123 baseline; renamed captures resolve + replay).
- [x] 4.2 Grep proof: no `genuine-card9[78]` / `genuine-multiaction` /
  `genuine-commit` reference remains in the shipped bundled tree or in the
  `capture=` defaults. See the Verification Matrix in `design.md`.
  → zero old **bundled-set** tokens in `src/`+`tests/`+`docker/`; the `_bundled`
  tree has no `genuine-*` dir left. The residual `genuine-card9x` hits are all
  **dev-only, non-bundled** captures (`windowlist`, `formanalysis`, `tableread`,
  `…/traffic-selfcontained` rowops/multiselect, `card90/96`) that resolve from the
  dev `runtime/` tree and do not ship — explicitly out of scope (Non-Goal; the
  broader runtime-exposed-string scrub is card 123).
