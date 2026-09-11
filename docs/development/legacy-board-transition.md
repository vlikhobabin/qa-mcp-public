# Legacy board transition

Reconciliation date: 2026-09-05. Publication baseline is upstream commit
`8e94a21`, after the 21 commits missing from the original local checkout.
`.changerail/legacy-lifecycle.json` freezes all 1419 published lifecycle files
byte-for-byte and records the 18 live board paths at this boundary. Doctor, FF
and handoff reject new, modified, deleted or symlinked lifecycle files.

## Retained local work and published authority

The operator authorized preserving unfinished work, reconciling Git, publishing
the migration and then inventorying the board. Before synchronization, all
preexisting changes were committed locally on
`archive/pre-migration-work-20260905`:

- `350fddb`: 74 product, test, board and historical artifact paths. This is a
  preservation checkpoint, not acceptance, native certification or delivery.
- `faecfc2`: the original 78-path workflow migration and its original snapshot.

These commits are retained locally and are not ancestors of the published
migration. Do not merge the historical product implementation into main: the
later published I16 decision keeps `open_external_processor` omitted, and
upstream contains subsequent safety, privacy and evidence corrections.

Of the original 33 untracked lifecycle files, six S7 files already exist
byte-identically in upstream. The other 27 files belong to the superseded
local OSS-06/I1/S2/S5 work and remain in the local preservation checkpoint.
Their exact paths and the original manifest digest are recorded in the
reconciliation entry. No local file was discarded.

Upstream adds 125 lifecycle files and updates 46 paths relative to the original
snapshot, including public-source redactions. The reconciled inventory uses
those published bytes without rewriting any lifecycle artifact. It has no
dependency on ignored or untracked files, the local archive branch, or another
checkout. This explicit ownership reconciliation is a one-time migration
boundary, not permission to regenerate the snapshot to bypass future gates.

## Unfinished published change mapping

| Legacy change | Owning card | Transition rule |
| --- | --- | --- |
| `propagate-qa-mcp-target-session-operation-identity` | `oss-04d-propagate-target-session-operation-identity` in todo | Reconcile the old umbrella against published bounded successors before accepting any remaining work. |
| `admit-hidden-direct-execute-public-route` | `oss-06-s7-admit-hidden-direct-execute-public-route` in todo | Remains incomplete; I16 omission does not grant qualification or retry authority. |
| `certify-published-i11-observation-lifecycle-evidence` | `oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence` in progress | Preserve failed admission/topology evidence and I14/I15/I16 decisions; no automatic runtime retry. |

The archived local `extract-hidden-prompt-admission-action` plan remains
available in `350fddb`; the published S5 card and S5-R1 successor determine the
current state. Earlier checked tasks and archived artifacts are claims to
compare with retained evidence, not automatic completion proof.

## Board inventory and admission

The synchronized board has three backlog, eleven todo and four in-progress
cards. Directory status alone is not delivery truth: exhausted originals,
superseded umbrellas and completed successors coexist. Inventory Result/Next,
dependencies, review records and published commits before moving any card.
Keep completed and canceled history unchanged.

To accept actual remaining work, transfer its behavior, dependencies and
verification into one or more bounded board plans. Use direct canonical-spec
updates and local handoff. Preserve runtime authority and explicit non-goals.
Old 500-line or larger exceptions do not automatically pass the current
300-line admission; select coherent boundaries before acceptance.

Historical cards are generally exempt only from the static new-card template
inventory test, not from admission, clean-start, dependency or single-active
checks. The narrow CHRL-FIX-01 correction additionally distinguishes exactly four
unchanged in-progress sources from actual activity: S1, S5 and OSS-07 are
`superseded-no-go`, while I13 remains `suspended-not-verifiable`. The fixed
path/hash/disposition table in `scripts/changerail/local_delivery.py` is checked
on each decision, including all original file/ancestor identities. Drift blocks
the workflow; new or similarly named cards receive no exemption.

These four sources are non-deliverable through admission, FF/resume,
start/recovery, review, handoff and publish. Their locations, bytes and statuses
remain unchanged; only their outbound references cease to be live-maintained.
Ordinary live links and literal done dependencies remain checked, and original
edits/deletions remain fingerprint-visible. This does not qualify I13, replace
it with I16, reset exhausted reviews or exempt any other legacy todo record.
Preservation commits and board reconciliation do not turn old work into
recovery of the new runner. The migration pilot still requires separate prior
agreement on its exact card and command.
