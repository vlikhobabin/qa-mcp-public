## 1. RED And Ownership Ordering

- [x] 1.1 Add RED oracles for cancellation during publication, after full
  response publication and immediately after controller duplication.
- [x] 1.2 Add RED oracles for terminate failure, `WAIT_TIMEOUT`, unexpected
  wait status and continued cleanup while preserving an unrelated process.

## 2. Bounded Replacement

- [x] 2.1 Publish only the worker-local job handle and remove worker access to
  the controller.
- [x] 2.2 Authenticate response identity, duplicate from the exact worker and
  record controller ownership before membership/cancellation admission work.
- [x] 2.3 Join terminate/wait failures, wait exact worker/listener convergence
  and remove both final and temporary response paths.
- [x] 2.4 Keep the lifecycle dormant and production additions at `297/300`;
  preserve the published shared TCP parser byte-for-byte and isolate strict
  uniqueness inside the lifecycle.

## 3. Verification

- [x] 3.1 Run ambient focused/full Go, vet and both Windows cross-builds.
- [x] 3.2 Reconstruct published `HEAD` plus the exact eight S2 paths and rerun
  focused/full/vet/build gates.
- [x] 3.3 Run deterministic clean candidate `e033a702...` on trusted
  `HISTORICAL-LAB-HOST\\historical-user`; retain sanitized verdict and cleanup evidence.
- [x] 3.4 Confirm exact tasks/stages/processes are removed, listener `18081` is
  preserved and Docker/reboot/unrelated processes are untouched.
- [x] 3.5 Retain and execute the literal module-aware clean composition twice;
  confirm stable test/host hashes `e033a702...` and `08c44636...`.

## 4. Delivery Handoff

- [x] 4.1 Sync the modified capability and archive this replacement change.
- [x] 4.2 Run strict all-spec, manifest scope and diff gates, retain the final
  verification handoff and prepare deterministic review preflight for one fresh
  ordinary/high independent review.
