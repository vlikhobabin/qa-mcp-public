# Use broker-released bundled-data key for protected qa-mcp startup

## Status
5.canceled

## Owner
unassigned

## OpenSpec Stage
canceled/superseded

## Source
- Root S40 delivery card:
  `/opt/ai-dev-suite-for-1c/openspec/board/3.inprogress/s40-suite-release-package-060-bundled-data-key-license-lease-binding.md`.
- Root archived changes:
  `bundled-data-key-release-contract`,
  `license-server-dek-wrap-service`, and
  `license-broker-bundled-key-command`.
- Existing qa-mcp protected-image follow-up:
  `openspec/board/3.inprogress/audit-qa-thin-layer-leak.md`.

## Summary
Switch the protected qa-mcp release/startup path from an operator-supplied
bundled-data key to a broker-produced runtime key file. The accepted root
interface is:

```text
ai1c-license bundled-key --product qa-mcp --component qa-mcp --release-id <release> --out <runtime-key-file> --json
```

qa-mcp should set `BUNDLED_DATA_KEY_FILE` only after that command succeeds and
the produced file is non-empty, owner-only, and usable by the container/runtime.
Development-only direct key inputs may remain for local tests, but they are not
the protected release path.

## Cancellation Rationale
Canceled 2026-08-01 by operator product decision: qa-mcp is distributed as a
free component both standalone and as part of `ai for 1c`. It must not require
product-license activation, entitlement, lease checks or a broker-produced
bundled-data key at startup, runtime or update time.

The replacement release-fix card is:
`openspec/board/2.todo/remove-product-license-gate-for-free-qa-mcp.md`.

## Acceptance
- Protected release startup invokes `ai1c-license bundled-key` with product and
  component `qa-mcp`, the release id being launched, and an owner-only runtime
  key-file path.
- Any broker non-zero exit, malformed JSON, missing output file, non-`0600`
  output file, empty key file, or failed decrypt smoke prevents qa-mcp startup
  and serves no bundled protocol IP.
- Successful startup passes only `BUNDLED_DATA_KEY_FILE` to qa-mcp; plaintext
  key material is not passed in argv, logged, written into tracked files, baked
  into Docker layers, or emitted in retained evidence.
- Scanner/evidence proves the shipped image and saved archive contain neither
  the active bundled-data key nor any KEK seed or recoverable plaintext bundled
  captures/templates.
- Cross-deployment lease/key reuse fails: a lease copied to another deployment
  cannot obtain or unwrap the release key.
- Release-key rotation is covered: release N+1 bundled data does not decrypt
  with release N key material.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- root `license/ai1c-license` command:
  `ai1c-license bundled-key --product qa-mcp --component qa-mcp --release-id <release> --out <runtime-key-file> --json`
- root contract: `license/contracts/bundled-key-release-v1.md`
- qa-mcp key hook: `src/qa_mcp/protocol/_bundled_crypto.py`
- qa-mcp release tooling: `tools/release/publish_self_hosted.sh`,
  `delivery/bootstrap.ps1`, `tools/release/render_standalone_bootstrap.py`

## Result
canceled/superseded by the no-license qa-mcp release policy

## Next
- none

## Change Plan Notes
When the card moves to `2.todo`, replace this section with ordered changes.

## Log
- 2026-07-30T08:58:00Z card created from root S40 broker-key delivery.
- 2026-08-01 canceled by operator decision: qa-mcp no longer has a product
  licensing path.
