## Context

The manager fixture V1 path already joins read-only manager harness case events
with captured traffic. V2 safe-action research needs a similar entry point,
but the scenario must model UI action phases and preserve background traffic
as separate evidence rather than treating every nearby frame as action proof.

## Goals / Non-Goals

**Goals:**

- Introduce a dedicated `manager-fixture-v2-safe-action` scenario.
- Require reviewed manifest rows before capture or manager-runner execution.
- Emit phase-aware events for pre-read, action, post-read and recovery.
- Preserve raw runtime output under ignored runtime paths.

**Non-Goals:**

- Implement client fixture UI handlers.
- Implement manager-side action execution that is not already available.
- Accept protocol mappings or real demo button behavior.
- Support text input, value toggles, business writes or V3 mutation recovery.

## Decisions

- Keep the V2 scenario separate from `manager-fixture-v1-readonly` instead of
  overloading the read-only route. This protects V1 reporting stability and
  makes action-specific frame ranges explicit.
- Treat `action_start` and `action_end` events as side-channel boundaries. The
  tooling records them for joining and review, but it does not inject markers
  into the TCP stream.
- Fail closed when a manifest row is missing required V2 fields, has
  `mutates_business_data` other than `false`, or uses a family outside the
  safe-action allowlist.

## Risks / Trade-offs

- [Risk] Background refresh traffic may be misread as action traffic.
  [Mitigation] Keep pre-read, action, post-read, background and recovery event
  ranges distinct in the scenario output.
- [Risk] Scenario wiring may depend on manager harness details.
  [Mitigation] Keep the scenario contract small and verify it with a
  Windows-native dry run before publishing compact evidence.
- [Risk] An incomplete manifest could trigger an unsafe action.
  [Mitigation] Validate manifest rows before capture and fail closed.
