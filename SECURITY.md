# Security policy

## Supported source

qa-mcp is pre-release software. Security fixes target the latest public
`main` source snapshot; no older version is promised support until a release
policy is published.

## Report a vulnerability

Use the repository's private vulnerability-reporting flow under
**Security → Advisories → Report a vulnerability**. Do not open a public issue
for an unpatched vulnerability and never include credentials, customer data,
private endpoints, infobases, captures or exploit payloads in public reports.

If private reporting is unavailable, open a public issue containing only a
request for a private security contact. Do not include technical exploit detail.

## Runtime boundary

- HTTP MCP defaults to loopback. A non-loopback bind requires a strong
  `QA_MCP_BEARER_TOKEN`.
- The Windows bridge requires its own token and target-bound lifecycle identity.
- 1C credentials belong in ignored local state and must not enter Git, logs,
  issue reports or evidence.
- Mutation/UI tools can change test data. Use a disposable test target and the
  documented target-binding/recovery controls.

See [SUPPORT.md](SUPPORT.md) for non-security questions and
[docs/publication-policy.md](docs/publication-policy.md) for disclosure gates.
