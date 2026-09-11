## Context

The build label describes release contents, not a wire protocol. Coupling the
client image to that label causes false incompatibility while the endpoint
contract is unchanged. An explicit operator version pin is still useful for a
controlled stand and must keep exact semantics.

## Decisions

1. Add `display_protocol: ai1c.windows-host-display-http.v1` to authenticated
   `/version`. Keep `version` and `sha256` unchanged.
2. The default client accepts the supported protocol regardless of build label.
   Known legacy build labels that predate `display_protocol` remain accepted.
   Unknown builds without a protocol and mismatched protocols fail closed.
3. A non-empty `QA_MCP_HOST_AGENT_EXPECTED_VERSION` marks the version as
   operator-pinned. Pinned mode compares the raw build label exactly before
   protocol compatibility; SHA pin behavior is unchanged.
4. Handshake returns `version_relationship` (`current`, `protocol-compatible`,
   `legacy-compatible`, or `pinned`) and `display_protocol`. Doctor copies only
   those bounded fields.

## Safety

- Unsupported protocol ids fail before any display action.
- Missing protocol is tolerated only for the existing known-good legacy set.
- No tokens, URLs, hashes beyond the already returned optional SHA, or local
  paths are added to doctor output.

## Verification

- Newer unknown build + supported protocol passes with
  `protocol-compatible`.
- Unknown build without protocol and unknown/mismatched protocol fail closed.
- Explicit version and SHA pins remain exact.
- Go response and Python doctor relationship tests pass.
