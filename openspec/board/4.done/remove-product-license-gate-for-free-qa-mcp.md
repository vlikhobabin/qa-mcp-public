# Remove qa-mcp product license gate for free distribution

## Status
4.done

## Owner
qa-mcp

## OpenSpec Stage
published/archived

## Source
- Operator decision 2026-08-01: qa-mcp is distributed freely both standalone and
  as part of `ai for 1c`.
- Supersedes license-gated backlog/in-progress cards:
  - `openspec/board/5.canceled/bundled-data-key-from-license-broker.md`
  - `openspec/board/5.canceled/audit-qa-thin-layer-leak.md`
- Supersedes active OpenSpec work that enables product-license activation:
  `openspec/changes/license-activation-bootstrap/`.

## Summary
Remove or hard-disable qa-mcp product-license enforcement from the earliest
startup and delivery paths. The current alpha release must not activate a
license, check a lease, call `ai1c-license`, require entitlement material, or
block startup/update based on qa-mcp product licensing.

This does not change the 1C platform license requirement. TestClient still needs
a legal, working 1C platform installation/license according to 1C rules.

## Change Set
1. `short-circuit-qa-mcp-product-license-gate`
2. `remove-qa-mcp-license-bootstrap-and-image-wiring`

## Change 1: `short-circuit-qa-mcp-product-license-gate`

### Why
The opt-in startup gate is still a real denial and broker-execution path when
legacy environment variables are set, which contradicts free distribution.

### Goal
Make qa-mcp startup independent of product-license state and remove the broker
gate implementation from the Python runtime.

### Scope
- Remove or inert the `QA_MCP_LICENSE_GATE` startup path in `mcp_server.py`,
  `config.py` and `license_gate.py`.
- Ensure `QA_MCP_LICENSE_GATE=1`, `QA_MCP_LICENSE_BROKER` or
  `QA_MCP_LICENSE_TIMEOUT` cannot make qa-mcp call the broker or deny startup.
- Adjust tests so the guaranteed behavior is free startup with no broker call.

### Acceptance
- Startup makes zero `ai1c-license` calls with license env vars unset or set.
- There is no startup denial for missing qa-mcp entitlement, lease, broker,
  license key or license server.
- Any retained compatibility env var is ignored or reported as deprecated
  without exposing secrets and without failing startup.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-01-short-circuit-qa-mcp-product-license-gate/`

## Change 2: `remove-qa-mcp-license-bootstrap-and-image-wiring`

### Why
Delivery assets still request activation, ship the broker, and verify a
compiled product-license gate even if the Python default is off.

### Goal
Ship a genuinely free standalone/protected distribution while retaining the
existing encrypted bundled-data and no-key-in-image protections.

### Scope
- Remove license activation prompts/defaults from `delivery/bootstrap.ps1`,
  generated standalone bootstrap, delivery docs and Windows runbooks.
- Stop passing `QA_MCP_LICENSE_GATE=1` and product-license broker env into the
  shipped Docker run path.
- Remove the broker from the thin image/release verifier requirements, or leave
  it only as inert historical baggage with tests proving it is not invoked.
- Cancel/supersede the active `license-activation-bootstrap` OpenSpec change
  instead of completing it.

### Acceptance
- Fresh standalone install/update needs no qa-mcp product license key,
  entitlement, activation server or lease volume.
- Release docs contain no instruction that qa-mcp product licensing is required.
- Protected-image verification no longer requires `/usr/local/bin/ai1c-license`
  or compiled `license_gate` as a non-removable gate.
- Bundled protocol data remains protected according to current release policy:
  no plaintext bundled data or runtime key material appears in shipped layers or
  retained evidence. If `BUNDLED_DATA_KEY_FILE` remains, it is a data-protection
  runtime key path, not a license-broker entitlement path.

### Depends On
- `short-circuit-qa-mcp-product-license-gate`

### Related
- `openspec/changes/archive/2026-08-01-remove-qa-mcp-license-bootstrap-and-image-wiring/`

## Archive
- `openspec/changes/archive/2026-08-01-short-circuit-qa-mcp-product-license-gate/`
- `openspec/changes/archive/2026-08-01-remove-qa-mcp-license-bootstrap-and-image-wiring/`

## Verify
- `pytest` focused on startup/config and legacy license env handling.
- Focused standalone renderer/bootstrap tests plus a rendered-script scan for
  no product-license prompts, broker calls, lease mounts, or
  `QA_MCP_LICENSE_GATE=1` in shipped runs.
- Protected-image/archive fixture tests and scanner smoke for retained
  source/data/key invariants.
- Windows-native PowerShell parse of the rendered bootstrap, or a concrete
  recorded runtime gap if the authorized contour cannot consume the worktree.
- `git diff --check` and strict change/all OpenSpec validation.

## Next
- none

## Result
Completed. qa-mcp starts without a product-license gate,
standalone/bootstrap assets no longer activate or lease a qa-mcp product
license, broker assets are removed, and protected source/data/key invariants
remain enforced by the built-image and saved-archive verifiers.

## Log
- 2026-08-01 card created from operator no-license decision for qa-mcp before
  the next alpha release.
- 2026-08-01 `$changerail-ff`: preserved the two ordered changes and created
  apply-ready proposal, design, delta specs, and tasks for free Python startup
  followed by standalone/protected-delivery cleanup.
- 2026-08-01 `$changerail-do`: moved the apply-ready card to `3.inprogress` and
  started `short-circuit-qa-mcp-product-license-gate`.
- 2026-08-01 Change 1 RED: `.venv/bin/pytest -q
  tests/test_free_startup.py tests/test_config.py` failed as intended (`2
  failed, 5 passed`) because legacy variables still activated the broker gate
  and license settings still existed. After implementation, the same command
  passed (`7 passed`); focused source scan, strict change validation, and
  `git diff --check` also passed.
- 2026-08-01 Change 1 Windows runtime gap: authenticated SSH reached the
  authorized `HISTORICAL-LAB-HOST` contour, but it has neither a qa-mcp source
  checkout nor `python`, `py`, or `uv`, so the uncommitted focused Python test
  cannot run there. PowerShell 5.1 is available for Change 2 bootstrap parsing.
- 2026-08-01 Change 2 RED: the inverted standalone/release tests failed because
  the renderer still required `LicenseKeyFile`, the publisher still pinned the
  broker, and broker assets still shipped; archive fixtures also failed while
  the scanner required the retired broker contract.
- 2026-08-01 Change 2 GREEN: focused startup/config, renderer, release-script,
  and protected-archive tests passed (`27 passed`), and the focused release and
  archive subset passed again after the current FastMCP verifier update (`20
  passed`). The rendered bootstrap scan found no product-license parameters,
  broker invocation, lease, or `QA_MCP_LICENSE_*` wiring while retaining the
  independent `BundledDataKeyFile` path.
- 2026-08-01 Windows-native bootstrap proof: PowerShell 5.1 on the authorized
  `HISTORICAL-LAB-HOST` contour parsed the rendered standalone bootstrap with
  execution-policy bypass and reported `standalone bootstrap Windows-native
  contract OK`; the exact temporary directory created for the proof was then
  removed.
- 2026-08-01 protected-image recovery proof: the first build correctly failed
  on readable `telemetry_bridge.py`; after adding it to the compiled/drop set,
  the build exposed and then fixed FastMCP/Nuitka postponed-annotation and
  public tool-list API drift. The final image built successfully, registered 68
  tools from the Nuitka entrypoint, encrypted/decrypted 16 bundled data files,
  and passed both the in-container verifier and saved-layer/config/history
  archive scanner without broker or product-license assets. The temporary image
  and archive created for this proof were removed.
- 2026-08-01 full offline verification: `.venv/bin/pytest -q -ra -m 'not
  live' --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60` passed (`888
  passed`, 71.69% coverage). Strict OpenSpec validation passed for all 20
  archived/main items, `openspec list --json` is empty, and `git diff --check`
  passed.
- 2026-08-01 independent ChangeRail review cycle 1 returned GO with all seven
  acceptance criteria satisfied, zero findings, zero unbacked claims, and no
  unrelated tracked changes. The canonical verdict validated as fresh for the
  reviewed payload before card finalization.
- 2026-08-01 `$changerail-pub`: finalized the reviewed card as `4.done` for
  publication on the configured `origin/main` track.
