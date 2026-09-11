# Session-1 Last-Access Restoration Authority Investigation

## Decision

The exact limited session-1 token can snapshot, read, restore
`LastAccessTimeUtc`, and write a receipt for its own disposable file. The
retained run used the same session owner and child worker in session 0 and
session 1; both owner/worker chains restored the disposable baseline exactly.
This safely rules out a generic
`InteractiveToken`/`Limited` inability on exact-owned temp files.

It does not prove or grant authority over the protected real target. The
least-authority successor design assigns the real target's first snapshot and
sole final metadata restoration to the session-0 outer broker. Session 1 may
consume exact-owned staged inputs and privacy-safe expected hashes only; it
must not open, read, write, or restore the real 1C configuration. Replacing
that ownership requires a separate reviewed authority change.

This decision is non-admitting. It does not authorize another S4-R1 live row,
start 1C, derive a marker, or advance S3, S4, S5, or S7.

## Classification

The earlier missing session-1 receipt is classified as
`target_specific_or_unobserved_pre_receipt`, not as a reproduced generic token
or disposable-file authority failure. The forbidden real target was not
opened or read, so this investigation cannot safely distinguish a
target-specific ACL/metadata condition from an earlier wrapper/transport exit.

The new privacy-safe boundary is fail-closed:

| Exit | Typed status | Retained meaning |
| ---: | --- | --- |
| `51` | `task_token_mismatch` | Expected session/principal did not match before probe access. |
| `52` | `snapshot_read_failure` | The first snapshot or protected read did not complete. |
| `53` | `metadata_set_authority_failure` | Final metadata restoration could not be trusted. |
| `54` | `evidence_write_failure` | No receipt could be written; the outer task result supplies the type. |

The `53` hostile row is explicitly a classifier test: it returns the fail-closed
type after successfully restoring its disposable probe. It is not evidence of
an observed Windows authority denial. The actual session-1 pass is the
authority observation for the exact-owned disposable boundary.

## Dynamic proof

Retained evidence index:
`.runtime/changerail/evidence/oss-06-s4-r1-i1-investigate-session1-last-access-restoration-authority/index.json`.

- Local structural proof: worker SHA-256
  `d7bcbe925fa7ce06cb90c9eb7b24e34a438808e723868f111b0ccd467369d8f7`;
  session-owner SHA-256
  `dd762721cb62d2bc701aa0e77696d1f9a7eeb5b8c8dec5d393b6a4072a9f5e5e`.
  Every invoked probe reader snapshots access time as its first operation,
  keeps reads inside its protected region, restores through `finally` as its
  sole final probe operation, and performs no later probe read. The outer
  runner initializes exact-owned probes without reading them and only deletes
  them during final exact-stage cleanup.
- Windows AST parse: `0` syntax errors across the exact worker, session owner,
  and runner.
- Session 0: `passed`, exit `0`, expected session, owner and child snapshots,
  child read/restoration, owner observation of child restoration, and final
  owner restoration all exact.
- Session 1: `passed`, exit `0`, receipt present, expected session/principal,
  owner and child snapshots, child read/restoration, owner observation of child
  restoration, and final owner restoration all exact.
- Typed rows: token `51`, snapshot/read `52`, metadata-set classifier `53`, and
  absent-receipt evidence-write `54` all mapped exactly.
- Cleanup: exact task count `0`, exact stage absent, exact stage-process count
  `0`, unrelated task set and boot identity unchanged.
- Forbidden surfaces: 1C process count `0` before and after; live runner false;
  S3/S4/S5 row counts `0`; S7 false; action count `0`; real-configuration
  access false.
- Privacy: no raw path, raw error, credential, UI data, screenshot, or raw
  configuration content was retained.

The first identical disposable attempt completed its remote command but its
local evidence recorder rejected a non-UTF-8 Windows diagnostic stream. An
immediate console-only cleanup observation was not retained and does not
support acceptance. The retained `remote-preflight-v2` established the clean
precondition for the next recorded run; the current decision is supported by
the corrected `rescue1-disposable-session-matrix` plus
`rescue1-remote-postflight`. The two recorder artifacts that lacked valid
structured evidence were removed from the canonical index; the superseded
worker-only proof and earlier matrix remain diagnostic history, not mandatory
evidence.

## Preserved lineage

The pre-investigation protected aggregate hashes are:

- blocked S4-R1 payload:
  `489c04d715440b15b7103aaaa394b8ebef11d4aafc93fe39da5e676e5274dbb6`;
- S7 payload:
  `cdf9310ec84c760d8bdf38c149062897950ee1bbb7292c5eb54d7d0c9c05c5b3`;
- fixtures:
  `e64b0caadfacf267a826d28caf733b31f6f3c1f2f757e8fb95ea97f28a08cc9c`;
- OSS-07:
  `73fc1f57689a9585566b4772039cb4eaaa4793166d438c28d6fc99c8bec471af`;
- OSS-08:
  `83d434b489650268b29be339859822cc6d22f815bbc4c8db9fd174b449ba472f`;
- parent delivery manifest:
  `ad30f653ebb339aa06d88e3591a4ebdfaf1b87e6fc98bfffa19df919d2c1f0d7`;
- empty staged diff:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

The four immutable S4-R2 values remain:

- platform:
  `ca26ada2c7baaf97516c59ba10a2a4d30d7c509da062a8d09ad2b5a9528f8bac`;
- candidate:
  `04e15c3abb8bae32590f9c55aa47fdfd1ccb263b797d438b9e1c61421afb20e9`;
- run 1:
  `ffd50b306cee13404e3be08d7c4f19e8529e78d86eb9ccf19f0aeb76b3ef5573`;
- run 2:
  `a9c35c020419b53dcb1e97c354dbce8c40919b902f9186f280296f87d5134b5a`.

Post-delivery verification must reproduce every protected aggregate and the
empty staged state before independent review.
