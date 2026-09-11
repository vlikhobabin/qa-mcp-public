## Context

README currently leads with an internal lab status narrative and active
delivery docs advertise a private staging portal. Standard public project
policies are absent. Public source users need documented source/package/Docker
routes and an honest pre-release boundary while OSS-08 remains unstarted.

## Goals / Non-Goals

**Goals:**

- Make README the concise public map for architecture, install, auth, bridge,
  development, safety and contributions.
- Add standard public project policies without personal contact details.
- Distinguish current public source build from historical/internal release
  staging and future OSS-08 publication.
- Validate local links and forbidden public terminology offline.

**Non-Goals:**

- Publish artifacts, configure GHCR, change bootstrap/release code or claim a
  stable release.
- Run the Windows bridge or any live protocol workflow.

## Decisions

1. Replace README rather than append another status layer. Detailed protocol
   history remains under `docs/protocol-research/` and is labeled historical.
2. Use `uv`/PEP 517 source install and locked offline pytest commands as the
   canonical contributor path; Docker and Windows bridge docs remain linked
   secondary routes.
3. SECURITY uses GitHub private vulnerability reporting; SUPPORT uses public
   Issues/Discussions. No invented email is published.
4. CONTRIBUTING states Apache-2.0 inbound contribution terms and upstream-first
   boundaries. GOVERNANCE uses maintainer-led public decisions. The Contributor
   Covenant text uses the same private reporting route for enforcement.
5. Retained staging docs get a prominent pre-release/historical boundary and
   are not presented as the public install path. OSS-08 remains the owner of
   release automation.

## Risks / Trade-offs

- [Risk] Replacing README hides useful lab detail. -> Preserve links to
  historical research indexes instead of deleting them.
- [Risk] GitHub feature availability varies. -> Describe UI routes, not a
  personal address or credential.
- [Risk] Source instructions imply runtime works without proprietary 1C. ->
  Separate offline development from live runtime prerequisites explicitly.

## Migration Plan

Add docs and link checks, replace README, update active delivery landing text,
then run terminology/link tests. Rollback affects documentation only.

## Capture, Replay And Cleanup

No capture/replay, frame range, dynamic runtime field, process or service is
used. Documentation checks create no persistent output.

## Open Questions

- none.
