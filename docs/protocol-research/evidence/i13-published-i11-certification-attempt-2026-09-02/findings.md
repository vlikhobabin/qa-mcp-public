# I13 Published-I11 Certification Attempt

## Outcome

I13 is `NOT-VERIFIABLE` and is not eligible for archive, review or publish.
The exact-source preflight passed, and the S3 control passed with zero action,
but the first tracked S4 row exited nonzero before producing an observation
receipt. The fail-closed runner did not start the remaining four rows.

The attempt retained only hashes, counts, bounded outcomes and cleanup
booleans. It retained no raw UI text, screenshots, credentials, connection
strings or broad process/window dumps.

## Exact Source And Preflight

- The clean workspace remained at `70d66b8`; all five bound blobs matched the
  published I11 lineage and had no path diff from `964e29f`.
- Two deterministic amd64 candidate builds were byte-identical at
  `9e32429f...`.
- Platform `8.3.27.2214`, its `ca26ada2...` hash, both exact EPF hashes, target
  presence, interactive-session availability and an initially uncontended
  execution surface passed.
- Configuration content, ACL, creation, last-write, last-access and attribute
  before-images were retained as privacy-safe hashes in `decision.json`.

## Row Evidence

The S3 control passed in `17,178 ms`, produced action count `0`, and completed
its internal exact-owned cleanup. Configuration restoration passed, the first
outer cleanup removed only the exact task, and the second cleanup removed
nothing.

The first tracked S4 row used exact candidate, platform, target, run-1 fixture,
marker and credential-absence inputs bound by argv hash `00e676e5...`. The
candidate exited `1` after `1,932 ms`; no observation or pre-receipt diagnostic
was produced, no later row started, and the immediate post-failure 1C process
count was zero. Because no observation receipt exists, I13 does not infer a
marker, topology or action result from this failed row.

## Cleanup And Investigation Stop

After the failed row, configuration content, ACL and all retained metadata
matched the exact before-image. Exact I13 tasks and 1C processes are zero, the
exact remote stage is absent, and repeated row/stage cleanup removed nothing.
No unrelated task or process was targeted.

The protected unrelated-task-set fingerprint nevertheless changed from
`25ed8ce8...` to `113c7390...` during the attempt. Its cause is not inferred,
and I13 does not repair or suppress it. The combination of the early S4 exit
and task-topology drift requires the linked I14 investigation before any new
certification attempt.
