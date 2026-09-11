## Context

The Go `RegistrationClient` intentionally POSTs to the configured registry URL
verbatim. On the real stand a base URL therefore reached `/`, and the root
registry returned a pre-audit 404. The client read and discarded the useful
response while retaining only `registry-rejected`, so the request-path defect
was indistinguishable from other rejections in host-agent health.

This is HTTP control-plane behavior, not native 1C TestClient protocol
research. Capture sources, protocol frame ranges, dynamic protocol fields and
replay strategy are therefore not applicable. Evidence comes from focused Go
tests and an offline loopback run of the real root Python registry router.

## Goals / Non-Goals

**Goals:**

- Expose the rejection status consistently in logs and authenticated health.
- Retain a useful but bounded response-body snippet without logging registry
  credentials or the per-bridge token.
- Warn operators when the explicit startup URL has no endpoint path.
- Prove that the Go client remains compatible with the root registry's real
  `/v1/bridges/register` router and audit behavior.

**Non-Goals:**

- Appending, normalizing or otherwise changing the configured request path.
- Changing registration headers, payload fields, heartbeat or TTL behavior.
- Modifying the root registry or copying its router into this component.
- Starting 1C, touching an infobase, or collecting raw protocol/runtime data.

## Decisions

1. **Keep the verbatim-URL wire contract and add a startup warning.** A helper
   parses the explicit `-registry-url` value and warns when its path is empty or
   slash-only. It does not require one hard-coded endpoint suffix because the
   contract permits a full deployment-specific endpoint URL. Rejecting the
   process or auto-appending `/v1/bridges/register` would turn a diagnostic
   hardening change into a compatibility change.

2. **Represent the HTTP rejection in both stable and structured health
   fields.** Non-2xx responses set `last_error` to
   `registry-rejected-<status>` and `last_http_status` to the integer status.
   A success or a later non-HTTP failure clears the HTTP status so health never
   presents stale transport evidence. Existing `state: error` and retry
   behavior remain unchanged.

3. **Redact before bounding the logged body.** The client reads at most the
   existing bounded response limit, replaces the current registration
   credential and bridge token with a fixed redaction marker, then selects at
   most 512 bytes and logs it with quoted escaping. Redaction before truncation
   prevents a token crossing the snippet boundary from being partially logged;
   quoted output prevents response newlines or control characters from forging
   additional log lines. The status is logged even when the non-2xx body is
   oversized or cannot be fully read.

4. **Exercise the actual root router through a loopback cross-language
   contract.** A pytest harness imports root
   `deploy/docker/bin/team_registry.py`, creates its real `StateStore` and
   `make_handler` with temporary state/audit paths, and starts its real HTTP
   handler on an ephemeral loopback port. It passes the issued registration
   credential and full endpoint to a focused Go test through environment
   variables; the Go test invokes the real `RegistrationClient`. The harness
   asserts successful client status and the real audit row
   `bridge_registration/status:ok`. Because the root router returns 404 for
   `/`, this turns red if the request path drifts. In a standalone qa-mcp clone
   without the root source, the cross-repository test skips explicitly; the
   ChangeRail verification in the suite workspace must record a passing, not
   skipped, focused run.

## Risks / Trade-offs

- **A hostile registry echoes a credential in its error body** -> redact both
  known registration secrets before truncating and test the log sink for secret
  absence.
- **A response injects control characters into logs** -> emit the snippet with
  quoted escaping and test single-line output.
- **A stale 404 survives a later network error** -> clear `last_http_status` on
  every non-HTTP failure and on success.
- **The cross-repository contract drifts or is unavailable in standalone CI**
  -> resolve an explicit environment override first, otherwise the canonical
  suite sibling path; skip only when root source is absent and require a
  non-skipped delivery run in the suite workspace.

## Migration Plan

Land RED focused tests for status/snippet/warning and the real-router path,
then implement the bounded diagnostics. Run Go unit/race/vet checks, Windows
cross-build, the focused pytest contract, the declared component offline test
floor and OpenSpec/whitespace validation. The suite-root public-surface scanner
is attempted only when its contract supports this component workspace; a
root-only contract mismatch is recorded as not applicable rather than claimed
green. Rollback is a normal revert of this component payload; no persisted
state or registry migration is needed.

The contract server binds only ephemeral loopback state, stops its owned thread
at test exit and uses pytest-owned temporary files, so no live-runtime cleanup
or process termination is required.

## Open Questions

None.
