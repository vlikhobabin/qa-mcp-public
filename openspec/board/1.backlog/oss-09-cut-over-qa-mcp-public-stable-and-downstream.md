# Cut over qa-mcp public stable and downstream consumption

## Status
1.backlog

## Owner
qa-mcp

## Series
oss-09

## Order Index
408

## OpenSpec Stage
story

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Promote the qualified public release to stable, make it the canonical upstream
for AI for 1C, and retire supported private/stale qa-mcp distribution routes
without erasing historical audit records.

## Acceptance
- Immutable runtime-target binding is delivered and identified in the stable
  release evidence.
- `open_external_processor` is either fully qualified by card 405 or absent
  from the stable standalone profile and documented as unsupported backlog.
- The stable public repository, package, GHCR digest and Windows artifacts are
  mutually traceable to one reviewed commit and pass exact-artifact smokes.
- AI for 1C pins the public semantic version and passes the consumer contract
  through a dependency update, without cherry-pick, source copy or reverse
  import from public core to private code.
- Upstream-first fixes and downstream upgrade/compatibility policy are tested
  and documented.
- Supported private portal/stale dist references are retired, with rollback
  criteria and historical records retained.

## Depends On
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`
- `openspec/board/1.backlog/oss-08-publish-qa-mcp-github-ghcr-release-train.md`
- Card 405 delivered, or an explicit standalone-profile omission decision.
- `openspec/board/4.done/oss-06-s4-r1-i16-record-stable-profile-omission-after-i15.md`
- Private AI for 1C downstream repository work remains separately owned.

## Change Set
- none yet

## Verify
- Exact public stable artifact and rollback smoke.
- Stable profile assertion for `open_external_processor`.
- AI for 1C pinned-version consumer contract and dependency-update proof.
- Full release manifest and strict OpenSpec validation.

## Archive
- not started

## Related
- `openspec/board/1.backlog/product-v1-runtime-proxy-qa-execution.md`
- Suite-root card `runtime-proxy-v1-qa-adapter-epic` (owned by the suite repository).

## Result
not started

## Next
- Inherit OSS-08's corrective release gate from the 2026-09-05 review. Stable
  evidence must identify FIX-04A/B/C and FIX-09A/B/C with the other bounded
  corrections and final source/artifact qualified by FIX-11/FIX-12, not only
  historical OSS-04 or the superseded corrective aggregates.
  Preserve the explicit non-owned bound-attach restriction until a genuine
  observer contract exists; unsupported attach and dormant external-processor
  behavior cannot be advertised as repaired.
- Remain blocked on OSS-08 release artifacts and separately owned downstream
  work. Card 403 is published; I16 at `10598ef` supplies the required explicit
  omission decision without certifying S7. Refine bounded board-only plans
  only when those release prerequisites are available.

## Log
- 2026-09-05T08:38:59Z Reconciled stable qualification to the six named corrective successors without accepting or completing their work.
- 2026-09-05T08:11:47Z Recorded the corrective qualification gate inherited
  through OSS-08; stable/downstream acceptance remains unstarted.
- 2026-08-24 extracted from the former all-in-one publication change so stable
  cutover and downstream adoption have their own release gate and rollback.
- 2026-09-05 board inventory corrected the published target-binding dependency
  and linked I16. Stable promotion and downstream cutover remain unstarted.
