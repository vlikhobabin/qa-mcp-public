# Governance

qa-mcp uses a maintainer-led, public-development model.

## Roles

- Contributors propose issues, documentation, tests and code.
- Reviewers evaluate correctness, safety, scope, evidence and compatibility.
- Maintainers merge changes, manage releases and steward security responses.

Roles are earned through sustained, constructive public contributions. A
maintainer may invite a contributor to a reviewer or maintainer role after
public discussion and existing-maintainer consensus.

## Decisions

Routine decisions happen in issues and pull requests. Compatibility, security,
public-contract and release changes require an OpenSpec change or equivalent
recorded design plus independent review. Maintainers seek consensus; when it is
not reachable, the reviewing maintainers document the decision and rationale.

No private downstream can silently redefine public core behavior. Generic
changes land upstream first; downstream-specific integrations remain outside
this repository.

## Conduct and security

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Vulnerabilities follow [SECURITY.md](SECURITY.md), not public design discussion.
