# Display-bridge host-agent version policy: make it forward-compatible instead of an exact-string allowlist

## Status
5.canceled — absorbed 2026-07-13 into
`host-agent-bsl-supervisor-cwd-and-diagnosability.md`, Change 2
`decouple-host-agent-version-compatibility`.

## Owner
unassigned

## Order Index
133

## OpenSpec Stage
absorbed into an apply-ready ChangeRail change; no independent implementation
or publish remains on this card

## Source
- 2026-07-12 supervised solo E2E on `.201` (standalone full-product suite, own
  Docker, no team-server) against the published 07-09 full-10 bundle with the
  current host-agent `0.1.6-bsl-supervision`.

## Problem
The display bridge gates every remote-client op on an **exact host-agent build
label** matched against a hardcoded allowlist:

- `src/qa_mcp/protocol/display_backend.py:18` — `HOST_AGENT_VERSION = "0.1.6-bsl-supervision"`.
- `display_backend.py:19-31` — `COMPATIBLE_HOST_AGENT_VERSIONS` is a hand-maintained
  `frozenset` of build-label strings.
- `display_backend.py:94-97` — `host_agent_version_compatible(version, expected)`:
  when `expected == HOST_AGENT_VERSION` (the default, no operator override) it
  returns `version in COMPATIBLE_HOST_AGENT_VERSIONS`; otherwise exact-equality.
- `display_backend.py:298-301` — a non-match raises `DisplayBackendError`
  (`host-agent-version-mismatch`) which hard-fails `force_list_refresh` and any
  other display-bridge op.

Because the allowlist is a set of exact strings baked **into the qa image at
build time**, any shipped qa image that predates a host-agent bump rejects the
newer host-agent by default — even when the display-bridge wire protocol is
unchanged. The image↔host-agent release cadences are coupled, and every host-agent
version bump silently requires a matching qa image rebuild or an operator override.

### Concrete evidence (.201 solo E2E, 2026-07-12)
The 07-09 published full-10 bundle's qa image was built when
`HOST_AGENT_VERSION == "0.1.4-window-by-client-port"` and its allowlist did not
contain `0.1.6`. Paired with the current host-agent `0.1.6-bsl-supervision`:

- `infobase_info` attached fine (thick client, demo10413, `Администратор`), but
- `read_list_grid Справочник.Валюты` returned `row_count: 0`, `list_refresh:
  {method:none, poll_outcome:timeout}`, error
  `host-agent-version-mismatch: host agent version 0.1.6-bsl-supervision does not
  match expected 0.1.4-window-by-client-port`.
- Setting `QA_MCP_HOST_AGENT_EXPECTED_VERSION=0.1.6-bsl-supervision` and recreating
  the qa container made the read GREEN — **15 rows of live data (EUR / USD / Рубли)**.

So the wire protocol and read path were fully functional with 0.1.6; only the
version-string gate blocked it. This is the same class as the archived finding H
(display-bridge handshake version) — it keeps recurring because the mechanism is
a static allowlist, not a compatibility policy.

## Not the fix
Current HEAD already sets `HOST_AGENT_VERSION = "0.1.6-bsl-supervision"` and
includes it in the allowlist (`display_backend.py:20` folds `HOST_AGENT_VERSION`
into the set), so a qa image **rebuilt from HEAD** accepts the 0.1.6 host-agent
with no override. Rebuilding/republishing the full-10 bundle from HEAD is a
separate **root/release** action (out of scope for this card) and resolves the
immediate symptom. This card is about the **recurring design coupling**, which a
bundle rebuild does not remove: the next host-agent bump (0.1.7, ...) reintroduces
the same mismatch for any already-shipped image.

## Proposed direction (planning, not prescriptive)
Replace the exact-string allowlist default with a forward-compatible policy while
keeping an explicit operator pin as the strict escape hatch. Candidate approaches
to evaluate during `$opsx-ff`:

1. **Min-supported gate.** Parse the numeric `MAJOR.MINOR.PATCH` prefix of the
   host-agent build label and accept any host-agent `>=` a declared
   `MIN_SUPPORTED_HOST_AGENT`. Newer builds pass by default; the trailing label
   (`-bsl-supervision`) becomes informational.
2. **Protocol-version handshake.** Have the host-agent advertise a display-bridge
   **protocol** version (independent of its build label); qa checks protocol
   compatibility, not the build string. This decouples the release cadences at
   the contract layer (most durable).
3. **Warn-not-fail on newer-unknown.** Keep the allowlist for known-good builds
   but treat an unrecognized **newer** version as compatible-with-warning (surfaced
   by `doctor`) instead of a hard fail; only unrecognized **older** or explicitly
   incompatible builds hard-fail.

Constraints to preserve:
- When `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is explicitly set, keep today's exact
  match (operator can still pin a specific build).
- Keep backward compatibility with the older host-agents already in the allowlist.
- The policy must live in the image but not require an image rebuild to accept a
  newer wire-compatible host-agent.

## Acceptance criteria (sketch — refine in `$opsx-ff`)
- A host-agent whose build label is newer/unknown but wire-compatible does NOT
  hard-fail display-bridge ops by default (repro: image built against host-agent
  vN, run against host-agent vN+1 → `read_list_grid` succeeds without an override).
- An explicit `QA_MCP_HOST_AGENT_EXPECTED_VERSION` still enforces exact match.
- `doctor` reports the host-agent vs expected relationship (compatible / newer /
  older / pinned) instead of only a boolean.
- Regression test covering the "shipped-image + newer-host-agent" scenario that
  `.201` exercised.

## Touch points
- `src/qa_mcp/protocol/display_backend.py` — `HOST_AGENT_VERSION`,
  `COMPATIBLE_HOST_AGENT_VERSIONS`, `host_agent_version_compatible`, the
  `host-agent-version-mismatch` raise site.
- `src/qa_mcp/config.py` — `HOST_AGENT_EXPECTED_VERSION_ENV` handling.
- `src/qa_mcp/doctor.py` — version-relationship reporting.

## Companion action (other repo, not this card)
Root/release: rebuild + republish the full-10 bundle from current HEAD so the
shipped qa image co-versions its host-agent compatible set with 0.1.6 (and picks
up other post-07-09 component fixes). Tracked separately from this qa-mcp card.
