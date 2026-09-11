# Public source publication policy

qa-mcp is licensed exactly under the [Apache License 2.0](../LICENSE). The
package metadata uses SPDX `Apache-2.0`; no second license or field-of-use
restriction applies. [NOTICE](../NOTICE) records project and trademark
attribution without claiming affiliation or endorsement.

## Publication boundary

The public upstream is intended to start from one source snapshot after its
applicable publication checks. This prepared prerelease snapshot uses commit
`b6ae33639d151e9b47bf0a1248f0be5309a72504`; preparation is not a new review verdict. Earlier
internal Git ancestors are not part of the public import because their author
metadata and historical lab reports contain personal or private-lab identity.
They remain owner-retained migration history, not distributable provenance.
The public asset manifest binds the path and SHA-256 of every redistributed
curated protocol/evidence file in the selected tree.

Retained historical records use explicit redaction labels. Names such as
`historical-user`, `HISTORICAL-LAB-HOST`, `third-party-config`, and addresses
from the documentation ranges in RFC 5737 preserve equality and topology only;
they are not actual accounts, hosts, products, routable endpoints, or runnable
paths. Commands in current guidance use environment variables or neutral
examples instead of those historical labels.

This policy does not rewrite history or publish a release. Repository URL,
destination and tag remain pending selection. OSS-08 owns the broader future
GitHub/GHCR release train; OSS-09 owns downstream cutover. Their completion is
not a mandatory prerequisite for this MVP snapshot. Preparation does not claim
stable-release or live-native qualification. The exported release workflow
retains manual builds with external publication steps disabled until a
destination is selected and publication is authorized.

## Contacts

- General support and bugs: use the repository's public Issues or Discussions.
- Vulnerabilities: use the repository's private vulnerability-reporting flow
  under Security/Advisories. Do not disclose credentials or exploit details in
  a public issue.

No personal email, private endpoint or credential is a project contact.

## Fail-closed gates

Publication stops on any unresolved credential, privacy, customer-data,
private-endpoint, provenance or non-redistributable-asset finding. It also runs:

```sh
python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations
```

The published OSS-07-I2 control must return `46/14/5/D14`, and all 23 hostile
mutations must fail with their reviewed classes. The failed OSS-07-I1 payload
is not available, is not a publication input, and must never be restored,
copied or reconstructed.

The machine-readable authority is
[`config/publication-policy.json`](../config/publication-policy.json).
