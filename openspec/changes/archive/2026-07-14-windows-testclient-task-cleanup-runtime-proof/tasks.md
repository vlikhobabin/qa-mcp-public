## 1. Production cleanup wiring

- [x] 1.1 Add behavioral tests for explicit cleanup success, failure and deferred retry.
- [x] 1.2 Add a production call-site contract test that turns red if explicit or deferred cleanup wiring is removed.
- [x] 1.3 Route the Windows launch implementation through the injectable exact-task cleanup guard.
- [x] 1.4 Keep solo registration disabled when registry URL is absent while preserving the enabled-registration bridge-token default.

## 2. Windows-native retained proof

- [x] 2.1 Add an opt-in Windows scheduled-task integration test with randomized exact ownership and bounded cleanup.
- [x] 2.2 Prove canceled-parent cleanup removes the exact registered task without wildcard cleanup.
- [x] 2.3 Prove injected explicit cleanup failure blocks success while deferred fallback removes the exact task.

## 3. Source-bound runtime evidence

- [x] 3.1 Build the current Windows host-agent bundle and test executable and bind both to the current Go source fingerprint.
- [x] 3.2 Stage the source-bound artifact and retain a normal product launch with exact-PID window and 62-second stability plus the Windows integration log.
- [x] 3.3 Run exact owned-file/task/PID cleanup and the T4 post-cleanup immutable-baseline comparison, then retain the evidence index.

## 4. Verification and lifecycle

- [x] 4.1 Run focused/full Python, native Go, Windows cross-build, release artifact, Ruff, shell, strict OpenSpec and diff gates.
- [x] 4.2 Sync the security capability, archive the rescue change and update all three QA delivery cards plus the combined manifest.
