# `_bundled/8.5/` — platform 8.5 protocol assets

This is the reserved per-version slot for a **1C platform 8.5** protocol asset
set if a future 8.5 build moves the wire protocol.

Current status (epic 112, 2026-06-25; grid fallback rechecked 2026-07-06):
8.5.1.1343 was validated by replaying the existing 8.3 protocol data while the
synthesized bootstrap, foreground and full captured-replay frames declare the
live 8.5 platform version. No full 8.5 corpus was needed.

Runtime path selection makes that decision explicit: supported 8.5 requests use
the populated `_bundled/8.3` protocol-data set until this directory is populated.
Windows bootstrap also prefers a direct-covered 8.3 executable by default on a
mixed 8.3/8.5 host; an explicit 8.5 `-PlatformExe` is allowed and prints a
fallback warning.

Keep this directory empty until a validate-first run goes red and a specific 8.5
capture must be bundled.

To populate after a real protocol drift (per `docs/capture-refresh-runbook.md`):

```bash
python scripts/bundle_runtime_assets.py --version 8.5 \
    --source-captures <8.5 runtime captures dir> \
    --source-templates <8.5 manager_frame_templates.json> ...
```

then stamp `config/protocol-capture-manifest-8.5.json` via
`python -m qa_mcp.regression.versioning --stamp --platform-root <8.5 root>`.
