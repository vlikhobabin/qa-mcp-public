<!--
TEMPLATE — seed board card for a Case-B platform-support job (new family / RED validate).

Do NOT deliver this file. Copy it to openspec/board/1.backlog/<NN>-<date>-platform-<FAMILY>-support.md,
replace every {{PLACEHOLDER}}, paste the RED evidence, then run:
    scripts/deliver-platform-support.sh <NN>-<date>-platform-<FAMILY>-support.md
$opsx-ff (inside $opsx-deliver) decomposes this story into apply-ready `## Change N:` sections.
-->
# {{NN}}. Platform support: {{FAMILY}} ({{VERSION}}) — new wire contour

## Status
1.backlog

## Order Index
{{NN}}

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Triggered by `python -m qa_mcp.platform_support probe {{VERSION}}` → case {{CASE}}
  ({{B = unsupported family / A-RED = supported family but validate went red}}).
- Validate-first proof: `python -m qa_mcp.platform_support validate {{VERSION}}` = RED.
  Verdict: `runtime/platform-support/{{VERSION}}/verdict.json`.
- Reference procedure: `docs/capture-refresh-runbook.md` (capture/re-stamp), `docs/platform-support.md`
  (factory overview), the 8.5 epic template [[qa-mcp-8-5-platform-support]].

## Summary
Add qa-mcp support for platform {{VERSION}}. Its validate went RED, so — unlike a wire-compatible same-family
bump — the deterministic `validate`+`bless` path does not apply: the wire (handshake or a frame offset) moved, or
{{FAMILY}} is a family qa-mcp does not yet know. This card carries the development work to bring {{VERSION}} to a
GREEN live-regression using the multi-version asset architecture, changing only what the RED evidence proves must
change.

## RED evidence (paste from the verdict)
- Failed required checks: {{FAILED_CHECKS}}
- Drift verdict: {{DRIFT_SEVERITY}} — {{DRIFT_MESSAGE}}
- First frame that diverges (if diagnosed via tools/protocol-research/compare_captures.py): {{FRAME_RANGE}}

## Scope
1. **Family declaration (if new):** add `{{FAMILY}}` to `SUPPORTED_VERSION_KEYS` in
   `src/qa_mcp/_bundled/__init__.py`; create the `src/qa_mcp/_bundled/{{FAMILY}}/` slot; mirror the family
   policy in `delivery/bootstrap.ps1` (parity test `tests/test_bootstrap_platform_selection.py`).
2. **Diagnose the RED:** if it is only a version-string rejection at the handshake, it is already handled
   generically (`resolve_synth_platform_version`) — re-check the env wiring first. If a frame genuinely moved,
   localize it with `tools/protocol-research/compare_captures.py` / `analyze_capture.py`.
3. **Lab + capture (only for a genuine wire move):** stand up the {{FAMILY}} lab per
   `docs/capture-refresh-runbook.md` (convert a throwaway copy of the fixture IB with `DESIGNER /UpdateDBCfg`;
   boot `/TESTCLIENT` on an explicit Xvfb display). Capture ONLY the red capability with Vanessa TestManager +
   `tcpdump` → `tools/protocol-research/pcap_to_traffic.py`. **Manual live step — a human may need to run the
   capture (license lives at `$HOME/.1cv8/.../conf/*.lic`; do not override `HOME`).**
4. **Bundle + version-conditional code (only if the wire moved):** bundle the new capture into the family slot
   via `python scripts/bundle_runtime_assets.py --version {{FAMILY}} --source-*`; add any minimal
   version-keyed protocol constant.
5. **Validate + stamp:** re-run `python -m qa_mcp.platform_support validate {{VERSION}}` to GREEN, then stamp
   `config/protocol-capture-manifest-{{FAMILY}}.json` (`python -m qa_mcp.regression.versioning --stamp
   --version {{FAMILY}} --platform-root /opt/1cv8/x86_64/{{VERSION}}`).
6. **Release + docs:** update the supported-build list (`README.md`, `delivery/*`), rebuild the wheel/Docker
   (`docker/Dockerfile.thin` — package-data globs ship the new slot automatically), retain one GREEN smoke
   transcript.

## Acceptance
- `python -m qa_mcp.platform_support validate {{VERSION}}` = GREEN (all required checks, incl. UI→DB write).
- `python -m qa_mcp.regression.versioning --platform-root /opt/1cv8/x86_64/{{VERSION}}` = OK.
- Full offline suite green; supported-build docs and delivery parity updated.
