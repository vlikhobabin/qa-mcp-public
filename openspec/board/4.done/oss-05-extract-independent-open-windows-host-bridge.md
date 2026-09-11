# Extract independent open Windows host bridge

## Status
4.done

## Owner
unassigned

## Series
oss-05

## Order Index
404

## OpenSpec Stage
archived

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `yes`
- Live admission: `yes`
- Final certification: `yes`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/oss-05-a1-authorize-standalone-host-bridge-api-v1.md","authorization_id":"oss-05-a1-authorize-standalone-host-bridge-api-v1"}`

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Extract a narrow, fully open Windows bridge for standalone TestClient and
display operations, independent of AI for 1C COM, BSL, Team, onboarding and
generic execution components.

## Acceptance
- The public bridge exposes a versioned authenticated capability handshake and
  only the reviewed TestClient lifecycle/relay and bounded display primitives.
- COM worker, BSL supervisor, agent completion, Team/onboarding and arbitrary
  platform execution are absent from the executable, installer and schema.
- The executable and installer build entirely from public repository source
  and require no AI for 1C binary at runtime.
- Lifecycle ownership, target-window binding, token safety, compatibility
  rejection and exact cleanup are proven for the release executable.
- The standalone container connects through this public contract.

## Change Set
1. `extract-independent-open-windows-host-bridge` -
   `openspec/changes/extract-independent-open-windows-host-bridge/`

## Depends On
- `openspec/board/4.done/oss-01-establish-qa-mcp-shared-core-boundary.md`
- `oss-05-i1-investigate-standalone-host-bridge-api-v1-boundary`
- `oss-05-a1-authorize-standalone-host-bridge-api-v1`

## Verify
- Go unit and API contract tests.
- Python bridge-client compatibility tests.
- Windows-native lifecycle/display/recovery and owned-cleanup proof against
  the exact release executable.
- `./bin/openspec validate extract-independent-open-windows-host-bridge --strict`.

## Archive
- `openspec/changes/archive/2026-08-27-extract-independent-open-windows-host-bridge/`

## Related
- `host-agent/`
- `openspec/board/4.done/120-2026-06-26-windows-host-input-screenshot-agent.md`

## Result
The standalone Windows host bridge is implemented as public API
`qa-mcp.windows-host-bridge` major `1`, host version `1.0.0-standalone`.
Only authenticated TestClient lifecycle/relay and bounded window, input,
screenshot and UIA routes remain; COM, BSL, agent CLI, Team/onboarding,
path-probe and generic platform execution surfaces were removed from the
executable, installer, schema and release tooling. Python clients negotiate
`/v1/capabilities` and fail closed on incompatible major versions or missing
capabilities.

After three independent `NO-GO` cycles, three bounded same-card rescues closed
the original runtime/install findings plus the final synced-spec, classifier
and exact-CI evidence-reference defects. The exact final Windows release
candidate SHA-256
`eb699c5c6b771ceba3ccc6c28a5780f6888395ec427329bb64c887c88bdc8025`
passed native owned lifecycle/read/input/screenshot/UIA/refusal/recovery plus a
real standalone-container `TestClientSession.read_initial()` through the
authenticated fixed-target relay on `HISTORICAL-LAB-HOST\\historical-user` at
`192.0.2.204`, platform `8.3.27.2130`, exact target
`C:\\1C_BASES\\vanessa_client`. `/window_list` returned exactly the
lifecycle-owned PID and refused a target-less request before desktop
enumeration. Clean install and idempotent reinstall succeeded with an external
protected token file; default uninstall removed both exact firewall rules
without repeating the optional relay address. Sanitized evidence
is indexed under
`.runtime/changerail/evidence/oss-05-extract-independent-open-windows-host-bridge/`;
raw screenshot, UI text, credentials, token and current-run Windows resources
were removed, and unrelated 1C/Docker state was preserved. All `14/14` tasks
are complete, the authorized ChangeRail production classifier is
`285 <= 301`, main specs are synced and the change is archived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-24 child card extracted from the open-source roadmap; its OpenSpec
  change is apply-ready.
- 2026-08-25 dependency link updated to published OSS-01; card is unblocked and
  remains apply-ready behind the current shared-main OSS-04 sequence.
- 2026-08-27 `$changerail-deliver` started on `main`; unrelated preexisting
  `.codex/config.toml` remains excluded from card scope.
- 2026-08-27 reduced the Go executable and public installer to the standalone
  v1 capability set; compatibility, removed-route and release tooling tests
  pass, while the bounded production addition gate is `231 <= 300` LOC.
- 2026-08-27 built exact candidate
  `347d9d9df0a06964e64aa5d8722efd82ad960b4b9b4c0af4428dc6dcefb4e772`;
  Go tests/vet, Windows cross-compiled tests and source-bound artifact checks
  passed.
- 2026-08-27 authorized `.204` Windows-native proof passed exact lifecycle,
  relay, window/read, bounded input, screenshot/UIA, negative compatibility,
  wrong-target, failed-launch, locked/disconnected/noninteractive and repeated
  cleanup cases. Exact-owned task/stage/tunnel/listeners were removed and
  unrelated Docker/1C state was preserved.
- 2026-08-27 exact non-live CI passed `1551` tests at `74.50%` coverage; the
  final installer/release regression rerun passed `20` tests, strict OpenSpec
  validation passed `38/38`, and `git diff --check` passed.
- 2026-08-27 synced `qa-mcp-standalone-host-bridge` and the narrowed
  `qa-mcp-windows-host-agent-security` spec, archived the completed `14/14`
  change, and kept the card in `3.inprogress` for independent review/publish.
- 2026-08-27 deterministic critical preflight passed manifest scope, archive,
  strict OpenSpec `38/38` and diff checks, measured `170 <= 300` added
  production LOC, then returned `investigation-required`: the new public API
  v1 wire contract has no published investigation authorization. No reviewer
  was launched and no publication was attempted.
- 2026-08-27 the operator authorized the bounded prerequisite chain;
  OSS-05-I1 was independently reviewed and published at `abfaff2`. Exact
  OSS-05-A1 authorization delivery started with this card as its sole successor.
- 2026-08-27 OSS-05-A1 was independently reviewed and published at `46f0c38`;
  deterministic preflight accepted its exact authorization and routed OSS-05
  to critical `xhigh` review.
- 2026-08-27 review cycle 1 returned `NO-GO` with six blockers (`R1`-`R6`):
  stale candidate bytes, display-selector lifecycle bypass, unused concurrency
  limiter, missing authenticated relay/container proof, relay firewall cleanup
  gap and Python boolean API-major acceptance.
- 2026-08-27 bounded rescue attempt 1 fixed all six classes and built exact
  candidate `11edeff48498a131c871b4516cf36492136a04c6319a65e0bb11da514ea7e011`.
  Windows-native proof on `.204` confirmed lifecycle-only targeting, N+1
  capacity refusal, authenticated relay plus real standalone-container protocol
  read, exact default-uninstall firewall cleanup and complete owned-resource
  cleanup with unrelated 1C/Docker preservation. Canonical sanitized evidence
  index validation passed with six mandatory entries.
- 2026-08-27 post-rescue verification passed Go test/vet/gofmt, `150` focused
  Python bridge/lifecycle/relay tests, source-bound candidate verification,
  strict OpenSpec `40/40`, manifest scope and `git diff --check`. Exact non-live
  CI passed `1556` tests at `74.51%` coverage.
- 2026-08-27 review cycle 2 returned `NO-GO`: `/window_list` still enumerated
  the whole desktop without lifecycle authority, clean install failed when
  `TokenFile` was outside `InstallDir`, and `delivery/README.md` described a
  retired password script.
- 2026-08-27 bounded rescue attempt 2 made `/window_list` require and resolve
  the exact owned lifecycle PID/TPort, created `InstallDir` independently of
  the token parent, and corrected the public credential-exposure description.
  Exact candidate `eb699c5c6b771ceba3ccc6c28a5780f6888395ec427329bb64c887c88bdc8025`
  passed `.204` lifecycle/window-list/display/relay/container proof; target-less
  window-list returned `422`, external-token clean install/reinstall/uninstall
  passed, and all current-run resources were removed with unrelated 1C/Docker
  counts preserved.
- 2026-08-27 review cycle 3 returned `NO-GO`: the synced security spec retained
  four retired authority contracts, the card recorded stale `260 <= 301` LOC,
  and the manifest referenced a missing exact-CI evidence id.
- 2026-08-27 bounded rescue attempt 3 explicitly retired or superseded the
  obsolete path-probe, title fallback, raw `client_port`/selector-precedence
  and COM/CLI/platform/BSL-helper contracts in both archived delta and active
  spec; corrected the deterministic classifier to `285 <= 301`; and retained
  exact CI evidence under `exact-nonlive-ci-rescue2`. Strict OpenSpec passed
  `40/40`, focused Python passed `60`, Go test/vet/gofmt passed, exact candidate
  verification retained SHA-256 `eb699c5...`, and exact CI passed `1557` at
  `74.51%` coverage.
- 2026-08-27T12:55:58Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
