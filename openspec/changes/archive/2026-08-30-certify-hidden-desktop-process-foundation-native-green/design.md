## Context

S1 ended after three independent `NO-GO` cycles and exhausted its `2/2`
same-card rescue budget. The final reviewed production/test source is bounded,
dormant and hash-bound, and its code implements terminate-failure dual-handle
cleanup. The remaining blocker is narrower: the Windows-only regression test
was RED-executed and GREEN-compiled, but the exact-source native GREEN regex
selected only ProcessContract and NativeLifecycle.

No protocol capture, frame range or replay is involved. The proof source is the
exact Go test binary composed from published HEAD plus the four adopted S1
files. Dynamic run, desktop and token values remain opaque; raw environment or
UI content is not retained.

## Goals / Non-Goals

**Goals:**

- Preserve the exhausted S1 verdict/history as immutable lineage.
- Adopt the exact four S1 source/test files without production behavior change.
- Execute all three named Windows tests from one literal hash-bound command.
- Retain truthful sanitized native result and exact-owned cleanup evidence.
- Publish only after a fresh replacement-card `GO`.

**Non-Goals:**

- No third S1 same-card rescue or rewrite of its review history.
- No S2 worker/job/TPort lifecycle or use of the combined retained successor.
- No TestClient, 1C, protocol, public route, wire, authority or stable-profile
  admission.
- No global input, cursor, foreground, desktop switch or user-visible UI.
- No Docker mutation, reboot or unrelated Windows process cleanup.

## Decisions

### Adopt exact source lineage instead of modifying it again

The replacement takes the four files whose hashes are recorded in the S1 final
verification and introduces no production/test edit. This keeps the new review
about the missing proof, avoids an unauthorized third S1 repair and preserves
the `248/300` production ceiling. Reimplementing or broad restoration of the
retained combined OSS-06 payload is rejected because it would expand scope and
invalidate the accepted S1 code findings.

### Select all required tests literally

The native selector is exactly:

`^TestHiddenDesktopProcessFoundation(ProcessContract|CleanupClosesHandlesWhenTerminateFails|NativeLifecycle)$`

This executes the creation/inheritance/transient-close contract, the separate
terminate-failure dual-close contract and the real named-desktop lifecycle.
Cross-build success alone is not treated as GREEN execution.

### Build from published baseline plus four adopted files

The candidate is composed in an isolated temporary directory from
`git archive HEAD:host-agent/windows-display-agent` plus only the four exact S1
files. The candidate and source SHA-256 values are recorded before transfer and
rechecked on Windows. Other dirty OSS-06/I1/S2-S7 files are excluded.

### Keep Windows execution exact-owned and input-free

One unique stage and one one-shot interactive ScheduledTask execute the test
binary on `HISTORICAL-LAB-HOST\\historical-user`. Before deletion, task action, arguments,
path, process ownership and candidate hash must match the current run. Cleanup
removes only that task/stage after the executable is absent; listener `18081`,
Docker inventory, unrelated processes and Defender configuration are observed
but not mutated. No raw output, environment values, screenshots or UI text are
retained.

## Risks / Trade-offs

- [Evidence again overstates the selector] -> Bind every oracle flag and index
  summary to the literal three-test argv and retain the task result.
- [Ambient dirty files enter the candidate] -> Build from published archive plus
  an explicit four-file copy and compare source/candidate hashes.
- [Cleanup deletes foreign state] -> Validate exact task action/args, stage,
  executable hash and zero owned processes before removal.
- [Replacement silently becomes S2] -> Manifest admits no worker, TPort,
  TestClient, route, wire or existing host production file.

## Migration Plan

Create replacement artifacts, build and run the exact three-test candidate,
sync the explicit cleanup scenario and archive the replacement change. After a
fresh independent `GO`, publish the replacement scope and mark the exhausted S1
as superseded by this published card. Rollback removes the dormant four-file
foundation and its capability; no runtime rollback is required because it has
no production caller.

## Open Questions

- none
