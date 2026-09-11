# I14 S4 Early-Exit And Task-Topology Investigation

## Decision

I14 is complete as a bounded `NOT-VERIFIABLE` investigation decision. It does
not certify I13 and does not change product or test source. The exact candidate
and both operator-specified immutable EPFs were available and matched their
expected hashes, but the authorized contour stopped at Session-1 task
admission before I14 could accept a candidate result. No retry or substitute
host, identity, target, platform, fixture or argv was used.

## Exact Source And Inputs

All five current product/test blobs match the published I11 lineage, and those
paths have zero diff from `964e29f` and no working-tree change. The exact
candidate remained `9e32429f...`; run-1 and run-2 remained `ffd50b30...` and
`a9c35c02...`. Exact host, principal, Session-0 controller, platform, target,
interactive-session process presence, clean task/stage/process surface and
configuration content preflight passed. The retained decision omits the raw
operator authority, local paths and target identity.

## S4 Boundary

I13's immutable handoff remains the only admitted exact-row evidence: its
first tracked S4 candidate exited `1` before `native-observation.json`, with
output hash `e3dd3f47...` and zero 1C processes afterward. Static analysis of
the unchanged published test bounds that outcome before the positive
observation receipt but cannot identify the fatal callsite from the retained
hash alone.

I14 staged the exact candidate and exact EPFs, but the interactive scheduled-
task route did not emit even a constant Session-1 canary within its bounded
`180`-second window. The exact task was removed, the repeated cleanup removed
nothing and all process counts remained zero. Because the candidate invocation
count cannot be proven from an admitted typed receipt, I14 records a `contour`
classification and `NOT-VERIFIABLE`; it does not infer a published-behavior
root cause or spend another live attempt.

## Task-Topology Attribution

The unrelated-task set currently contains `291` hashed identities and exactly
matches I13's original before hash `25ed8ce8...`, not its transient after hash
`113c7390...`. Creating the exact I14 task left the protected set at the same
hash and count, and cleanup returned to the identical hash and count. No
foreign task was selected. This rules out deterministic inclusion of the
owned task and provides no ownership-violation evidence. It does not exercise
the historical started route, and scheduler operational history was disabled.
Historical harness/start behavior and external drift therefore remain
observationally indistinguishable: topology is `not_verifiable`, and the
retained decision infers no cause.

## Cleanup And Successor

Configuration content stayed at `90fb293e...`; ACL, creation, last-write and
attributes were exact, and last-access restoration was the final configuration
operation. Because the initial preflight did not retain a comparable
last-access value, continuity from that initial state is not verifiable. Exact
I14 task and process counts and all 1C process counts are zero. The exact stage
cleanup removed one stage on its first pass and nothing on its second; the
stage is absent. With no admitted candidate receipt, job/desktop/transport
zero-state is not verifiable and is not claimed. No raw UI, output, task names,
screenshots, credentials or connection strings were retained.

I13 remains active, unarchived and uncertified. The proposed I15 backlog card
may retry one exact S4 isolation only after an operator separately confirms
that Session-1 task admission is restored; it carries no current execution
authority.
